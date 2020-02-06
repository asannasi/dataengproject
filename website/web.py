from flask import Flask
from consumer import Consumer
app = Flask(__name__)

@app.route('/')
def hello_world():
    topics = ["test"]
    c = Consumer(topics)
    msg = c.consume_message()
    c.close()
    topics = ["KSQL_OUTPUT2"]
    c = Consumer(topics)
    msg2 = c.consume_message()
    c.close()
    return "Input:\n" + str(msg) + "\nNeo4j Input" + str(msg2)
