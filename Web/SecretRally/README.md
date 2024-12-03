# Secret Rallies

## Analysis

The problem provides us a website that contains a login page requiring a username and a password. It also provides us the source code for the project, which is an ASP.NET application written in C#. The problem states that we are looking for the location of the "Secret Rally". The flag follows the format `cybersci{...}`.

## Solution

By analizing the code we first notice the presence of a middleware [`AgentChecker.cs`](Source/src/SecretRally/SecretRally/Middleware/AgentChecker.cs), which enforces that every request be sent with the header of `User-Agent` set to one of the valid values. From now on, assume that every request sent to the server includes the header `User-Agent: Chrome/`.

Since we can only see a login page, a reasonable location to explore in the code is the [`Auth`](Source/src/SecretRally/SecretRally/Auth/) folder. While the JWT handling section in the [`JwtAuthHandler.cs`](Source/src/SecretRally/SecretRally/Auth/JwtAuthHandler.cs) file seems fine, we may notice that the method `readJWTToken` is being used to read the contents of the JWT. According to the [documentation](https://learn.microsoft.com/en-us/dotnet/api/system.identitymodel.tokens.jwt.jwtsecuritytokenhandler.readjwttoken), this method does not validate the token, meaning that any signature is ignored. This means that we can forge a JWT with any signature and that will be considered valid by the system. Still in this context, we will notice that the code looks for the value under the claim with type `ClaimTypes.NameIdentifier`, which means that the claim key should be `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier`. Therefore, to login into the system, we need a JWT with that claim key whose value is the username we want to login as.

By looking at the [`Program.cs`](Source/src/SecretRally/SecretRally/Program.cs) file, we will find some initialization code, including a portion that adds a username with the format `username = "admin" + new Random().Next(1000, 2000)` and `password = RandomNumberGenerator.GetHexString(32)`. While a password with 32 bytes in hex is a bit much to brute-force, a number in the range 1000 to 2000 is well within range of a brute-force. Since we know how to craft JWT for given usernames, we can perform the brute-force with a username `admin` followed by a number between 1000 and 2000 until we successfully log into the system.

Once logged in, we are presented with a page called _Dashboard_ that contains a list of rallies, but none of them contain the flag we are looking for. By analyzing the [`Models/Rally.cs`](Source/src/SecretRally/SecretRally/Models/Rally.cs) file, we will see that a rally may or may not be hidden, leading us to believe that only the non-hidden rallies are actually being displayed in the dashboard. This is confirmed by looking at [`Pages/Dashboard.cshtml`](Source/src/SecretRally/SecretRally/Pages/Dashboard.cshtml), which contains the following [LINQ](https://learn.microsoft.com/en-us/dotnet/csharp/linq/) query: `@foreach (var rally in Model.Rallies.Where(r => !r.Hidden))`. 

The dashboard also contain a form for adding attendees to any of the rallies, which is handled in the file [`Pages/Dashboard.cshtml.cs`](Source/src/SecretRally/SecretRally/Pages/Dashboard.cshtml.cs). Analyzing this file we will notice that the inclusion of the attendee is performed using the `ExecuteSqlRawAsync` with its parameters being appended to the code string, which opens up the opportunity for a SQL Injection. While the attendee name is filtered for valid characters and the rally ID must be sent as a number, the entrance code gets no such restrictions, giving us a parameter to perform our injection.

While we may be led to send the entrance code as an empty string, we must notice that the entrance code must be present in the database ahead of time, leading us to two options: performing the injection directly on the browser (since the entrance code will be loaded on page load), or parsing the HTML for the entrance code and sending it with the injection request. Given that there are other mechanisms for stopping CSRF provided by ASP.NET, complicating the code to perform the injection, it is recommended that the first option be taken. The code provided with this writeup uses the second option.

With a SQL injection entrypoint identified, we can perform the injection with the following:

```SQL
[ENTRANCE_CODE] + ', 1); UPDATE "Rallies" SET "Hidden"=false; -- -
```
Note that the syntax is specific to PostgreSQL, which is why the quotes around the table name and columns are required.

This will cause all of the rallies in the database to be considered non-hidden and, therefore, to be shown on the main dashboard. One of the rallies will have its location as `cybersci{th1s_1s_n0t_th3_0r1g1n4l_fl4g}`, which is this problem's flag.

In the provided code, there's a portion to extract the flag from the page after the injection is run and to revert the injection, setting the rally back to hidden. This is done in case the server is shared, so that we do not spoil the problem for other users.