import os
from dotenv import load_dotenv

from pymongo import MongoClient

load_dotenv()
MONGO_URI = os.getenv("DB_URL")

client = MongoClient(MONGO_URI)

db = client.get_database("LMS")

books_collection = db.books
members_collection = db.members
borrowings_collection = db.borrowings