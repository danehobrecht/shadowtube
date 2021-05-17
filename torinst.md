# Setting up Tor
#### Initial Steps
1. Open your `torrc` file and uncomment the line `ControlPort`. Change the control port now if you wish
2. Pick one of the 2 options below to authenticate with Tor
---
#### Using a Hashed Control Password
1. run `tor --hash-password <password>`

```
tor --hash-password <password>
16:43EAB78403DE31976030CFEC0BDE888EA9D5BAC62F9284A446383ACC1C
```

2. Append the hashed password to `HashedControlPassword` in `torrc`
```
sudo nano /etc/tor/torrc
HashedControlPassword 16:43EAB78403DE31976030CFEC0BDE888EA9D5BAC62F9284A446383ACC1C
```
---
#### Using Cookie Authentication
```
sudo nano /etc/tor/torrc
```
Uncommment `CookieAuthentication 1`  in `torrc`
---
### Additional Security Steps
To prevent unauthorized users from accessing `tor`, consider adding the following steps:
- Change your SOCKS5 and control ports to a port not commonly used
- **Important for users using cookie authentication**: Append the following lines to your `torrc`
```
SocksPolicy accept 127.0.0.1
SocksPolicy reject *
```
This step limits connection only to the local loopback address, effectivly limiting to connections originating from the local machine
- As always, [RTFM](https://tor.void.gr/docs/tor-manual.html.en "RTFM")
