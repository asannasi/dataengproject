import boto3
import json

BUCKET_NAME = "arvind-opendota-dec2015"
KEY_NAME = "yasp-dump-2015-12-18.json"
CHUNK_SIZE = 1024
NUM_CHUNKS = 2

class S3_JSON_Stream:
    def __init__(self,bucket_name, key, chunk_size=1024, num_chunks=2):
       self.bucket = bucket_name
       self.key = key
       self.chunk_size = chunk_size
       self.num_chunks = num_chunks

       self.buffer = b""
       self.start_byte = 1
       self.end_byte = (self.chunk_size * self.num_chunks)-1

    def _send_request(self):
        # Send request to s3
        range_header = "bytes=" + str(self.start_byte) + "-" + str(self.end_byte)
        s3_response = boto3.client('s3').get_object(
                Bucket=self.bucket,
                Key=self.key,
                Range=range_header
        )
        return s3_response

    def get_msg(self):
        downloading = True
        msg = None
        while (downloading):
            # Make request to s3 and parse returned data by iterating chunks
            s3_response = self._send_request()
            s3_chunk_iter = s3_response["Body"].iter_chunks(chunk_size=self.chunk_size)
            for s3_chunk in s3_chunk_iter:
                msg_end_idx = s3_chunk.find(b"\n,")
                if msg_end_idx != -1:
                    downloading = False
                    s3_json = self.buffer + s3_chunk[:msg_end_idx]
                    try:
                        msg = json.loads(s3_json)
                    except Exception as e:
                         self.logger.error("Json could not be parsed.")
                         self.logger.debug(s3_json)
                    self.buffer = s3_chunk[msg_end_idx+2:]
                else:
                    self.buffer += s3_chunk

            self.start_byte = self.end_byte + 1
            self.end_byte = self.start_byte + self.chunk_size*self.num_chunks

        return msg

if __name__ == '__main__':
    stream = S3_JSON_Stream(BUCKET_NAME, KEY_NAME, CHUNK_SIZE, NUM_CHUNKS)
    counter = 0
    while True:
        counter += 1
        j = stream.get_msg()
        print("Parsed Message", counter)
