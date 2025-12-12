#!/usr/bin/env python3
"""
Init DB script — creates essential indexes for master_db.

Usage:
  MONGO_URI and MASTER_DB are read from env or defaults used.
  Example:
    MONGO_URI=mongodb://localhost:27017 MASTER_DB=master_db python scripts/init_db.py
"""

import os
import sys
from pymongo import MongoClient, ASCENDING
from pymongo.errors import OperationFailure

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MASTER_DB = os.getenv("MASTER_DB", "master_db")

def main():
    print(f"Connecting to MongoDB at {MONGO_URI}, DB: {MASTER_DB}")
    client = MongoClient(MONGO_URI)
    db = client[MASTER_DB]

    try:
        print("Creating unique index on organizations.name ...")
        db["organizations"].create_index([("name", ASCENDING)], unique=True)
    except OperationFailure as e:
        print("Warning: could not create organizations.name index:", e)

    try:
        print("Creating unique index on admins.email ...")
        db["admins"].create_index([("email", ASCENDING)], unique=True)
    except OperationFailure as e:
        print("Warning: could not create admins.email index:", e)

    print("Indexes created (or already exist).")
    client.close()

if __name__ == "__main__":
    main()
