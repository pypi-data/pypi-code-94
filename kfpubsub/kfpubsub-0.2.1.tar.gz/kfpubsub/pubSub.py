# -*- coding: utf-8 -*-
import json
import redis
import logging

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient, KafkaClient
from kafka.admin import NewTopic

logger = logging.getLogger('pubsub')
fh = logging.StreamHandler()
fh.setFormatter(logging.Formatter(fmt='%(asctime)-22s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


class PubSub(object):

    def __init__(
            self,
            host='localhost',
            port=6379,
            database=0,
            enable_kafka=False,
            kafka_brokers=None,
            kafka_group_id=None,
            kafka_topics=None,
            kafka_enable_auto_commit=False,
            kafka_replication_factor=1,
            kafka_partitions=1,
            kafka_poll_timeout=500,
    ):
        self.connection = None
        self.pubsub = None
        self.host = host
        self.port = port
        self.database = database

        if enable_kafka:
            if not kafka_brokers or not kafka_topics:
                raise ValueError("Couldn't find kafka_topics or kafka_brokers while kafka is enabled")

            self.enable_kafka = enable_kafka
            self.kafka_brokers = kafka_brokers
            self.kafka_enable_auto_commit = kafka_enable_auto_commit
            self.kafka_group_id = kafka_group_id
            self.kafka_topics = kafka_topics
            self.kafka_replication_factor = kafka_replication_factor
            self.kafka_partitions = kafka_partitions
            self.kafka_poll_timeout = kafka_poll_timeout
            self._kafka_producer = None
            self._kafka_consumer = None
            self.validated_topics = False

    def get_kafka_producer(self):
        # We don't want to establish a connection everytime we need to use the producer
        if self._kafka_producer:
            return self._kafka_producer

        # https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html
        # gzip is natively supported but we should use lz4 or zlib.
        # uber did some tests and they are using messagepack with zlib events in order to save space and cpu time.
        # more at: https://eng.uber.com/trip-data-squeeze-json-encoding-compression/
        return KafkaProducer(
            bootstrap_servers=self.kafka_brokers,
            compression_type="gzip",
        )

    def get_kafka_consumer(self):
        # We don't want to establish a connection everytime we need to use the consumer
        if self._kafka_consumer:
            return self._kafka_consumer

        if not self.kafka_group_id:
            # If there is no group id we will consume all events from all partitions but if there is a group id
            # this consumer will be part of a larger group and consumes the partitions that are assigned to it.
            logger.info("Kafka consumer running without a group id. I hope you know what you are doing")

        # https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html
        # we don't enable autocommit because we have to take care of that.
        return KafkaConsumer(
            group_id=self.kafka_group_id,
            bootstrap_servers=self.kafka_brokers,
            enable_auto_commit=self.kafka_enable_auto_commit,
        )

    def create_kafka_topics(self):
        client = KafkaClient(bootstrap_servers=self.kafka_brokers)
        kafka_admin = KafkaAdminClient(bootstrap_servers=self.kafka_brokers)

        future = client.cluster.request_update()
        client.poll(future=future)
        metadata = client.cluster
        already_topics = metadata.topics()

        new_topic_list = list()
        for topic in self.kafka_topics:
            if topic not in already_topics:
                new_topic_list.append(NewTopic(
                    name=topic,
                    num_partitions=self.kafka_partitions,
                    replication_factor=self.kafka_replication_factor,
                ))
                logger.info("Creating new kafka topic %s" % (topic, ))

        kafka_admin.create_topics(new_topic_list)
        self.validated_topics = True

    def emit(self, event, message, emit=False):

        # Convert dict to string
        message_str = json.dumps(message)
        logger.debug(" [x] Sent %r:%r" % (event, message_str))

        if not emit:
            return

        self.connection = redis.StrictRedis(host=self.host, port=self.port, db=self.database)
        self.pubsub = self.connection.pubsub()
        self.connection.publish(channel=event, message=message_str)
        self.pubsub.close()

        if self.enable_kafka:
            if not self.validated_topics:
                raise ValueError("You forgot to run create_kafka_topics method")

            kafka_producer = self.get_kafka_producer()
            future = kafka_producer.send(event, bytes(message_str, "utf-8"))
            # Should we wait and make sure it is sent ?
            future.get(timeout=60)

    def receive(self, listeners, restart_connections=None):
        # We cannot have both (Redis & Kafka) consumers running at the same time, they will block the
        # thread they run on.
        if self.enable_kafka:
            self.receive_kafka(listeners)
        else:
            self.receive_redis(listeners, restart_connections)

    def receive_kafka(self, listeners):
        consumer = self.get_kafka_consumer()
        consumer.subscribe(listeners.keys())
        while True:
            # poll accepts timeout_ms and it will keep polling new records and batching them until timeout is met
            message = consumer.poll(self.kafka_poll_timeout)

            if len(message) == 0:
                continue

            for topic_partition, consumer_records in message.items():
                # we get back a dict with batches of records grouped by topic & partition
                for record in consumer_records:
                    # we might be able to use another type of serializer here that is more efficient.
                    message_json = json.loads(record.value.decode("utf-8"))
                    function = listeners.get(topic_partition.topic)

                    if function:
                        function(message_json)
                    else:
                        logger.info(
                            "unable to find function %s in order to consume that topic" % (topic_partition.topic,)
                        )

            # This will block until it receives ack., should we block?
            consumer.commit()

        consumer.unsubscribe()
        consumer.close(autocommit=self.kafka_enable_auto_commit)

    def receive_redis(self, listeners, restart_connections):
        self.connection = redis.StrictRedis(host=self.host, port=self.port, db=self.database)
        self.pubsub = self.connection.pubsub(ignore_subscribe_messages=True)

        def callback(message):
            """
            Receiving messages from the queue.
            It works by subscribing a callback function to a queue.
            """
            # Convert str to dict and call handler event function and get handler for event.
            # print(" [x] %r:%r" % (method.routing_key, body))
            logger.debug(u'[x] %(routing_key)s: %(body)s' % {
                'routing_key': message.get('channel'), 'body': message.get('data')
            })
            function = listeners.get(message.get('channel').decode("utf-8"))
            if function is None:
                print('Listener not found %s' % str(message.get('channel').decode("utf-8")))
                return
            my_body = json.loads(message.get('data'))
            logger.debug(u'[f] %(function)s loaded' % {'function': function})
            if restart_connections is not None:
                restart_connections()

            for item in function:
                item(my_body)

        for key in listeners.keys():
            for loaded_func in listeners.get(key):
                logger.info('Loaded function for key %r: %r' % (key, loaded_func.__name__))

            self.pubsub.subscribe(**{key: callback})

        logger.info(' [*] Waiting for logs. To exit press CTRL+C')

        for item in self.pubsub.listen():
            pass

        self.pubsub.close()
