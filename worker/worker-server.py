#
# Worker server
#
import os, sys
import pickle
import platform
import pika
import redis
import pytesseract 
from PIL import Image
from pdf2image import convert_from_path



hostname = platform.node()
INFO = "{}.rest.info".format(hostname)
DEBUG = "{}.rest.debug".format(hostname)
redisHost = os.getenv("REDIS_HOST") or  "172.18.103.67" # "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "172.18.103.67" # "localhost" 

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbitMQHost))
channel = connection.channel()
logs_channel = connection.channel()

channel.exchange_declare(exchange='toWorker', exchange_type='direct')
logs_channel.exchange_declare(exchange ='logs', exchange_type = 'topic')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange='toWorker', queue=queue_name, routing_key='addEntry')

print(' [*] Waiting for logs. To exit press CTRL+C')

# Redis databases declaration
redisUsernamefilehashToFilename = redis.Redis(host = redisHost, db = 3)
redisUsernameToFilehashSet = redis.Redis(host = redisHost, db = 4)
redisFilehashToText = redis.Redis(host = redisHost, db = 5)

def callback(ch, method, properties, body):
    message = pickle.loads(body)
    filename = message['filename']
    # print(filename, file=sys.stderr)
    username = message['username']
    # print(username, file=sys.stderr)
    file_hash = message['hash']
    # print(file_hash, file=sys.stderr)
    file_data = pickle.loads(message['file'])
    # print(type(file_data), file=sys.stderr)

    logs_channel.basic_publish(
            exchange='logs', routing_key=INFO,\
            body="Recieved file with name: {} and hash: {}".format(filename, file_hash))
            
    redisUsernamefilehashToFilename.set(username+file_hash, filename)
    redisUsernameToFilehashSet.sadd(username, file_hash)

    with open(filename, 'wb') as fp: 
            fp.write(file_data)

    if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
        img = Image.open(filename)
        text = pytesseract.image_to_string(img)
    elif filename.lower().endswith('.pdf'):
        pages = convert_from_path(filename, 350)
        text = ""
        for page in pages: 
            page_filename = filename+"_page.jpg"
            page.save(page_filename, 'JPEG')
            img = Image.open(page_filename)
            text += pytesseract.image_to_string(img)
            os.remove(page_filename)
    
    redisFilehashToText.set(file_hash, text)
    os.remove(filename)

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
