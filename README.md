# CPSC449-Proj3

#### Brian Fang (brian.fang@csu.fullerton.edu)
#### Nathan Tran (ntran402@csu.fullerton.edu)
#### Ashkon Yavarinia (ashkon@csu.fullerton.edu)
#### Edgar Cruz (ed.cruz76@csu.fullerton.edu)

## Setup
>```shell-session
>$ sudo apt update
>$ sudo apt install --yes python3-pip ruby-foreman httpie sqlite3
>$ python3 -m pip install hug sqlite-utils
>$ sudo apt install --yes haproxy gunicorn
>$ sudo apt install --yes redis python3-hiredis awcli python3-boto3
>```

- Navigate to /etc/haproxy/haproxy.cfg and paste the contents of etc/haproxy.cfg in the bottom and restart
- Port 80 is the new port for both api's while haproxy is running

>```shell-session
>$ sudo systemctl restart haproxy
>```

- Configure AWS
>```shell-session
>$ aws configure
>$ AWS Access Key ID [None]: fakeMyKeyId
>$ AWS Secret Access Key [None]: fakeSecretAccessKey
>$ Default region name [None]: us-west-2
>$ Default output format [None]: table
>```

- Download the proper DynamoDB package for your system from https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html
- Extract the package, navigate to the location of DynamoDBLocal.jar, and enter the following command:
>```shell-session
>$ java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb


- Navigate to the CPSC449-Proj3 directory and create the databases and start the servers

>```shell-session
>$ bash ./bin/init.sh
>$ foreman start -m users=1,posts=3,likes=1,polls=1,registry=1
>```
Note - You may need to change file permissions to run/edit files

---
# Users

## - Create a user
**POST:** /users/   
Creates a user and stores it into users.db
> ```shell-session
> $ http -f POST localhost/users/ username="newUser" email="email@site.com" bio="bio here" password="password"
> ```

## - Get a user
**GET:** /users/{username}	  
Gets the specified user
> ```shell-session
> $ http GET localhost/users/{username}
> ```

## - Follow a user
**POST:** /users/following	  
Allows a user to follow another
> ```shell-session
> $ http -f POST localhost/users/following/ users_id=# following_id=#
> ```

## - Get list of users someone is following
**GET:** /users/following/{username}	  
Gets a list of users someone is following
> ```shell-session
> $ http GET localhost/users/following/{username}
> ```

---
# Posts

## - Tweeting
**POST:** /posts/ Creates a new post and inserts it into posts.db
> ```shell-session
> $ http -f -a username:password POST localhost/posts/ username="username" tweet_content="content"
> ```

## - Retweeting
**POST:** /posts/retweet
Retweets a post specified by *retweet_id*
> ```shell-session
> $ http -f -a username:password POST localhost/posts/retweet username="username" retweet_id=#
> ```

## - Retrieve tweet by postId
**GET:** /posts/{postId}   
Retrieves a post by its *postId*
> ```shell-session
> $ http GET localhost/posts/{postId}
> ```

## - Retrieve all tweets
**GET:** /posts   
Retrieves all posts
> ```shell-session
> $ http GET localhost/posts
> ```

## - Retrieve user timeline
**GET:** /posts/timeline/user/{username}   
Retrieves a list of posts by *username* in reverse chronological order
> ```shell-session
> $ http GET localhost/posts/timeline/user/{username}
> ```

## - Retrieve home timeline
**GET:** /posts/timeline/home   
Retrieves a list of posts by users specified in *users_followed* in reverse chronological order
> ```shell-session
> $ http -f -a username:password GET localhost/posts/timeline/home/ users_followed="comma_delimited_list_of_usernames"   
ex: users_followed="Ashkon,BrianFang2"
> ```

## - Retrieve public timeline
**GET:** /posts/timeline/public   
Retrieves a list of all posts in reverse chronological order
> ```shell-session
> $ http GET localhost/posts/timeline/public
> ```

---
# Likes

## - Liking Tweets
**POST:** /likes/{username}/{tweetId}  
Likes a specific post as a given user and updates redis values  
> ```shell-session
> $ http POST localhost/likes/Ashkon/5
> ```

## - Retrieve tweets that a user liked
**GET:** /likes/{username}/liked_posts  
Retrieves a list of all the posts that a given user has liked  
> ```shell-session
> $ http GET localhost/likes/Ashkon/liked_posts
> ```

## - Retrieve likes for a tweet
**GET:** /likes/posts/{tweetId}/likes  
Retrieves a list of all the users that liked a given post as well as the total number of likes  
> ```shell-session
> $ http GET localhost/likes/posts/4/likes
> ```

## - Retrieve popular posts
**GET:** /likes/posts/popular_posts  
Retrieves the most popular posts in the service. Shows posts with more liked first   
> ```shell-session
> $ http GET localhost/likes/posts/popular_posts
> ```

---
# Polls

## - Create a Poll
**POST:** /polls/create  
Authenticated users can create a new poll with 1 question and up to 4 responses
> ```shell-session
> $ http -f -a username:password POST localhost/polls/create question="poll_question" response1="response1" response2="response2" response3="response3" response4="response4"
> ```
ex: question="What is your favorite color?" response1="Blue" response2="Green" response3="Red" response4=""
> ```
Note- pollTimeStamp will be returned when a poll is created. This is used to retrieve a poll and voting for a poll.

## - Get a poll by key
**GET:** /polls/getPoll  
Get a poll by the compositeKey(pollTimeStamp, question)
> ```shell-session
> $ http GET localhost/polls/getPoll pollTimeStamp=="time_stamp_when_poll_created" question=="poll_question"
> ```
ex: pollTimeStamp=="2021-11-25 11:19:32.398902" question=="What is your favorite color?"
> ```

## - Vote for a poll
**PATCH:** /polls/vote  
Authenticated users can vote for a response in a poll
> ```shell-session
> $ http -f -a username:password PATCH localhost/polls/vote pollTimeStamp="time_stamp_when_poll_created" question="poll_question" responseNum=#
> ```
ex: pollTimeStamp="2021-11-25 11:19:32.398902" question="What is your favorite color?" responseNum=3
> ```

---
# Registry

## - Note:  
The registry service assumes that each service defines a fixed URL ```/health-check``` that returns 200 for the registries health check process

## - Register a service
**POST:** /registry/register  
Handles service registration done by services in the backend and should not normally be accessed by users.
> ```shell-session
> $ http -f POST localhost/registry/register url="domainName:port" service="service"
> ```
>ex: url="localhost:5100" service="users"

## - Check a services health
**GET:** /registry/{service}  
Checks if a service is alive and its available services.
> ```shell-session
> $ http GET localhost/registry/{service}
> ```
>ex: http GET localhost/registry/posts
