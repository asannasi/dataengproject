# Kafka

## Installation

I mostly followed the [Kafka quickstart](https://kafka.apache.org/quickstart)
to setup Zookeeper and Kafka brokers, but it skipped some needed steps for 
setting up a multi-broker cluster.

I went into each broker and ran these commands. The below commands assume 
a broker id and zookeeper id of 3. This should be unique for each 
broker/zookeeper.

```shell
cd ~
sudo apt update
sudo apt install openjdk-8-jdk openjdk-8-jre
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export JRE_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre
wget http://apache.mirrors.tds.net/kafka/2.4.0/kafka_2.12-2.4.0.tgz
tar -xzf kafka_2.12-2.4.0.tgz
cd kafka_2.12-2.4.0
sudo mkdir /var/lib/zookeeper
sudo touch /var/lib/zookeeper/myid
sudo echo "3" >> /var/lib/zookeeper/myid
sudo echo "syncLimit=2" >> ~/kafka_2.12-2.4.0/config/zookeeper.properties
sudo echo "tickTime=2000" >> ~/kafka_2.12-2.4.0/config/zookeeper.properties
sudo echo "initLimit=5" >> ~/kafka_2.12-2.4.0/config/zookeeper.properties
sudo echo server.1=<ZOOKEEPER-NODE-1-HOSTNAME>:2888:3888 >> ~/kafka_2.12-2.4.0/config/zookeeper.properties
sudo echo server.2=<ZOOKEEPER-NODE-2-HOSTNAME>:2888:3888 >> ~/kafka_2.12-2.4.0/config/zookeeper.properties
sudo echo server.3=<ZOOKEEPER-NODE-3-HOSTNAME>:2888:3888 >> ~/kafka_2.12-2.4.0/config/zookeeper.properties
```

Edit these properties (Remove the existing lines and add these)

```shell
sudo echo "dataDir=/var/lib/zookeeper" >> ~/kafka_2.12-2.4.0/config/zookeeper.properties
sudo echo "broker.id=3" >> config/server.properties
sudo echo "log.retention.hours=24" >> config/server.properties
sudo echo "num.partitions=10" >> config/server.properties
```

## Run

```shell
sudo bin/zookeeper-server-start.sh config/zookeeper.properties &
sudo bin/kafka-server-start.sh config/server.properties &
```

# Kafdrop

For viewing the data in my Kafka cluster, I used Kafdrop. I ran it in a 
[Docker container](https://hub.docker.com/r/obsidiandynamics/kafdrop).
The command is here and the website can be viewed on port 9000.

```shell
docker run -d --rm -p 9000:9000 \
    -e KAFKA_BROKERCONNECT=host:port,host:port \
    -e JVM_OPTS="-Xms32M -Xmx64M" \
    -e SERVER_SERVLET_CONTEXTPATH="/" \
    obsidiandynamics/kafdrop:latest
```
