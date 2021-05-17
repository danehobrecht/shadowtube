# ShadowTube
Bash version of ShadowTube.
1. [Setup Tor](https://github.com/danehobrecht/shadowtube-bash/blob/main/torinst.md)
2. Install dependencies
```
pip3 install -r requirements.txt
```
4. Launch an instance of Tor
5. Run
```
python3 main.py
```
## Configuring torrc
1. Hash a custom control password
```
tor --hash-password <password>
```
3. Open `torrc` with elevated privelages
```
sudo nano /etc/tor/torrc
```
4. Append the hashed password to line 59
```
HashedControlPassword <hash>
```
6. Uncomment line 60
```
ControlPort <port>
```
---
**Alternatively:** Uncomment line 59
---
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
