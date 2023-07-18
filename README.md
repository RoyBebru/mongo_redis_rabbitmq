# mongo_redis_rabbitmq

ЧАСТИНА 1

Хмарна MongoDB сконфігурована на час демонстрації в режимі доступу звідусіль.

Завантажити в MongoDB:

    main1.py -l authors.json quotes.json

Очистити DB:

    main1.py -c

Інтерактивний режим запитів:

    main1.py -f

    Inspecting database
    >>> name:.+in
    In find_by_name(Author object)
    “The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”
    “There are only two ways to live your life. One is as though nothing is a miracle. The other is as though everything is a miracle.”
    “Try not to become a man of success. Rather become a man of value.”
    [Author: Albert Einstein]

    In find_by_name(Author object)
    “A day without sunshine is like, you know, night.”
    [Author: Steve Martin]
    >>> tag:ch
    In find_by_tags(re.compile('^(ch)', re.IGNORECASE))
    “The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”
    [Author: Albert Einstein] [Tags: 'change','deep-thoughts','thinking','world']
    >>> tag:ad,ch
    In find_by_tags(re.compile('^(ad|ch)', re.IGNORECASE))
    “The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”
    [Author: Albert Einstein] [Tags: 'change','deep-thoughts','thinking','world']

    “Try not to become a man of success. Rather become a man of value.”
    [Author: Albert Einstein] [Tags: 'adulthood','success','value']
    >>> tag:ad,ch
    “The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”
    [Author: Albert Einstein] [Tags: 'change','deep-thoughts','thinking','world']

    “Try not to become a man of success. Rather become a man of value.”
    [Author: Albert Einstein] [Tags: 'adulthood','success','value']
    >>>

ЧАСТИНА 2

Генерація фейкових контактів та завдань на їх обробку черговим виконавцем через RabbitMQ:

    main2_producer.py

Виконавець обробки черг на розсилку повідомлень через email:

    main2_comsumer_email.py

Виконавець обробки черг на розсилку повідомлень через SMS (телефон):

    main2_consumer_tel.py

ВИСНОВКИ, ОСОБЛИВОСТІ, ПИТАННЯ:

1. При використанні кеша redis значення залишаються між викликами.
2. Celery потрібен тільки на стороні віконавця (Consumer'а).
3. Як вийти по Ctrl+C (зловити KeyboardInterrupt) з циклу в channel.basic_consume(queue='email_queue', on_message_callback=callback)
без фіктивних повідомлень про помилку?


