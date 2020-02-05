import logging
import json
from confluent_kafka import Producer as KProducer

# This class sends given messages to Kafka cluster. It's 
# basically a wrapper for the official Kafka Confluent Producer
class Producer:
    # Configure producer
    def __init__(self, bootstrap_servers, logger=None):
        # setup logger
        self.logger = logger or logging.getLogger(__name__)
        if logger == None:
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(logging.StreamHandler())

        # connect to Kafka cluster after setting kafka producer's config
        kp_config = {"bootstrap.servers":bootstrap_servers, \
                     "on_delivery":self.on_delivery}
        self.producer = KProducer(kp_config, logger=self.logger)
        self.logger.info("Producer configured")

        self.delivered_msgs = 0 # Counter

    # Send json to kafka to given topic
    def send_json_to_kafka(self, json_msg, msg_key, topic_name):
        self.producer.produce(topic=topic_name, \
                              value=json.dumps(json_msg), \
                              callback=self.on_delivery, \
                              key=msg_key)
        self.producer.poll(timeout=0)

    # This method is called every time a message is delivered to kafka
    def on_delivery(self, error, message):
        self.delivered_msgs += 1
        self.logger.info(f"Delivered Message {self.delivered_msgs}")
        self.logger.debug(f"{message.topic()}, {message.value()}")

    # This method forces queued messages to send
    def flush(self):
        self.producer.flush()
