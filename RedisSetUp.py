import redis 

red = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True) # posts as key
red1 = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True) # popular posts 
red2 = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True) # users as key
name2 = "PopularPosts" # Ordered set with post id. number = amount of likes

# Flushing
red.flushall()
red1.flushall()
red2.flushall()
# Inserting data

red.sadd("1", "asd", "KevinAWortman")
red.sadd("2", "asd")
red.sadd("3", "KevinAWortman")
red.sadd("4", "asd", "Beth_CSUF", "ProfAvery")
red.sadd("5", "asd")

red1.zincrby(name2, 2, "1")
red1.zincrby(name2, 1, "2")
red1.zincrby(name2, 1, "3")
red1.zincrby(name2, 3, "4")
red1.zincrby(name2, 1, "5")

red2.sadd("asd", "1", "2", "4", "5")
red2.sadd("Beth_CSUF", "4")
red2.sadd("KevinAWortman", "1", "3")
red2.sadd("ProfAvery", "4")