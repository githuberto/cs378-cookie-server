#!/bin/bash

# example POST request for storing XSS urls
if [ $# -ne 1 ]; then
    (>&2 echo "Usage: ./$(basename $0) url")
    exit 1
fi

curl --data "url=${1}" 127.0.0.1:5000/store_url
