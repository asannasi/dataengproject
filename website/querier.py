from py2neo import Graph
import json

class Querier:
    def __init__(self):
        self.graph = Graph("bolt://10.0.0.12:7687")

    def num_nodes(self):
        return str(len(self.graph.nodes))

    def num_relationships(self):
        return str(len(self.graph.relationships))

    def _run_query(self, query):
        return json.loads(json.dumps(graph.run(query).data()))

    def top_heroes(self, account_id=0):    
        query = "MATCH (p:Player{account_id:'"+str(account_id)+"'})\
                -[r:PLAYED_AS]->(a:Avatar)-[:IS]-(h:Hero)\
                RETURN DISTINCT h.hero_id, r.weight ORDER BY r.weight\
                DESC LIMIT 5"
        return self._run_query(query)

    def won_heroes(self, account_id=0, hero_id=0):
        composite_id = str(account_id) + str(hero_id)
        query = "MATCH (a:Avatar{composite_id:'"+ composite_id +"'})\
                -[r:WON_WITH]-(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN DISTINCT h.hero_id, r.weight\
                ORDER BY r.weight DESC"
        return self._run_query(query)
       
    def lost_heroes(self, account_id=0, hero_id=0):
        composite_id = str(account_id) + str(hero_id)
        query = "MATCH (a:Avatar{composite_id:'"+ composite_id +"'})\
                -[r:LOST_WITH]-(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN DISTINCT h.hero_id, r.weight\
                ORDER BY r.weight DESC"
        return self._run_query(query)

    def killed_heroes(self, account_id=0, hero_id=0):
        composite_id = str(account_id) + str(hero_id)
        query = "MATCH (a:Avatar{composite_id:'"+ composite_id +"'})\
                -[r:KILLED]->(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN DISTINCT h.hero_id, r.weight\
                ORDER BY r.weight DESC"
        return self._run_query(query)

    def healed_heroes(self, account_id=0, hero_id=0):
        composite_id = str(account_id) + str(hero_id)
        query = "MATCH (a:Avatar{composite_id:'"+ composite_id +"'})\
                -[r:HEALED]->(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN DISTINCT h.hero_id, r.weight\
                ORDER BY r.weight DESC"
        return self._run_query(query)

    def damaged_heroes(self, account_id=0, hero_id=0):
        composite_id = str(account_id) + str(hero_id)
        query = "MATCH (a:Avatar{composite_id:'"+ composite_id +"'})\
                -[r:DAMAGED]->(a2:Avatar)-[:IS]-(h:Hero)\
                RETURN DISTINCT h.hero_id, r.weight\
                ORDER BY r.weight DESC"
        return self._run_query(query)

    def win_players(self, account_id=0, hero_id=0):
        composite_id = str(account_id) + str(hero_id)
        query = "MATCH (a:Avatar{composite_id:'"+ composite_id +\
                "'})-[r:WON_WITH]-(a2:Avatar)<-[r2:PLAYED_AS]-(p:Player)\
                RETURN DISTINCT p.account_id, r2.weight ORDER BY r2.weight DESC"
        return self._run_query(query)

    def json_to_string_heroes(self, link, results_json):
        output = ""
        for result in results_json:
            output += "Hero " + str(result['h.hero_id']) + " was " + link + " " +\
                     str(result['r.weight']) + " times, "
        return output

    def json_to_string_players(self,results_json):
        output = ""
        for result in results_json:
            output += "Player " + str(result['p.account_id']) + " , "
        return output
