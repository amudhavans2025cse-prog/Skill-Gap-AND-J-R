import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"), serverSelectionTimeoutMS=1200)
db = client[os.getenv("DB_NAME", "skillgap_db")]

def get_db():
    return db
