import boto3
import json
import logging

import config
from heroes import heroes_json

JSON_DELIMITER = b"\n,\n"
NUM_PLAYERS = 10
ANON_ID = 4294967295 # account id of anonymous players (set by dataset)
TEAM_BIT_POS = 128

# This class is for connecting to an S3 bucket containing a JSON file
# with an array of JSON messages and returning each message.
class S3_JSON_Stream:

    # Configure the stream
    def __init__(self,bucket_name, key, 
                chunk_size=1024, num_chunks=2, logger=None):

        # Configure the logger
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(config.log_level)
        self.logger.addHandler(logging.StreamHandler())

        # Set the S3 bucket and key from which to download from
        self.bucket = bucket_name
        self.key = key

        # Set how many bytes to read from S3 at a time
        self.chunk_size = chunk_size
        self.num_chunks = num_chunks
        self.start_byte = 1 # Set to 1 to avoid skip "["
        self.end_byte = (self.chunk_size * self.num_chunks)-1

        # Initialize a blank buffer to store partial downloads
        self.buffer = b""

    # Sends a single request to S3 with the byte range to download and
    # returns the response.
    def _send_request(self):
        range_header = "bytes=" + str(self.start_byte) + \
                       "-" + str(self.end_byte)
        s3_response = boto3.client('s3').get_object(
                Bucket=self.bucket,
                Key=self.key,
                Range=range_header
        )
        return s3_response

    # Sends requests to S3 until a full JSON message is able to be parsed.
    # This message is returned and leftover bytes are stored in the buffer.
    # The byte range is updated so that subsequent calls use the buffer and
    # the last call's byte range to get the next message.
    def download_raw_msg(self):
        # Check for a complete JSON message in the buffer
        delim_idx = self.buffer.find(JSON_DELIMITER)
        if delim_idx != -1:
            # Message found, so return parsed JSON and remove it from the buffer
            msg = json.loads(self.buffer[:delim_idx])
            self.buffer = self.buffer[delim_idx+len(JSON_DELIMITER):]
            return msg

        # Send requests to S3 until a complete JSON message can be parsed 
        downloading = True
        msg = None
        while (downloading):
            # Send S3 request and get iterator over returned bytes. The iterator
            # increments based on self.chunk_size.
            s3_response = self._send_request()
            s3_chunk_iter = s3_response["Body"] \
                            .iter_chunks(chunk_size=self.chunk_size)

            for s3_chunk in s3_chunk_iter:
                # Append chunk to buffer
                self.buffer += s3_chunk

                # Check if JSON message was already found. If a message was 
                # already parsed, the remaining chunks are appended.
                if msg == None:
                    # Check for a complete JSON message in the buffer
                    delim_idx = self.buffer.find(JSON_DELIMITER)
                    if delim_idx != -1:
                        # Message found, so try parsing
                        downloading = False
                        s3_json = self.buffer[:delim_idx]
                        try:
                            msg = json.loads(s3_json)
                        except Exception as e:
                            # Message could not be parsed
                            self.logger.error(e)
                            self.logger.debug(s3_json)
                            return None

                        # Remove parsed JSON from buffer
                        self.buffer= self.buffer[delim_idx+len(JSON_DELIMITER):]

            # Increment byte range
            self.start_byte = self.end_byte + 1
            self.end_byte = self.start_byte + self.chunk_size*self.num_chunks

        return msg

    # Extracts relevant fields and transforms it into hardcoded format.
    def transform_raw_msg(self, orig_msg):
        new_msg = {}

        # Set match data values
        new_msg["match_id"] = str(orig_msg["match_id"])
        new_msg["radiant_win"] = bool(orig_msg["radiant_win"])
        new_msg["start_time"] = str(orig_msg["start_time"])
        new_msg["duration"] = str(orig_msg["duration"])

        # Dict of hero id to account id. Dota2 does not allow repeats in a team.
        team_heroes = {}
        for i in range(NUM_PLAYERS):
            hero_id = orig_msg["players"][i]["hero_id"]
            team_heroes[hero_id] = str(orig_msg["players"][i]["account_id"])

        # Store player data into JSON array
        new_msg["players"] = []
        for i in range(NUM_PLAYERS):
            # Create dict for player data
            new_msg["players"].append({})
            new_player = new_msg["players"][i]
            orig_player = orig_msg["players"][i]
            # Set fields
            new_player["hero_id"] = orig_player["hero_id"]
            new_player["total_healing"] = orig_player["hero_healing"]
            new_player["total_hero_damage"] = orig_player["hero_damage"]
            new_player["total_tower_damage"] = orig_player["tower_damage"]
            new_player["xp_per_min"] = orig_player["xp_per_min"]
            new_player["gold_per_min"] = orig_player["gold_per_min"]

            if orig_player["account_id"] == None or \
                    orig_player["account_id"] == -1:
                # Standardize anonymous account ID
                new_player["account_id"] = str(ANON_ID)
            else:
                new_player["account_id"] = str(orig_player["account_id"])

            # Set the player's team from the bit field
            if orig_player["player_slot"] >= TEAM_BIT_POS:
                new_player["team"] = "radiant"
            else:
                new_player["team"] = "dire"

            # Parse player interactions. Original message is a list of 
            #format "npc_hero_blank, etc.", which will be changed to
            # a list of account_id's and corresponding hero id's.
            def get_interactions(field_name):
                interactions = []
                for name in orig_player[field_name]:
                    for hero in heroes_json:
                        if hero['name'] == name:
                            interaction = {
                                "account_id":team_heroes[hero['id']], 
                                "hero_id":hero['id']
                            }
                            interactions.append(interaction) 
                return interactions
            
            # Parse interactions
            new_player["killed"] = get_interactions("killed")
            new_player["damaged"] = get_interactions("damage")
            new_player["healed"] = get_interactions("healing")
            
        # Convert the dict into JSON and return it as a string
        return json.loads(json.dumps(new_msg))

    # Returns a JSON message downloaded from S3 in the transformed format. 
    def get_msg(self):
        orig_msg = self.download_raw_msg()
        new_msg = self.transform_raw_msg(orig_msg)
        return new_msg
