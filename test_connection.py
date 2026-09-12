"""
Test that your MongoDB Atlas cluster is reachable from Python.
Run: python test_connection.py

IMPORTANT: Never hardcode your real password in a file you commit to
GitHub. This file reads it from an environment variable instead.
Before running, set it in PowerShell like this (one time per session):

    $env:MONGO_URI = "mongodb+srv://shahjahnvi02_db_user:<NEW_PASSWORD>@cluster0.pzh5xa3.mongodb.net/?appName=Cluster0"

Then run: python test_connection.py
"""

import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = os.environ.get("MONGO_URI")

if not uri:
    print("MONGO_URI environment variable not set. See instructions at top of this file.")
    exit(1)

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Connected successfully to MongoDB Atlas!")
    print("Databases available:", client.list_database_names())
except Exception as e:
    print("Connection failed:", e)
