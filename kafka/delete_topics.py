import config
from confluent_kafka.admin import AdminClient

# This program deletes topics from the kafka cluster
#github.com/confluentinc/confluent-kafka-python/blob/master/examples/adminapi.py

a = AdminClient({'bootstrap.servers':config.bootstrap_servers})
topics = [
"raw_json",
"lost_against",
"won_against",
"lost_with",
"won_with",
"neo4j",
"players"
]
fs = a.delete_topics(topics, operation_timeout=30)

# Wait for operation to finish.
for topic, f in fs.items():
    try:
        f.result()  # The result itself is None
        print("Topic {} deleted".format(topic))
    except Exception as e:
        print("Failed to delete topic {}: {}".format(topic, e))
