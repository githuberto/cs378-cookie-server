#!/bin/bash

# example POST request to the local server
# adds the cookie (COOKIE, 12345) to google.com
curl --data "url=github.com&cookie_name=COOKIE&cookie_value=12346" 127.0.0.1:5000/cookie_jar
