
import pandas as pd
import json
from pymongo import MongoClient

# Uniform Resource Identifier (URI) for connecting to the MongoDB cluster
uri = "mongodb+srv://avaneeshpathak900:03717anujP@cluster0.tszy1a8.mongodb.net/Avaneesh?retryWrites=true&w=majority"

# Create a new client and connect to the MongoDB server
client = MongoClient(uri)

# Create database name and collection name
DATABASE_NAME = 'Avaneesh'
COLLECTION_NAME = 'waferfault'

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(r"D:\sensor-fault-detection\notebooks\wafer_23012020_041211.csv")


# Convert the data into JSON format
json_records = df.to_dict(orient='records')

# Insert the JSON records into the specified collection within the database

client[DATABASE_NAME][COLLECTION_NAME].insert_many(json_records)

# Close the MongoDB connection
client.close()

client.close()