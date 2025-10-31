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

def callback(ch, method, properties, body):
    print(f"Received: {body.decode()}")

# Subscribe to the queue
channel.basic_consume(queue='test_queue',
                      on_message_callback=callback,
                      auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
