import os
from dotenv import load_dotenv

def get_config():
    load_dotenv()
    return os.environ
