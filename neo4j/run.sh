sudo docker run \
	--publish=7474:7474 \
	--publish=7687:7687 \
	--volume=$HOME/neo4j/data:/data \
	--volume=/home/ubuntu/neo4j/plugins:/plugins \
	--volume=$HOME/neo4j/conf:/conf \
	--env NEO4J_AUTH=none  \
	--user="$(id -u):$(id -g)" \
	neo4j:3.5
