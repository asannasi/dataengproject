# Neo4j README

To initialize neo4j config file, run

```shell
docker run --rm \
    --volume=$HOME/neo4j/conf:/conf \
    neo4j:4.0 dump-config
```

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

