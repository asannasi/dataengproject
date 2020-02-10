# Neo4j README

## Configuration

To initialize neo4j config file, run

```shell
docker run --rm \
    --volume=$HOME/neo4j/conf:/conf \
    neo4j:4.0 dump-config
```

My config file template is [here](./sample_neo4j.conf). I set the Kafka broker and zookeeper IPs and ports and then wrote Cypher queries for each player interaction corresponding to a Kafka topic.

## On Startup

To create [constraints](https://neo4j.com/docs/cypher-manual/current/administration/constraints/) for the neo4j database, I entered them manually into the browser once the database starts up. Connect via port 7474. The run.sh file and neo4j config file currently sets up neo4j without authentication.

## Resources

https://neo4j.com/docs/operations-manual/current/docker/configuration/

I used neo4j streams version 3.5.5.
https://github.com/neo4j-contrib/neo4j-streams/releases/tag/3.5.5

Place the plugin as per:
https://neo4j.com/docs/operations-manual/current/docker/operations/

Configure for Kafka
https://neo4j.com/docs/labs/neo4j-streams/current/introduction/#kafka_settings

Setup for Neo4j as a Kafka Consumer
https://neo4j.com/docs/labs/neo4j-streams/current/consumer/

