FROM mozilla/sbt
RUN mkdir /kafka_streams
COPY transform.scala /kafka_streams
COPY transform.sbt /kafka_streams
WORKDIR /kafka_streams
ENTRYPOINT ["sbt", "run"]
