#
# CPSC449-Proj3
# Registry API

#### Brian Fang (brian.fang@csu.fullerton.edu)
#### Nathan Tran (ntran402@csu.fullerton.edu)
#### Ashkon Yavarinia (ashkon@csu.fullerton.edu)
#### Edgar Cruz (ed.cruz76@csu.fullerton.edu)

import hug
import threading
import requests
import time

lock = threading.Lock()

registry = {} #{url:serviceName}

# 2b. Checks with a services health-check endpoint to see if it is alive and removes it from the registry if its down
def healthChecker():
    while True:
        for url in registry:                            # goes through all urls in the registry
            print(registry[url])
            r = requests.get('http://' + url + '/' + registry[url] + "/health-check/")
            if r.status_code != 200:                    # checks if response is valid
                with lock:
                    registry.pop(url)                   #remove service from registry
                    return
        time.sleep(30)


# 2a. Creates a daemon thread which preforms the check
@hug.startup()
def healthCheck(response):
    x = threading.Thread(target=healthChecker, args=(), daemon=True)
    x.start()

# 1. Handles service registration
# TODO: Services will need to have a startup function to register
#       Test
@hug.post("/registry/register/", status=hug.falcon.HTTP_201)
def register(response, url:hug.types.text, service:hug.types.text):
    print(url, service)
    print(registry.items())
    if url not in registry.items():     # only registers a service if its not already registered
        registry.__setitem__(url,service)
        #registry.update(service)
        print(registry.items())

# 3. Checks if a service is alive and its available instances
# TODO: test
@hug.get("/registry/{service}")
def getRegistry(response, service:hug.types.text):
    if service in registry.values():                #service exists
        response.status = hug.falcon.HTTP_200
        inst = []
        for i in registry.items():                  #looks through all elements in the registry and checks if its from the requested service 
            if i[1] == service:
                inst.append(i[0])
        return {service: inst}
    else:                                           #service does not exist
        response.status = hug.falcon.HTTP_502
        return {service:'unavailable'}

# TODO:
# ~ 1. register services with the registry
# ~ 2. check health and update registry
# ~ 3. return a list of available instances of a service