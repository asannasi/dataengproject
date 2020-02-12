import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
db = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT
)
db.flushdb()
