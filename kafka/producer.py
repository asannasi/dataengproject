from confluent_kafka import Producer as KProducer
import logging
from stream import S3_JSON_Stream 
import json
import config
import random
import time

CHUNK_SIZE = 2048
NUM_CHUNKS = 100

LOG_LEVEL = logging.INFO

class Producer:
    def __init__(self, logger=None):
        # setup logger
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(LOG_LEVEL)
        self.logger.addHandler(logging.StreamHandler())

        # connect to Kafka cluster
        kp_config = {"bootstrap.servers":config.bootstrap_servers, "on_delivery":self.on_delivery}
        self.producer = KProducer(kp_config, logger=self.logger)
        self.logger.info("Producer configured")

        # Initialize stream
        self.stream = S3_JSON_Stream(config.bucket, config.key, CHUNK_SIZE, NUM_CHUNKS)

        self.delivered_msgs = 0

    def produce_message(self):
        json_msg = self.stream.get_msg()

        self.producer.produce(topic=config.topic_name, value=json.dumps(json_msg), callback=self.on_delivery, key=bytes(str(json_msg["match_id"]),'utf-8'))
        self.producer.poll(timeout=0)
        return json_msg

    def produce_messages(self):
        counter = 0
        while True:
            counter += 1
            json_msg= self.produce_message()
            self.logger.info(f"Produced Msg {counter}: MatchID {json_msg['match_id']}")
        self.producer.flush()

    def on_delivery(self, error, message):
        self.delivered_msgs += 1
        self.logger.info(f"Delivered Message {self.delivered_msgs}")
        self.logger.debug(f"{message.topic()}, {message.value()}")
        
if __name__ == '__main__':
    producer = Producer()
    producer.produce_messages()
