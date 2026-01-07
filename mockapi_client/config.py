import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
TOKEN = os.getenv("API_TOKEN")
DEFAULT_TIMEOUT = 10