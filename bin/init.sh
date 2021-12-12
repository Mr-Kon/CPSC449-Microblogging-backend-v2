#!/bin/sh

rm -f ./var/users.db ./var/posts.db

sqlite3 ./var/users.db < ./share/users.sql
sqlite3 ./var/posts.db < ./share/posts.sql

python3 ./RedisSetUp.py
python3 ./share/createPollsTable.py
