# Gamer Matchmaking: A Winning Team is a Good Team

In the online video game Dota 2, each match is a battle between 2 teams of 5 players. However, many players do not actually play this game as a team but are instead drafted along with other individuals by the game's matchmaking system. 

Video games have the unique problem that every time someone interacts with their service, there is a inherent chance for the user to lose. How do developers keep players engaged with their game? Traditionally, players are matched based on their skill level for balanced teams so even losses are memorable and gripping experiences as opposed to frutrating ones. Under this system, the team for one match is not carried over to the other. This is a missed opportunity.

My project aims to reimagine matches as social interactions. Every match means a player has won with 4 other people and lost with 4 other people. These relationships can be represented as a property graph. Players can be matched based on their shared win rate with players they have played with before. This will help them build their own story when they engage with the game since they'll eventually learn the other player's playstyle, fostering teamwork. 

## Overall Pipeline

I pull JSON match data from S3 and produce it to Kafka with a python producer. Then a Kafka streams program will transform the data into a format useable by Neo4j, changing match data into player interactions. Neo4j reads the resulting Kafka topic and updates its database. My front-end website queries my database to matchmake teams.

## S3 to Kafka

This code is in the kafka folder. It uses python 3. It depends on boto3, json, and confluent-kafka libraries. It basically downloads from S3 in chunks using GET requests and returns parseable JSON messages.

```shell
docker container run kafka_producer
```
Or if you have the dependencies:
```shell
python3 send_data.py
```
