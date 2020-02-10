import unittest
import json

import config
from consumer import Consumer
from producer import Producer

# This tests if a message sent to Kafka is successfully consumed.
class KafkaTestCase(unittest.TestCase):
    def test_message(self):
        topic = "test"

        # Make test message
        test_json = {}
        test_json["id"] = 1
        json_msg = json.loads(json.dumps(test_json))
        key = bytes(str(json_msg["id"]),'utf-8')

        # Send message
        producer = Producer(config.bootstrap_servers)
        p_msg = producer.send_json_to_kafka(json_msg, key,topic)

        # Consume message
        consumer = Consumer(config.bootstrap_servers, [topic])
        c_msg = consumer.consume_message()

        # Check if the messages are the same
        self.assertTrue(p_msg == c_msg)

if __name__ == '__main__':
    unittest.main()
