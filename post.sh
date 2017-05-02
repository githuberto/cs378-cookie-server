#!/bin/bash
# example POST request to the local server
# adds the cookie (COOKIE, 12345) to github
curl --data "url=github.com&cookie_name=COOKIE&cookie_value=12345" 127.0.0.1:5000/cookie_jar
