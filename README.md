# ShadowTube
Bash version of ShadowTube.
1. [Configure torrc](#configure-torrc)
2. Install dependencies
```
pip3 install -r requirements.txt
```
3. Launch an instance of Tor Browser
```
torbrowser-launcher
```
5. Run ShadowTube
```
python3 main.py
```
### Configure torrc
1. Hash a custom control password
```
tor --hash-password <password>
```
2. Open `torrc` with elevated privelages
```
sudo nano /etc/tor/torrc
```
3. Append the hashed password to line 59
```
HashedControlPassword <hash>
```
4. Uncomment line 60
```
ControlPort <port>
```
- Alternatively, uncomment line 59
```
CookieAuthentication 1
```
### Additional security steps
To prevent unauthorized users from accessing `tor`, consider adding the following steps:
- Change your SOCKS5 and control ports to a port not commonly used
- **Important for users using cookie authentication**: Append the following lines to `torrc`
```
SocksPolicy accept 127.0.0.1
SocksPolicy reject *
```
This step limits connection only to the local loopback address, effectively limiting connections originating from the local machine.
- As always, [RTFM](https://tor.void.gr/docs/tor-manual.html.en)
---
For more information, refer to https://github.com/danehobrecht/shadowtube/blob/main/README.md
