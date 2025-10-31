import pika

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.50.2'))
channel = connection.channel()

# Declare a queue (creates if it doesn't exist)
channel.queue_declare(queue='test_queue')

# Send messages
for i in range(5):
    message = f"Hello {i}"
    channel.basic_publish(exchange='',
                          routing_key='test_queue',
                          body=message)
    print(f"Sent: {message}")

connection.close()
