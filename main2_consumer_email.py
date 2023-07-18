#!/usr/bin/env python3

import json
from mongoengine import connect
import os
import pika


from main2_model import Contact


URI="mongodb+srv://roybebru:1Kviton.ka@cluster0.pluwqkl.mongodb.net/?retryWrites=true&w=majority"
connect(db="notifypool", host=URI)


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='email_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


def handle_contact(id):
    contact = Contact.objects(pk=id).first()
    if contact is None:
        print(f"No document with id={id}")
        return
    if contact.issent:
        return
    print(f"SENDING EMAIL TO {contact.email} FOR CONTACT:"
            + os.linesep + "    " + f"Object Id: {contact.id}"
            + os.linesep + "    " + contact.fullname
            + os.linesep + "    " + contact.email
            + os.linesep + "    " + contact.tel
            + os.linesep + "    " + f"Is email better? {contact.isemailbetter}"
            + os.linesep + "    " + f"Is already sent? {contact.issent} -> True")
    contact.issent = True
    contact.save()


def callback(ch, method, properties, body):
    message = json.loads(body.decode())
    print(f" [x] Received {message}")

    handle_contact(message["id"])

    print(f" [x] Done: {method.delivery_tag}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='email_queue', on_message_callback=callback)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print()
