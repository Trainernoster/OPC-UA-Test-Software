# import
import pika # Python librarby based on the AMQR protocol
import datetime # Get current time
import time # Sleep library

# RabbitMQ connection
credentials = pika.PlainCredentials('admin', 'RabbitAdmin')                     # Credentials for the Rabbitmq user
parameters = pika.ConnectionParameters('192.168.2.19', 5672, '/', credentials)  # Connection data of the broker

# Creating connection
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare a queue (creates if it doesn't exist)
channel.queue_declare(queue='test_queue')

# Send messages
for i in range(60):
    current_time = datetime.datetime.now()
    clock = current_time.strftime("%H:%M:%S.%f")[:-2]
    message = f"The current time is {clock}"
    
    channel.basic_publish(exchange='',
                          routing_key='test_queue',
                          body=message)
    print(f"Sent: {message}")

    time.sleep(1)

connection.close()
