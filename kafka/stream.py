import boto3
import json
import logging

LOG_LEVEL = logging.DEBUG
class S3_JSON_Stream:
    def __init__(self,bucket_name, key, chunk_size=1024, num_chunks=2):
       self.bucket = bucket_name
       self.key = key
       self.chunk_size = chunk_size
       self.num_chunks = num_chunks

       self.buffer = b""
       self.start_byte = 1
       self.end_byte = (self.chunk_size * self.num_chunks)-1

       self.logger = logging.getLogger(__name__)
       self.logger.setLevel(LOG_LEVEL)
       self.logger.addHandler(logging.StreamHandler())
       

    def _send_request(self):
        # Send request to s3
        range_header = "bytes=" + str(self.start_byte) + "-" + str(self.end_byte)
        s3_response = boto3.client('s3').get_object(
                Bucket=self.bucket,
                Key=self.key,
                Range=range_header
        )
        return s3_response

    def download_msg(self):
        msg_end_idx = self.buffer.find(b"\n,\n")
        if msg_end_idx != -1:
            msg = json.loads(self.buffer[:msg_end_idx])
            self.buffer = self.buffer[msg_end_idx+3:]
            return msg
        downloading = True
        msg = None
        while (downloading):
            # Make request to s3 and parse returned data by iterating chunks
            s3_response = self._send_request()
            s3_chunk_iter = s3_response["Body"].iter_chunks(chunk_size=self.chunk_size)
            for s3_chunk in s3_chunk_iter:
                self.buffer += s3_chunk
                if msg == None:
                    msg_end_idx = self.buffer.find(b"\n,\n")
                    if msg_end_idx != -1:
                        downloading = False
                        s3_json = self.buffer[:msg_end_idx]
                        try:
                            msg = json.loads(s3_json)
                        except Exception as e:
                            self.logger.error(e)
                            self.logger.debug(s3_json)
                            return None
                        self.buffer = self.buffer[msg_end_idx+3:]

            self.start_byte = self.end_byte + 1
            self.end_byte = self.start_byte + self.chunk_size*self.num_chunks

        return msg

    def get_msg(self):
        orig_msg = self.download_msg()
        #return orig_msg
        new_msg = {}
        new_msg["match_id"] = orig_msg["match_id"]
        new_msg["radiant_win"] = orig_msg["radiant_win"]
        new_msg["players"] = []
        for i in range(9):
            player_data = orig_msg["players"][i]
            new_msg["players"].append({})
            if orig_msg["players"][i]["account_id"] == None or -1:
                new_msg["players"][i]["account_id"] = 4294967295
            else:
                new_msg["players"][i]["account_id"] = int(player_data["account_id"])
            new_msg["players"][i]["hero_id"] = player_data["hero_id"]
            new_msg["players"][i]["level"] = player_data["level"]
            if player_data["player_slot"] >= 128:
                new_msg["players"][i]["win"] = "true"
            else:
                new_msg["players"][i]["win"] = "false"
        return json.loads(json.dumps(new_msg))
