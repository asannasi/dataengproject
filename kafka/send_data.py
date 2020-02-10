import logging

import config
from stream import S3_JSON_Stream
from producer import Producer

CHUNK_SIZE = 2048
NUM_CHUNKS = 100

# This program creates a stream from S3 to download JSON messages and then
# sends them to Kafka
if __name__ == "__main__":
    # setup logger
    logger = logging.getLogger(__name__)
    logger.setLevel(config.log_level)
    logger.addHandler(logging.StreamHandler())
    
    # connect to S3 and Kafka cluster
    stream = S3_JSON_Stream(config.bucket, config.key, CHUNK_SIZE, NUM_CHUNKS)
    producer = Producer(config.bootstrap_servers, logger=logger)

    # Download and send messages
    msg_counter = 0
    while True:
        json_msg = stream.get_msg()
        key = str(json_msg["match_id"])
        if msg_counter > 46686:
            producer.send_json_to_kafka(json_msg, key, config.topic_name)

        msg_counter += 1
        logger.info(f"Produced Msg {msg_counter} with Match ID {key}")
    producer.flush()
