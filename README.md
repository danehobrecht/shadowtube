# ShadowTube
Analyzation options/features:
- Video URLs
- Comment URLs
- Web UI (under construction)
- Complete comment histories (under construction)
## Installation
### Arch
`yay -S shadowtube`
### Other (UNIX)
1. Install prerequisites:
 - [Python 3.7.3+ & pip](https://www.python.org/downloads/)
 - [Tor Browser](https://www.torproject.org/)
2. Clone the repository and navigate to the directory:
```
git clone https://github.com/danehobrecht/shadowtube.git && cd shadowtube
```
3. Create virtual environment:
```
python -m venv venv && source /venv/bin/activate
```
4. Install dependencies:
```
pip install -r requirements.txt
```
5. [Configure torrc](#configure-torrc) (optional)
6. Launch an instance of Tor Browser
7. Execute:
```
python shadowtube
```
## Configure torrc
1. Hash a custom control password:
```
tor --hash-password <password>
```
2. Open `torrc` with elevated privelages:
```
nano /etc/tor/torrc
```
3. Append the hashed password to `HashedControlPassword` and uncomment `ControlPort`:
```
...
## The port on which Tor will listen for local connections from Tor
## controller applications, as documented in control-spec.txt.
ControlPort 9151
## If you enable the controlport, be sure to enable one of these
## authentication methods, to prevent attackers from accessing it.
HashedControlPassword 16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C
#CookieAuthentication 1
...
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
- [More information](https://2019.www.torproject.org/docs/documentation.html.en#UpToSpeed)
## Sample outputs
```
Title: "Portal - 'Still Alive'"
Video URL: https://www.youtube.com/watch?v=Y6ljFaKRTrI
Interrupt (CTRL+C) to conclude the session

[ X ] [ 1 / 8 ] [ N/A ]
[ ✓ ] [ 2 / 8 ] [ United States — 162.247.74.27 ] 
[ X ] [ 3 / 8 ] [ N/A ]
[ X ] [ 4 / 8 ] [ Germany — 84.252.122.55 ]
[ ✓ ] [ 5 / 8 ] [ Luxembourg — 104.244.74.159 ]
[ ✓ ] [ 6 / 8 ] [ Iceland — 89.147.109.233 ]
[ X ] [ 7 / 8 ] [ United States — 199.249.230.145 ]
 ╰──⚠ Throttling
[ ✓ ] [ 8 / 8 ] [ Austria — 109.70.100.6 ]

Status: Questionable
```
```
Title: "Me at the zoo"
Comment URL: https://www.youtube.com/watch?v=jNQXAC9IVRw&lc=UgzuC3zzpRZkjc5Qzsd4AaABAg
Interrupt (CTRL+C) to conclude the session

[ ✓ ] [ 1 / 8 ] [ N/A ]
[ ✓ ] [ 2 / 8 ] [ United States — 162.247.74.27 ] 
[ ✓ ] [ 3 / 8 ] [ N/A ]
[ ✓ ] [ 4 / 8 ] [ Germany — 84.252.122.55 ]
[ ✓ ] [ 5 / 8 ] [ Luxembourg — 104.244.74.159 ]
[ ✓ ] [ 6 / 8 ] [ Iceland — 89.147.109.233 ]
[ ✓ ] [ 7 / 8 ] [ United States — 199.249.230.145 ]
[ ✓ ] [ 8 / 8 ] [ Austria — 109.70.100.6 ]

Status: Healthy
```
## Known compatability issues (subject to change)
- Video premieres
- Live streams
- "Discussion", or, "Community" posts
- Geometric unicode characters in titles