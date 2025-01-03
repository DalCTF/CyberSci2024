# Parts (CyberSci 2024 Web)

For the most part the encryption mechanism was secure, using a large e, n, p and q values made most attacks unfeasible. The only liability is the block size of four which can be reasonably brute forced, especially when considering the restricted charset of only `[A-Za-z0-9_-]`. I therefore built a [custom tool](rsa_bruteforce_tool.py) to bruteforce each block. This gave the flag `cybersci{no_need_to_worry}`.