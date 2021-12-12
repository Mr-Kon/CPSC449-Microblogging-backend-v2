#
# CPSC449-Proj2
# Users API 

#### Brian Fang (brian.fang@csu.fullerton.edu)
#### Nathan Tran (ntran402@csu.fullerton.edu)
#### Ashkon Yavarinia (ashkon@csu.fullerton.edu)
#### Edgar Cruz (ed.cruz76@csu.fullerton.edu)


import configparser
import logging.config
import os
import socket
from falcon import response

import hug
import requests
import sqlite_utils
from sqlite_utils import Database
import sqlite3

# Load configuration
#
config = configparser.ConfigParser()
config.read("./etc/api.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)


db = Database(sqlite3.connect("./var/users.db"))


@hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)


# Routes
#
# Creates a user with a username, email, bio and password
@hug.post("/users/", status=hug.falcon.HTTP_201)
def createUser(
    response,
    username: hug.types.text,
    email: hug.types.text,
    bio: hug.types.text,
    password: hug.types.text,
):
    users = db["users"]

    user = {
        "username": username,
        "email": email,
        "bio": bio,
        "password": password,
    }

    try:
        users.insert(user)
        user["id"] = users.last_pk
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

    response.set_header("Location", f"/users/{user['id']}")
    return user

# Finds a user in the db and returns the row 
@hug.get("/users/{username}")
def getUser(response, username:hug.types.text):
    users = []
    try:
        user = db.query("SELECT * FROM users WHERE username = ?", (username,))
        users.append(user)
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404
    return {"users": user}

#adds followers to a user in the join table
@hug.post("/users/following/", status=hug.falcon.HTTP_201)
def addFollowing(
    response, 
    users_id: hug.types.number, 
    following_id: hug.types.number,
):

    followers = db["following"]

    follower = {
        "users_id": users_id,
        "following_id": following_id
    }

    try:
        followers.insert(follower)
        follower["id"] = followers.last_pk
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

    return follower

#getfollowers returns a list of the id's the specified user is following
@hug.get("/users/following/{username}")
def getfollowings(response, username:hug.types.text):
    following = []
    try:
        follow = db["followingNames"].rows_where("username = ?", (username,))
        for i in follow:
            following.append(i["friendname"])
        
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404
    return {"following": following}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# project 3

#Registers this service with the registry service
@hug.startup()
def register(response):
    url = socket.getfqdn("localhost") +':'+ os.environ["PORT"]
    print(url)
    d = {'url':url,'service':'users'}
    r = requests.post(config['registry']['register'], data=d)
    print(r.status_code, r.url)

#Returns a 200 ok and alive status 
@hug.get("/users/health-check/")
def healthCheck(response):
    response.status = hug.falcon.HTTP_200
    return {"status": "alive"}