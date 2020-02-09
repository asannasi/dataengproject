FROM python:3.6.9
RUN pip3 install boto3
RUN pip3 install confluent-kafka
COPY . /app
WORKDIR /app
ENTRYPOINT ["python3", "send_data.py"]
