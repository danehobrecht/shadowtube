# ShadowTube - Bash

Bash version of ShadowTube.

1. [Setup Tor](https://github.com/danehobrecht/shadowtube-bash/blob/main/torinst.md)

2. Install dependencies

`pip3 install -r requirements.txt`

3. Launch an instance of Tor

4. Run

`python3 main.py`
## Configuring torrc
1. Run `tor --hash-password <password>`
2. Open `torrc` with your favorite text editor `sudo nano /etc/tor/torrc`
4. Append the hashed password to `HashedControlPassword`
5. Uncomment `ControlPort`
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

For more information, refer to https://github.com/danehobrecht/shadowtube/blob/main/README.md
