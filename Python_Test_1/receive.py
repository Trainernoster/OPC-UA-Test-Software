import pika

# Connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('vm1-ip'))
channel = connection.channel()

# Declare the same queue
channel.queue_declare(queue='test_queue')

def callback(ch, method, properties, body):
    print(f"Received: {body.decode()}")

# Subscribe to the queue
channel.basic_consume(queue='test_queue',
                      on_message_callback=callback,
                      auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
