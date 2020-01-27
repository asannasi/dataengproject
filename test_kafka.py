import unittest
from consumer import Consumer
from producer import Producer

class KafkaTestCase(unittest.TestCase):

    def test_message(self):
       producer = Producer()
       p_msg = producer.produce_message()
       topics = ["test"]
       consumer = Consumer(topics)
       c_msg = consumer.consume_message()
       self.assertTrue(p_msg == c_msg)

if __name__ == '__main__':
    unittest.main()
