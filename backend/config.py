import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
AI_KEY = os.getenv("AI_KEY", "")
TTL_SECONDS = int(os.getenv("TTL_SECONDS", 3600))
