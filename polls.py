#
# CPSC449-Proj3
# Polls API

#### Brian Fang (brian.fang@csu.fullerton.edu)
#### Nathan Tran (ntran402@csu.fullerton.edu)
#### Ashkon Yavarinia (ashkon@csu.fullerton.edu)
#### Edgar Cruz (ed.cruz76@csu.fullerton.edu)

import configparser
import logging.config
import os
import socket

import hug
import requests
import json
import datetime

# IMPORT DATABASE STUFF DYNAMODB
import boto3

# Load configuration
#
config = configparser.ConfigParser()
config.read("./etc/api.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)


# Connect to database here
@hug.directive()
def dynamodb(**kwargs):
    return boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

@hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)

def auth(username, password):
	r = requests.get(config["users"]["url"]+username)#f"http://localhost:5000/users/{username}")
	temp = json.loads(r.text)
	user = temp["users"][0]
	if user["password"] == password:
		return user
	return False

# Routes
#

# Gets a poll based on composite_key(pollTimeStamp, question)
@hug.get("/polls/getPoll/", status=hug.falcon.HTTP_201, examples="pollTimeStamp=time_stamp_string&question=question_string")
def getPoll(
    response,
    pollTimeStamp : hug.types.text,
    question : hug.types.text,
    db : dynamodb,
):
    table = db.Table('polls')
    item = None

    #Query table based on composite_key(pollTimeStamp, question)
    try:
        response = table.get_item(
            Key={
                'pollTimeStamp' : pollTimeStamp,
                'question' : question
            }
        )
        item = response
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}
    return item



# Authenticated users can create a poll
@hug.post("/polls/create/", status=hug.falcon.HTTP_201, requires=hug.authentication.basic(auth))
def createPoll(
    response,
    db : dynamodb,
    question : hug.types.text,
    response1 : hug.types.text="",
    response2 : hug.types.text="",
    response3 : hug.types.text="",
    response4 : hug.types.text="",
):
    usersList = []
    poll = None

    table = db.Table('polls')

    # Put item into table
    try:
        poll={
        'pollTimeStamp' : str(datetime.datetime.now()),
        'question' : question,
        'response1' : response1,
        'response2' : response2,
        'response3' : response3,
        'response4' : response4,
        'voteCount1' : None if response1 == "" else 0,
        'voteCount2' : None if response2 == "" else 0,
        'voteCount3' : None if response3 == "" else 0,
        'voteCount4' : None if response4 == "" else 0,
        'usersList' : usersList,
        }
        table.put_item(Item=poll)
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}
    return poll

# Authenticated users can vote in a poll
@hug.patch("/polls/vote/", status=hug.falcon.HTTP_201, requires=hug.authentication.basic(auth))
def votePoll(
    response,
    pollTimeStamp : hug.types.text,
    question : hug.types.text,
    responseNum : hug.types.number,
    user : hug.directives.user,
    db : dynamodb,
):

    table = db.Table('polls')
    username = user['username']
    # username = user.username

    # Retrieve list of users that have voted
    try:
        response = table.get_item(
            Key={
                'pollTimeStamp' : pollTimeStamp,
                'question' : question
            }
        )
        item = response['Item']
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}


    # Check if current user exists in list of users that have voted
    if username in item['usersList']:
        return {"error": "User has already voted."}

    # create Update Expression
    updateString = "ADD voteCount" + str(responseNum) + " :inc SET usersList = list_append(usersList, :u)"

    # Cast vote
    try:
        reponse = table.update_item(
            Key={
                'pollTimeStamp' : pollTimeStamp,
                'question' : question
            },
            UpdateExpression=updateString,
            ExpressionAttributeValues={
                ':inc' : 1,
                ':u' : [username],
            },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

    return response


#Registers this service with the registry service
@hug.startup()
def register(response):
    url = socket.getfqdn("localhost") +':'+ os.environ["PORT"]
    d = {'url':url,'service':'polls'}
    r = requests.post(config['registry']['register'], data=d)

#Returns a 200 ok and alive status 
@hug.get("/polls/health-check/")
def healthCheck(response):
    response.status = hug.falcon.HTTP_200
    return {"status": "alive"}
