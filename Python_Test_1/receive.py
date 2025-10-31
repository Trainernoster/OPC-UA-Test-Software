# import
import pika # Python librarby based on the AMQR protocol
import datetime # Get current time
import time # Sleep library
import sys # System library to get CLI access 

# RabbitMQ connection
credentials = pika.PlainCredentials('admin', 'RabbitAdmin')                     # Credentials for the Rabbitmq user
parameters = pika.ConnectionParameters('192.168.2.19', 5672, '/', credentials)  # Connection data of the broker

# Creating connection
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare a queue (creates if it doesn't exist)
channel.queue_declare(queue='test_queue')

# create a update function for the time
def updateTime(message_time):
    sys.stdout.write("\033[K")                          # Delete the old message
    # Get current time
    current_time = datetime.datetime.now()
    clock = current_time.strftime("%H:%M:%S.%f")[:-2]
    
    # Print message
    print(f"Received:")
    print(f"            Time from server: {message_time}")
    print(f"           Time from machine: {clock}")
    sys.stdout.write("\033[F\033[F\033[F")                  # Set courser to message top

# Callback if message arrives
def callback(ch, method, properties, body):
    updateTime(body.decode())

# Subscribe to the queue
channel.basic_consume(queue='test_queue',
                      on_message_callback=callback,
                      auto_ack=True)

# End
print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
