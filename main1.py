#!/usr/bin/env python3

import argparse
import bisect
from datetime import datetime
import json
import os
import re
import redis
from redis_lru import RedisLRU


from mongoengine import connect, Document, ReferenceField, StringField, ListField
from mongoengine import DateField


URI="mongodb+srv://roybebru:1Kviton.ka@cluster0.pluwqkl.mongodb.net/?retryWrites=true&w=majority"


client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client, default_ttl=60)


#{{{ Data Classes

class Author(Document):
    fullname = StringField(max_length=127, required=True)
    description = StringField()
    born_date = DateField()
    born_location = StringField(max_length=63)

class Quote(Document):
    author = ReferenceField(Author, required=True)
    quote = StringField(required=True)
    tags = ListField(StringField(max_length=31))

#}}}

def find_in_sorted_authors(author, sorted_list):
    """Case insensitive finding author in the sorted list"""
    author = author.upper()
    i = bisect.bisect_left(sorted_list, author,
                           key=lambda author: author["fullname"].upper())
    if i != len(sorted_list) and sorted_list[i]["fullname"].upper() == author:
        return i
    return -1

def handle_load(filename_authors, filename_quotes):
    try:
        with open(filename_authors, "r") as fh:
            authors = json.load(fh)
        if not isinstance(authors, list) or \
                not isinstance(authors[0], dict) or \
                "fullname" not in authors[0].keys():
            raise ValueError(f"[IAFL] File '{filename_authors}' "
                             "is incorrect authors file")
    except Exception as e:
        print(f"Cannot read authors json file: {str(e)}")
        exit(1)

    authors.sort(key=lambda author: author["fullname"])

    try:
        with open(filename_quotes, "r") as fh:
            quotes = json.load(fh)
        if not isinstance(quotes, list) or \
                not isinstance(quotes[0], dict) or \
                "quote" not in quotes[0].keys():
            raise ValueError(f"[IQFL] File '{filename_quotes}' "
                             "is incorrect quotes file")
    except Exception as e:
        print(f"Cannot read quotes json file: {str(e)}")
        exit(1)

    author_odms = []
    for amap in authors:
        author = Author()
        for k,v in amap.items():
            match k:
                case "fullname":
                    author.fullname = v
                case "description":
                    author.description = v
                case "born_date":
                    try:
                        author.born_date = datetime.strptime(v, "%B %d, %Y").date()
                    except ValueError as e:
                        print("Error while handling born_date field in "
                              f"{str(amap)[0:30]}..." "}: " f"{str(e)}")
                        break
                case "born_location":
                    author.born_location = v
                case _:
                    print(f"Unknown field '{k}' in {str(amap)[0:30]}..." "}: ignored")
        else:
            print(f"Save '{amap['fullname']}'")
            author.save()
            author_odms.append(author)
            continue
        author_odms.append(None)

    for qmap in quotes:
        quote = Quote()
        for k,v in qmap.items():
            match k:
                case "author":
                    ix = find_in_sorted_authors(v, authors)
                    if ix == -1:
                        print(f"Error: absent author '{v}' info: ignoring")
                        break
                    quote.author = author_odms[ix]
                case "quote":
                    quote.quote = v
                case "tags":
                    quote.tags = v
        else:
            quote.save()


@cache
def find_by_name(a: Author) -> list:
    print(f"In find_by_name({str(a)})")
    quotes = []
    for q in Quote.objects(author=a):
        quotes.append(q.quote)
    return quotes


@cache
def find_by_tags(regex) -> list:
    print(f"In find_by_tags({str(regex)})")
    quotes = []
    for q in Quote.objects(tags__regex=regex):
        tagstr = ",".join([f"'{t}'" for t in q.tags])
        quotes.append(q.quote + os.linesep
                      + f"[Author: {q.author.fullname}] [Tags: {tagstr}]")
    return quotes


def handle_find():
    try:
        while True:
            reqstr = input(">>> ").strip()
            if reqstr == "":
                continue
            elif reqstr.lower() == "exit":
                return
            try:
                key, value = reqstr.split(":")
                key = key.strip()
                value = value.strip()
            except ValueError:
                print("Wrong format. Usage: '{name|tag}:sample[,sample,...]'")
                continue

            if key.lower() == "name":
                #{{{ Searching quotes by author
                if not any((c in set(r"\.+*?[]()^$")) for c in value):
                    # It is not true regular expression
                    value = "^" + value
                try:
                    regex = re.compile(value, re.I)
                except Exception as e:
                    print(f"Wrong regular expression '{value}': {str(e)}")
                    continue
                nl = False
                for a in Author.objects(fullname__regex=regex):
                    if nl:
                        print()
                    for q in find_by_name(a):
                        print(q)
                    print(f"[Author: {a.fullname}]")
                    nl = True
                #}}}

            elif key.lower() == "tag":
                #{{{ Searching quotes by tags
                tags = value.split(",")
                regex = r"^(" + "|".join(tags) + ")"
                try:
                    regex = re.compile(regex, re.I)
                except Exception as e:
                    print(f"Wrong regular expression for'{value}': {str(e)}")
                    continue
                #}}}
                nl = False
                for q in find_by_tags(regex):
                    if nl:
                        print()
                    print(q)
                    nl = True

            else:
                print("Wrong format. Usage: '{name|tag}:sample[,sample,...]'")
    except (KeyboardInterrupt, EOFError):
        print()
        return


def parse_options():
    parser = argparse.ArgumentParser(description='Qatalog Application HW8')
    parser.add_argument("-l", "--load", nargs=2,
                        help="Load 'AUTHORS.json QUOTES.json' files")
    parser.add_argument("-c", "--clean", action=argparse.BooleanOptionalAction,
                        help="Clean database")
    parser.add_argument("-f", "--find", action=argparse.BooleanOptionalAction,
                        help="Interactive database searching")
    arg_map = vars(parser.parse_args())
    return arg_map


def main():
    arg_map = parse_options()

    connect(db="qatalog", host=URI)

    if arg_map["clean"]:
        # Clean all documents in database
        print("Cleaning database...")
        for q in Quote.objects:
            q.delete()
        for a in Author.objects:
            a.delete()

    if arg_map["load"]:
        print("Loading data to database...")
        handle_load(arg_map["load"][0], arg_map["load"][1])

    if arg_map["find"]:
        print("Inspecting database")
        handle_find()

if __name__ == '__main__':
    main()
