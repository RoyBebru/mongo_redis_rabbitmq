#!/usr/bin/env python3

from mongoengine import Document, StringField, BooleanField


#{{{ Data Classes
class Contact(Document):
    fullname = StringField(max_length=127, required=True)
    issent = BooleanField(required=True, default=False)
    email = StringField(max_length=255, required=True)
    tel = StringField(max_length=63, required=True)
    isemailbetter = BooleanField(requred=True, default=True)
#}}}
