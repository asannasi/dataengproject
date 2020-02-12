import redis
from py2neo import Graph

import json
from datetime import timedelta
import random

NUM_ONLINE_PLAYERS = 25
GRAPH_LINK = "bolt://10.0.0.12:7687"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_TTL = 30 # in minutes
SKIP_RANGE_MIN = 1
SKIP_RANGE_MAX = 50

def main():
    # Setup up connections to redis and neo4j
    db = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT
    )
    graph = Graph("bolt://10.0.0.12:7687")

    # Get player accounts to simulate online players
    skip = random.randint(SKIP_RANGE_MIN,SKIP_RANGE_MAX)
    player_query = "MATCH (p:Player) RETURN p.account_id SKIP " + str(skip)\
            + " LIMIT " + str(NUM_ONLINE_PLAYERS)
    players = graph.run(player_query).data()

    # Iterate through players and find the heroes their teammates used
    # with whom they won the most
    for player in players:
        account_id = player['p.account_id']
        hero_query = "MATCH (p:Player{account_id:'"+account_id+"'})\
                -[pa:PLAYED_AS]-(a:Avatar)-[w:WON_WITH]\
                -(teammate:Avatar)-[:IS]-(h:Hero) \
                RETURN DISTINCT teammate.account_id,a.hero_id,h.hero_id,\
                pa.weight,w.weight \
                ORDER BY pa.weight DESC, w.weight DESC LIMIT 5"
        heroes = graph.run(hero_query).data()
        teammates = {}
        # Iterate through each hero the player won with and rate each
        for hero in heroes:
            hero_id = hero['h.hero_id']
            if hero_id in teammates:
                teammates[hero_id] += hero['w.weight']
            else:
                teammates[hero_id] = 1
        # Sort the teammates dict by count
        best_teammates = sorted(teammates, key=teammates.get)[:4]
        
        # Store in redis
        db.setex(
            account_id, 
            timedelta(minutes=REDIS_TTL),
            str(best_teammates)
        )
    print("Stored")
    db.flushdb()

if __name__ == "__main__":
    while True:
        main()
