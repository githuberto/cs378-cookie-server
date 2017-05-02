#!/bin/bash
# example POST request script for sending to the local server

if [ $# -ne 3 ]; then
    (>&2 echo "Usage: ./$(basename $0) url cookie_name cookie_value")
    exit 1
fi

curl --data "url=${1}&cookie_name=${2}&cookie_value=${3}" 127.0.0.1:5000/cookie_jar
