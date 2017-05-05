# cs378-cookie-server
Flask server which receives stolen cookies and adds them to Chrome. Made for CS378 Ethical Hacking group final project.

To run the server, make sure Flask is installed and run
```
python3 server.py <path to Chrome cookie db>
```
## API
```
POST /cookie_jar
url - the url to store the cookie at
name - the name of the cookie
value - the value of the cookie
```
When a valid cookie is received, it will be added to Chrome's cookie database, and
Chrome will open at the target url.

```
POST /store_cookie
url - the url to store for redirection
```
When a valid URL is stored, the `/redirect` endpoint will redirect there.
