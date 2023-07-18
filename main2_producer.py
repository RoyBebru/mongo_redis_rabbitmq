#!/usr/bin/env python3

from datetime import datetime
from faker import Faker
import json
from mongoengine import connect
import os
import pika
from random import randint


from main2_model import Contact


URI="mongodb+srv://roybebru:1Kviton.ka@cluster0.pluwqkl.mongodb.net/?retryWrites=true&w=majority"


fake = Faker("uk_UA")


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='task_notify', exchange_type='direct')
channel.queue_declare(queue='email_queue', durable=True)
channel.queue_bind(exchange='task_notify', queue='email_queue')
channel.queue_declare(queue='tel_queue', durable=True)
channel.queue_bind(exchange='task_notify', queue='tel_queue')


#{{{
TRANSLITERATION_TABLE = (
    " _,'j,-_,аa,бb,вv,гg,дd,еe,ёe,жsz,зz,иy,йj,кk,лl,мm,нn,оo,пp,рr,"
    "сs,тt,уu,фf,хh,цc,чch,шw,щsw,ъ,ыy,ь,эe,юyu,яya,єye,іi,їyi,ґg"
)
TRANSLATION_TABLE={}
# Converting CONFIG.FILENAME_TRANSLATION_TABLE to useful inner representation"""
for pair in TRANSLITERATION_TABLE.split(','):
    (key, val) = (pair[:1], pair[1:])
    TRANSLATION_TABLE[ord(key)] = val
    TRANSLATION_TABLE[ord(key.upper())] = val.upper()
del TRANSLITERATION_TABLE
# print((fake.first_name()+" "+fake.last_name()+"'яков").translate(TRANSLATION_TABLE))
# exit(0)
#}}}


def cleandb():
    """Clean all documents in database"""
    print("Cleaning database...")
    for c in Contact.objects:
        c.delete()

def main():
    connect(db="notifypool", host=URI)
    cleandb()

    print("*** ФЕЙКОВІ КОНТАКТИ ДЛЯ РОЗСИЛКИ ПОВІДОМЛЕНЬ ***"
            + os.linesep + "-------------------------------------")
    for i in range(randint(3,9)):
        contact = Contact()
        first_name = fake.first_name()
        last_name = fake.last_name()
        contact.fullname = f"{last_name}, {first_name}"
        contact.email = (first_name + " "+last_name).translate(TRANSLATION_TABLE) \
                + r"@" + fake.free_email_domain()
        contact.tel = fake.phone_number()
        contact.isemailbetter = bool(randint(0,1))
        contact.save()

        print("FAKE CONTACT:"
                + os.linesep + "    " + f"Object Id: {contact.id}"
                + os.linesep + "    " + contact.fullname
                + os.linesep + "    " + contact.email
                + os.linesep + "    " + contact.tel
                + os.linesep + "    " + f"Is email better? {contact.isemailbetter}"
                + os.linesep + "    " + f"Is already sent? {contact.issent}")

        message = {
            "id": str(contact.id),
            "date": datetime.now().isoformat()
        }

        queue = "tel_queue"
        if contact.isemailbetter:
            queue = "email_queue"

        channel.basic_publish(
            exchange="task_notify",
            routing_key=queue,
            body=json.dumps(message).encode(),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        print(" [x] Sent %r" % message)
    connection.close()


if __name__ == '__main__':
    main()
