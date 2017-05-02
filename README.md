# cs378-cookie-server
Flask server which receives stolen cookies and adds them to Chrome. Made for CS378 Ethical Hacking group final project.

To run the server, make sure Flask is installed and run
```
python3 server.py <path to Chrome cookie db>
```

The server will listen for POST requests on the `/cookie_jar` endpoint of the form:
```
url - the url to store the cookie at
name - the name of the cookie
value - the value of the cookie (must be an integer)
```

When a valid cookie is received, it will be added to Chrome's cookie database, and
Chrome will open at the target url.
