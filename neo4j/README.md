To initialize neo4j config file, run

docker run --rm \
    --volume=$HOME/neo4j/conf:/conf \
    neo4j:4.0 dump-config

as per https://neo4j.com/docs/operations-manual/current/docker/configuration/

I used neo4j streams version 3.5.5.
https://github.com/neo4j-contrib/neo4j-streams/releases/tag/3.5.5

Place this plugin as per 
https://neo4j.com/docs/operations-manual/current/docker/operations/
