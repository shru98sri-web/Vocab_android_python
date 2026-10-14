from pymongo import MongoClient

# Replace with your actual Atlas connection string and password
CONNECTION_STRING = "mongodb+srv://<username>:<password>@cluster0.8sr6god.mongodb.net/?appName=Cluster0"

# Initialize the client
client = MongoClient(CONNECTION_STRING)

# Select database and collection
db = client["test_database"]
collection = db["test_collection"]

# Insert a sample document
sample_data = {"name": "Alice", "role": "Developer", "location": "Chennai"}
result = collection.insert_one(sample_data)

print(f"Data inserted with ID: {result.inserted_id}")

# Fetch and print documents
for doc in collection.find():
    print(doc)
