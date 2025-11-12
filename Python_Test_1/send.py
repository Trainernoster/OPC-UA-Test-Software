# import
import pika # Python librarby based on the AMQR protocol
import datetime # Get current time
import time # Sleep library
import sys # Deleting

# RabbitMQ connection
credentials = pika.PlainCredentials('admin', 'RabbitAdmin')                     # Credentials for the Rabbitmq user
parameters = pika.ConnectionParameters('192.168.50.2', 5672, '/', credentials)  # Connection data of the broker

# Creating connection
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare a queue (creates if it doesn't exist)
channel.queue_declare(queue='test_queue')

# Main programm loop
print("Press Ctrl+C to stop.")
try:
    while True:
        # Get current time
        current_time = datetime.datetime.now()
        clock = current_time.strftime("%H:%M:%S.%f")[:-2]
        message = f"{clock}"

        # Send message
        channel.basic_publish(exchange='',
                                routing_key='test_queue',
                                body=message)
        print(f"Sent: {message}")
        time.sleep(1)
        sys.stdout.write("\033[F")                  # Set courser to message top

except KeyboardInterrupt:
    print("Stopping send.")


connection.close()
