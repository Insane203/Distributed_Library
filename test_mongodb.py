
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGO_URI", "mongodb://localhost:27016")
database_name = os.getenv("MONGO_DB", "DistributedLibrary")

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")

    db = client[database_name]

    print("MongoDB connection successful!")
    print("Database:", database_name)
    print("Collections:", db.list_collection_names())

    print("\nBooks in the database:")
    for book in db["Books"].find({}, {"_id": 0}):
        print(book)

except Exception as error:
    print("MongoDB connection failed:", error)

finally:
    if "client" in globals():
        client.close()
