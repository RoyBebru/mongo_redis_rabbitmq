#!/bin/sh

sudo docker run --name redis-cache -p 6379:6379 -d redis

# start with persistent storage
#docker run --name some-redis -d redis redis-server --save 60 1 --loglevel warning

