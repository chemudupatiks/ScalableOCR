##
from flask import Flask, request, Response
import jsonpickle, pickle
import platform
import io, os, sys
import pika, redis
import hashlib, requests
import json
import secrets
import google.cloud
from google.cloud import storage

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or  "172.18.103.67" # "localhost" 
rabbitMQHost = os.getenv("RABBITMQ_HOST") or  "172.18.103.67" # "localhost"
hostname = os.uname()[1]
print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))
app = Flask(__name__)


'''
Rest APIs

Auth 
-----------
Login    : info(username, password) return(status)
Register : info(username, password) return(status)
Logout   : info(username, authkey) return(status)

Main 
-----------
AddDocument : params(document data) return(text, url, status)
GetAll : params() return ([text, url, status])
'''

INFO = "{}.rest.info".format(hostname)
DEBUG = "{}.rest.debug".format(hostname)

redisUsernamePwd = redis.Redis(host = redisHost, db = 1) # key - username and value - hash of password
redisAuthKey = redis.Redis(host = redisHost, db = 2) # key - username and password - login auth key
redisUsernamefilehashToFilename = redis.Redis(host = redisHost, db = 3)
redisUsernameToFilehashSet = redis.Redis(host = redisHost, db = 4)
redisFilehashToText = redis.Redis(host = redisHost, db = 5)



@app.route('/auth/login', methods = ['POST'])
def login():
    connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitMQHost))
    logs_channel = connection.channel()
    logs_channel.exchange_declare(exchange ='logs', exchange_type = 'topic')
    data = jsonpickle.decode(request.data)
    username = data['username']
    password = data['password']
    authkey = ""
    message = "Login failed"
    # print(password, file=sys.stderr)
    # print(redisUsernamePwd.get(username), file=sys.stderr)
    if redisUsernamePwd.exists(username):
        if redisAuthKey.get(username):
            message = "Already logged in!"
            authkey = redisAuthKey.get(username).decode()
            # print(authkey, file=sys.stderr)
            # print(authkey.decode(), file=sys.stderr)
        elif redisUsernamePwd.get(username).decode() ==  password:
            message = "Logged in successfully"
            authkey = secrets.token_hex(16)
            redisAuthKey.set(username, authkey)
    else: 
        message = "No such username. Please register!"
    
    response = {
        'message': message,
        'authkey': authkey
    }
    logs_channel.basic_publish(
                exchange='logs', routing_key=INFO, body="[auth/login] username: {}, authkey: {}".format(username,authkey))
    connection.close()
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/auth/register', methods=['POST'])
def register():
    connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitMQHost))
    logs_channel = connection.channel()
    logs_channel.exchange_declare(exchange ='logs', exchange_type = 'topic')
    data = jsonpickle.decode(request.data) 
    username = data['username']
    password = data['password']
    authkey = ""
    # print(username, file=sys.stderr)
    # print(password, file=sys.stderr)    
    # print(redisUsernamePwd.keys(), file=sys.stderr)
    # print(redisAuthKey.keys(), file=sys.stderr)
    message = "Username already exists!"
    if not redisUsernamePwd.exists(username):
        redisUsernamePwd.set(username, password)
        message = "Registered successfully!"
        redisAuthKey.set(username, authkey) 
    
    response = {
        'message': message
    }
    # print(response, file = sys.stderr)
    logs_channel.basic_publish(
                exchange='logs', routing_key=INFO, body="[auth/register] username: {}, message: {}".format(username,message))
    connection.close()
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/auth/logout', methods=['POST'])
def logout():
    connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitMQHost))
    logs_channel = connection.channel()
    logs_channel.exchange_declare(exchange ='logs', exchange_type = 'topic')
    data = jsonpickle.decode(request.data)
    username = data['username']
    authkey = data['authkey']
    message = "Unauthorized logout"
    if redisAuthKey.get(username).decode() == authkey:
        if authkey == "":
            message = "Already logged out"
        else:
            redisAuthKey.set(username, "")
            message = "Logged out successfully"

    response = {
        'message': message
    }
    logs_channel.basic_publish(
                exchange='logs', routing_key=INFO, body="[auth/logout] username: {}, message: {}".format(username, message))
    connection.close()
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/api/addfile/<filename>', methods=['POST'])
def add_file(filename):
    '''
    - if the authkey matches what is stored the redisAuthkey key-values store, send the file to the worker
    '''

    data = jsonpickle.decode(request.data)
    username = data['username']
    authkey = data['authkey']
    file_upload = data['file']
    # print(type(file_upload), file = sys.stderr)
    url = ""
    file_hash = ""
    try:
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
            message = "Cannot add file. Filename should end with ('.jpg', '.jpeg', '.png', '.pdf')"
        else: 
            if redisAuthKey.get(username).decode() == authkey:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=rabbitMQHost))
                worker_channel = connection.channel()
                logs_channel = connection.channel()

                worker_channel.exchange_declare(exchange='toWorker', exchange_type='direct')
                logs_channel.exchange_declare(exchange ='logs', exchange_type = 'topic')
                file_hash = hashlib.sha256(file_upload).hexdigest()

                # save the file in a bucket and send the url
                with open(filename, 'wb') as fp: 
                    fp.write(file_upload)
                
                bucket_name = "user-ocr-files"
                client = storage.Client()
                try:
                    bucket = client.get_bucket(bucket_name)
                except google.cloud.exceptions.NotFound:
                    print("Sorry, that bucket does not exist! Creating one now..", file=sys.stderr)
                    bucket = storage.Bucket(client, name=bucket_name, user_project="scalableocr")
                    bucket.location = "us"
                    bucket.storage_class = "COLDLINE"
                    bucket = client.create_bucket(bucket)

                # print(bucket, file=sys.stderr)
                blob = storage.Blob(file_hash, bucket)
                blob.upload_from_filename(filename)

                url = "https://storage.cloud.google.com/{}/{}".format(bucket_name, file_hash) 
                os.remove(filename)

                routing_key = 'addEntry'
                worker_message = {
                    'filename': filename,
                    'username': username,
                    'hash'    : file_hash, 
                    'file'    : pickle.dumps(file_upload, 0)
                }
                worker_channel.basic_publish(
                    exchange='toWorker', routing_key=routing_key, body=pickle.dumps(worker_message, 0))
                print("INFO [api/addfile] hash: {}".format(file_hash)) 

                logs_channel.basic_publish(
                    exchange='logs', routing_key=INFO, body="[api/addfile] hash: {}".format(file_hash))

                connection.close()
                message = "Added file successfully!"
            else: 
                message = "Unauthorized access"
        response = {
            'message': message,
            'url': url, 
            'file_hash': file_hash
        }
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=200, mimetype="application/json")
    except Exception as e: 
        connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitMQHost))
        logs_channel = connection.channel()
        logs_channel.exchange_declare(exchange ='logs', exchange_type = 'topic')
        logs_channel.basic_publish(
                exchange='logs', routing_key=INFO, body="[api/addfile] username: {}, message: {}".format(username, str(e)))
        connection.close()

        
@app.route('/api/getall', methods=['GET'])
def getall():
    connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitMQHost))
    logs_channel = connection.channel()
    logs_channel.exchange_declare(exchange ='logs', exchange_type = 'topic')
    data = jsonpickle.decode(request.data)
    username = data['username']
    authkey = data['authkey']

    message = "Unauthorized access"
    url = ""
    file_hash = ""
    bucket_name = "user-ocr-files"
    response = []
    if redisAuthKey.get(username).decode() == authkey:
        file_hashes = redisUsernameToFilehashSet.smembers(username)
        if file_hashes: 
            for file_hash in file_hashes: 
                username_filehash = username + file_hash.decode()
                filename = redisUsernamefilehashToFilename.get(username_filehash).decode()
                text = redisFilehashToText.get(file_hash).decode()
                url = "https://storage.cloud.google.com/{}/{}".format(bucket_name, file_hash)
                single_respose = {
                    'filename': filename, 
                    'filehash': file_hash.decode(), 
                    'url'     : url, 
                    'text'    : text
                }
                response.append(single_respose)
    else: 
        response = {
            'message': message
        }
    logs_channel.basic_publish(
                exchange='logs', routing_key=INFO, body="[api/getall] username: {}, authkey: {}".format(username, authkey))
    connection.close()
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/', methods=['GET'])
def hello():
    return '<h1> Scalable OCR Server</h1><p> Use a valid endpoint </p>'

@app.errorhandler(Exception)
def handle_exception(e):
    print(e)
    os._exit(1)

# start flask app
app.run(host="0.0.0.0", port=5000)
