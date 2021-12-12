#
# CPSC449-Proj2
# Timeline API 

#### Brian Fang (brian.fang@csu.fullerton.edu)
#### Nathan Tran (ntran402@csu.fullerton.edu)
#### Ashkon Yavarinia (ashkon@csu.fullerton.edu)
#### Edgar Cruz (ed.cruz76@csu.fullerton.edu)

import configparser
import logging.config
import os
import socket

import hug
import sqlite_utils
import requests
import json

# Load configuration
#
config = configparser.ConfigParser()
config.read("./etc/api.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)


# Arguments to inject into route functions
#
@hug.directive()
def sqlite(section="postsdb", key="dbfile", **kwargs):
    dbfile = config[section][key]
    return sqlite_utils.Database(dbfile)

@hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)

# Authorization function
def auth(username, password):
	r = requests.get(config["users"]["url"]+username)
	temp = json.loads(r.text)
	user = temp["users"][0]
	if user["password"] == password:
		return user
	return False

# Routes

# Returns an array of posts of a given 'username'
@hug.get("/posts/timeline/user/{username}")
def user_timeline(
    response,
    username: hug.types.text,
    db: sqlite,
):
    try:
        timeline = db["posts"].rows_where("username = :username", {"username":username},order_by="timestamp desc")
    except Exception as e:
        response.status = hug.falcon.HTTP_404
        return {"error": str(e)}
    return timeline

# Returns an array of posts from a users following list
@hug.get("/posts/timeline/home/", requires=hug.authentication.basic(auth))
def home_timeline(
    response, 
    users_followed: hug.types.delimited_list(','),
    db: sqlite,
):
	timeline = []

	try:
		for followed in users_followed:
			temp = db["posts"].rows_where("username = :username", {"username":followed})
			timeline = timeline + list(temp)
    	#need to order all posts now that they've all been appended
		timeline.sort(key = lambda x:x["timestamp"], reverse=True)
	except Exception as e:
		response.status = hug.falcon.HTTP_404
		return {"error": str(e)}
	return timeline

# Returns an array of public posts
@hug.get("/posts/timeline/public")
def public_timeline(response, db: sqlite):
    timeline = []
    tweets = db["posts"] 
    for tweet in tweets.rows: 
        timeline.insert(0, tweet)

    return timeline

# Get all posts
@hug.get('/posts/')
def posts(db: sqlite):
    return {"tweets": db["posts"].rows}

# Get post by tweet id
@hug.get('/posts/{tweetId}')
def postsById(response, tweetId: hug.types.text, db: sqlite):
    try:
        return db["posts"].get(tweetId)
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404


# This route posts a tweet
@hug.post("/posts/", status=hug.falcon.HTTP_201, requires=hug.authentication.basic(auth))
def postTweet(
    response,
    username: hug.types.text,
    tweet_content: hug.types.text,
    db: sqlite,
):
    tweets = db["posts"]

    tweet = {
        "username": username,
        "text": tweet_content,
    }

    try:
        tweets.insert(tweet)
        tweet["id"] = tweets.last_pk
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

    response.set_header("Location", f"/posts/{tweet['id']}")
    return tweet

# This route reposts a tweet
@hug.post("/posts/retweet", status=hug.falcon.HTTP_201, requires=hug.authentication.basic(auth))
def reTweet(
    request,
    response,
    username: hug.types.text,
    retweet_id: hug.types.number,
    db: sqlite,
):
    oldtweet = postsById(response, retweet_id, db)
    tweet_content = {"Retweet:": oldtweet}
    tweetUrl=f"localhost:80/posts/{retweet_id}"
    tweets = db["posts"]

    tweet = {
        "username": username,
        "text": tweet_content,
    }

    try:
        tweets.insert(tweet)
        tweet["id"] = tweets.last_pk
        tweet["original_url"] = tweetUrl
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

    response.set_header("Location", f"/posts/{tweet['id']}")
    return tweet

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# project 3

#Registers this service with the registry service
@hug.startup()
def register(response):
    url = socket.getfqdn("localhost") +':'+ os.environ["PORT"]
    d = {'url':url,'service':'posts'}
    r = requests.post(config['registry']['register'], data=d)

#Returns a 200 ok and alive status 
@hug.get("/posts/health-check/")
def healthCheck(response):
    response.status = hug.falcon.HTTP_200
    return {"status": "alive"}