from pymongo import MongoClient
from config.config import settings

client = MongoClient(settings.MONGODB_URL)
db = client["Scraped_Data"]
collection = db["sample"]

def clean_collection():
    collection.delete_many({})