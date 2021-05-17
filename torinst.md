# Configuring torrc
#### Initial Steps
1. Open your `torrc` file and uncomment the line `ControlPort`.
```
sudo nano /etc/tor/torrc
```
2. Pick one of the 2 options below to authenticate with Tor.
---
#### Hashed control password
1. Run `tor --hash-password <password>`
```
tor --hash-password sample_pass123
16:43EAB78403DE31976030CFEC0BDE888EA9D5BAC62F9284A446383ACC1C
```
2. Append the hashed password to `HashedControlPassword`
```
HashedControlPassword 16:43EAB78403DE31976030CFEC0BDE888EA9D5BAC62F9284A446383ACC1C
```
---
#### Cookie authentication
Uncommment `CookieAuthentication 1`
---
### Additional security steps
To prevent unauthorized users from accessing `tor`, consider adding the following steps:
- Change your SOCKS5 and control ports to a port not commonly used
- **Important for users using cookie authentication**: Append the following lines to `torrc`
```
SocksPolicy accept 127.0.0.1
SocksPolicy reject *
```
This step limits connection only to the local loopback address, effectively limiting to connections originating from the local machine.
- As always, [RTFM](https://tor.void.gr/docs/tor-manual.html.en "RTFM")
