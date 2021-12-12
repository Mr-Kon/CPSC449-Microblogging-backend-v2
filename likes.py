#
# CPSC449-Proj3
# Likes API

#### Brian Fang (brian.fang@csu.fullerton.edu)
#### Nathan Tran (ntran402@csu.fullerton.edu)
#### Ashkon Yavarinia (ashkon@csu.fullerton.edu)
#### Edgar Cruz (ed.cruz76@csu.fullerton.edu)

import configparser
import logging.config
import os
import socket

import hug
from hug.directives import user
import requests
import json
import redis


# Load configuration
#
config = configparser.ConfigParser()
config.read("./etc/api.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)

# Set up for Redis
#
red = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True) # posts as key
red1 = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True) # popular posts 
red2 = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True) # users as key

name1 = "Posts"     # Set that has list of users that liked the post
name2 = "PopularPosts" # Ordered set with post id. number = amount of likes
name3 = "UserLiked" # Set that has post ids for posts that the user liked



# Arguments to inject into route functions
#
@hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)


# Routes


# Route for liking tweets
@hug.post("/likes/{username}/{tweetId}", status=hug.falcon.HTTP_201)
def likeTweet(
    response,
    username: hug.types.text,
    tweetId: hug.types.text,
):
    # checking if user exists
    r = requests.get(f"http://localhost/users/{username}")
    temp = json.loads(r.text)
    if not temp["users"]: # temp returns an empty dict if empty
        response.status = hug.falcon.HTTP_404
        return {"error": "User not found"}
    # checking if tweet exists
    r2 = requests.get(f"http://localhost/posts/{tweetId}")
    temp2 = json.loads(r2.text)
    if not temp2:   #temp2 returns nothing if empty
        response.status = hug.falcon.HTTP_404
        return {"error": "Post not found"}

    # Setting data for redis

    # If statment tries to insert into set
    # If successfull (equals to 1), new user liked the post!
    # Thus increase the score for value in the sorted set
    # If statment not successful -> the user already liked the tweet
    # Thus don't increment the score for value in sorted set
    if red.sadd(tweetId, username): 
        red1.zincrby(name2, 1, tweetId)
    red2.sadd(username, tweetId)


    response.set_header("Location", f"/{username}/liked_posts")
    likedPosts = {}
    likedPosts["Liked_Posts"] = red2.smembers(username)
    return likedPosts

# Route for getting liked tweets for a given user
@hug.get("/likes/{username}/liked_posts")
def likeTweet(
    response,
    username: hug.types.text,
):
    # checking if user exists
    r = requests.get(f"http://localhost/users/{username}")
    temp = json.loads(r.text)
    if not temp["users"]:
        response.status = hug.falcon.HTTP_404
        return {"error": "User not found"}


    # Preparing data types for the result
    liked_posts = {}
    arr = []
    id_of_likedPosts = list(red2.smembers(username))
    # Getting the posts here
    req = requests.get(f"http://localhost/posts/")
    tempPosts = json.loads(req.text)
    for post in tempPosts["tweets"]:
        if str(post["id"]) in list(red2.smembers(username)):
            arr.append(post)
    liked_posts["Liked_Posts"] = arr
    return liked_posts

# Route for getting all the likes for a given
@hug.get("/likes/posts/{tweetId}/likes")
def likeTweet(
    response,
    tweetId: hug.types.text,
):
    red = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    # check if post exists 
    r = requests.get(f"http://localhost//posts/{tweetId}")
    temp = json.loads(r.text)
    if not temp:
        response.status = hug.falcon.HTTP_404
        return {"error": "Post not found"}


    # Preparing data types for the result
    likes = {}
    likes["amount_of_likes"] = red.scard(tweetId)
    likes["liked_by"] = list(red.smembers(tweetId))
    return likes


# Route for getting posts sorted by amount of likes, post wont show if 0 likes
@hug.get("/likes/posts/popular_posts")
def likeTweet(
    response,
):
    # Preparing data types for the result
    popular_posts = {}
    arr = []
    allPosts = red1.zrevrange(name2, 0, -1, withscores=True) # Tuple
    # Getting the posts here
    for post in allPosts:
        req = requests.get(f"http://localhost/posts/{post[0]}")
        tempPosts = json.loads(req.text)
        tempPosts["likes"] = post[1]
        arr.append(tempPosts)
    popular_posts["Popular_Posts"] = arr
    return popular_posts

#Registers this service with the registry service
@hug.startup()
def register(response):
    url = socket.getfqdn("localhost") +':'+ os.environ["PORT"]
    d = {'url':url,'service':'likes'}
    r = requests.post(config['registry']['register'], data=d)

#Returns a 200 ok and alive status 
@hug.get("/likes/health-check/")
def healthCheck(response):
    response.status = hug.falcon.HTTP_200
    return {"status": "alive"}