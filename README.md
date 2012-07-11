CJDNS-URI
==========
Allows you to add CJDNS peers via a URI scheme:
`cjdns://ip:port/&password=password&key=publickey`
I know that it's a bit odd to have the /&, not a ?, but it's v0.1 so work with me

Install
---------
`sudo ./cjdns-uri.py install`

Setup
---------
make ~/.cjdnsadmin.ini look like this:

    [cjdns]
    importpath = <path to cjdns git>/contrib/python/
    adminpassword = <admin password>
    adminport = 11234

Test
--------
[Go here](https://www.thefinn93.com/cjdns/uritest/) to add me as a peer
