import logging
import json
from confluent_kafka import Consumer as KafkaConsumer

GROUP_ID = 1

# This class consumes messages from Kafka cluster's topics. It's 
# basically a wrapper for the official Kafka Confluent Consumer.
class Consumer:
    # Configure consumer
    def __init__(self, bootstrap_servers, topics, logger=None):
        # setup logger
        self.logger = logger or logging.getLogger(__name__)
        if logger == None:
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(logging.StreamHandler())

        # connect to kafka cluster after setting kafka consumer's config
        kc_config = {"bootstrap.servers":bootstrap_servers, 
                     "on_commit":self.on_commit, 
                     "group.id":GROUP_ID}
        self.consumer = KafkaConsumer(kc_config)
        self.logger.info("Consumer configured")
        
        # subscribe to topic
        self.consumer.subscribe(topics, on_assign=self.on_assignment)
    # Consumes a single message from a topic
    def consume_message(self):
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    self.logger.error("Message Error")
                else:
                    self.logger.info(f"Message found at {msg.offset()}")
                    self.logger.debug(f"Topic: {msg.topic()}, " + \
                                       "Partition: {msg.partition()}, " + \
                                       "Offset: {msg.offset()}")
                    self.logger.debug(f"Value: {msg.value()}")
                    # Return the complete message
                    return msg.value()
                    
        except KeyboardInterrupt:
            # If keyboard interrupts, close consumer connection
            self.close()

    # Close the consumer connection
    def close(self):
        self.logger.error("Closing Consumer")
        self.consumer.close()

    # Keep consuming messages in the topic
    def consume_messages(self):
        while True:
            json_msg = self.consume_message()
            self.logger.info(f"Got MatchID: {json_msg['match_id']}")
        self.consumer.close()

    # Called when the consumer commits it's new offset
    def on_commit(self, error, partition_list):
        self.logger.info(f"On Commit: Error: {error}, " \
                          "Partitions: {partition_list}")

    # Called when the consumer is assigned to a topic
    def on_assignment(self,consumer, partitions):
        self.logger.info(f"Assignment: {partitions}")
