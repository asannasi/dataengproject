from confluent_kafka import Consumer as KafkaConsumer
import logging
import json

BOOTSTRAP_SERVER1 = "ip-10-0-0-8.us-west-2.compute.internal:9092"
BOOTSTRAP_SERVER2 = "ip-10-0-0-5.us-west-2.compute.internal:9092"
BOOTSTRAP_SERVER3 = "ip-10-0-0-10.us-west-2.compute.internal:9092"
BOOTSTRAP_SERVERS = BOOTSTRAP_SERVER1 + "," + BOOTSTRAP_SERVER2 + "," + BOOTSTRAP_SERVER3

GROUP_ID = 1
LOG_LEVEL = logging.INFO 

class Consumer:
    def __init__(self, topics, logger=None):
        # setup logger
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())

        # connect to kafka cluster
        config = {"bootstrap.servers":BOOTSTRAP_SERVERS, "on_commit":self.on_commit, "group.id":GROUP_ID}
        self.consumer = KafkaConsumer(config)
        self.logger.info("Consumer configured")
        
        # subscribe to topic
        self.consumer.subscribe(topics, on_assign=self.on_assignment)
    
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
                    self.logger.debug(f"Topic: {msg.topic()}, Partition: {msg.partition()}, Offset: {msg.offset()}")
                    self.logger.debug(f"Value: {msg.value()}")

                    json_msg = json.loads(msg.value())
                    return json_msg
                    
        except KeyboardInterrupt:
            self.logger.error("Closing Consumer")
            self.consumer.close()

    def consume_messages(self):
        while True:
            json_msg = self.consume_message()

            self.logger.info(f"Got MatchID: {json_msg['match_id']}")
        self.consumer.close()

    def on_commit(self, error, partition_list):
        self.logger.info(f"On Commit: Error: {error}, Partitions: {partition_list}")

    def on_assignment(self,consumer, partitions):
        self.logger.info(f"Assignment: {partitions}")


if __name__ == "__main__":
    topics = ["test"]
    consumer = Consumer(topics)
    consumer.consume_messages()
