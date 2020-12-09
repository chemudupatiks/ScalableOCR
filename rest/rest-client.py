#!/usr/bin/env python3
# 
#
# A sample REST client for the face match application
#
import requests
import json
import time
import sys, os
import jsonpickle
import hashlib

def login(addr, username, password, debug=False):
    headers = {'content-type': 'application/json'}
    pwd = hashlib.sha256(password.encode()).hexdigest()
    url = addr + '/auth/login'
    data = jsonpickle.encode({
        'username': username, 
        'password': pwd
    })
    response = requests.post(url, data=data, headers=headers)
    if debug: 
        print("Response is", response)
        print(json.loads(response.text))

def register(addr, username, password, debug=False):
    headers = {'content-type': 'application/json'}
    pwd = hashlib.sha256(password.encode()).hexdigest()
    url = addr + '/auth/register'
    data = jsonpickle.encode({
        'username': username, 
        'password': pwd
    })
    response = requests.post(url, data=data, headers=headers)
    if debug: 
        print("Response is", response)
        print(json.loads(response.text))

def logout(addr, username, authkey, debug=False):
    headers = {'content-type': 'application/json'}
    url = addr + '/auth/logout'
    data = jsonpickle.encode({
        'username': username, 
        'authkey' : authkey
    })
    response = requests.post(url, data=data, headers=headers)
    if debug: 
        print("Response is", response)
        print(json.loads(response.text))

def addfile(addr, username, authkey, filepath, debug=False):
    headers = {'content-type': 'application/json'}
    basepath, filename = os.path.split(filepath)
    url = addr + '/api/addfile/' + filename
    file_data = open(filepath, 'rb').read()
    data = jsonpickle.encode({
        'username': username, 
        'authkey' : authkey,
        'file'    : file_data  
    })
    response = requests.post(url, data=data, headers=headers)
    if debug: 
        print("Response is", response)
        print(json.loads(response.text))


def getall(addr, username, authkey, debug=False):
    headers = {'content-type': 'application/json'}
    url = addr + '/api/getall'
    data = jsonpickle.encode({
        'username': username, 
        'authkey' : authkey
    })
    response = requests.get(url, data=data, headers=headers)
    print(response.text, file= sys.stderr)
    if debug: 
        print("Response is", response)
        print(json.loads(response.text))


host = sys.argv[1]
cmd = sys.argv[2]

addr = 'http://{}'.format(host)

if cmd == 'login':
    username = sys.argv[3]
    password = sys.argv[4]
    reps = int(sys.argv[5])
    start = time.perf_counter()
    for x in range(reps):
        login(addr, username, password, True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'register':
    username = sys.argv[3]
    password = sys.argv[4]
    reps = int(sys.argv[5])
    start = time.perf_counter()
    for x in range(reps):
        register(addr, username, password, True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'logout':
    username = sys.argv[3]
    authkey = sys.argv[4]
    reps = int(sys.argv[5])
    start = time.perf_counter()
    for x in range(reps):
        logout(addr, username, authkey, True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'addfile':
    filepath = sys.argv[3]
    username = sys.argv[4]
    authkey = sys.argv[5]
    reps = int(sys.argv[6])
    start = time.perf_counter()
    for x in range(reps):
        addfile(addr, username, authkey, filepath, True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'getall':
    username = sys.argv[3]
    authkey = sys.argv[4]
    reps = int(sys.argv[5])
    start = time.perf_counter()
    for x in range(reps):
        getall(addr, username, authkey, True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
else:
    print("Unknown option", cmd)