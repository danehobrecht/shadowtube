# Setting up Tor
1. run `tor --hash-password <your password>`

```bash
tor --hash-password whoisHauteknits?
16:43EAB78403DE31976030CFEC0BDE888EA9D5BAC62F9284A446383ACC1C
```

2. Append the hashed password to your `torrc` file preceded by `HashedControlPassword`
```bash
sudo vi /etc/tor/torrc
HashedControlPassword 16:43EAB78403DE31976030CFEC0BDE888EA9D5BAC62F9284A446383ACC1C
```

