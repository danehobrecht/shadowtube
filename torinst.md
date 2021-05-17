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

2. Append the hashed password to your `torrc` file preceded by `HashedControlPassword`
```
sudo vi /etc/tor/torrc
HashedControlPassword 16:43EAB78403DE31976030CFEC0BDE888EA9D5BAC62F9284A446383ACC1C
```
---
#### Using Cookie Authentication
1. From your `torrc`, uncommment the line `CookieAuthentication 1`
---
### Additional Security Steps
To prevent unauthorized users from accessing `tor` considering adding the following steps below
- Consider changing your SOCKS5 and Tor Control Ports to a port not commonly used
- **Important for users using Cookie Authentication**: Append the following lines to your `torrc`
```
SocksPolicy accept 127.0.0.1
SocksPolicy reject *
```
This step limits connection only to the local loopback address, effectivly limiting to connections originating from the local machine
- As always, [RTFM](https://tor.void.gr/docs/tor-manual.html.en "RTFM")
