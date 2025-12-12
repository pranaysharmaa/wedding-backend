import re
from pymongo import MongoClient
from .config import settings
import time
from pymongo.errors import ServerSelectionTimeoutError

_client: MongoClient | None = None
_master_db = None


def get_client():
    global _client
    if _client is None:
        for i in range(5):
            try:
                _client = MongoClient(str(settings.MONGO_URI), serverSelectionTimeoutMS=5000)
                _client.admin.command("ping")
                break
            except ServerSelectionTimeoutError:
                time.sleep(1)
        else:
            raise RuntimeError("Could not connect to MongoDB")
    return _client

"""
def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(str(settings.MONGO_URI))
    return _client
"""

def get_master_db():
    global _master_db
    if _master_db is None:
        _master_db = get_client()[settings.MASTER_DB]
    return _master_db


def sanitize_org_name(org_name: str) -> str:
    """
    Convert org name into a safe collection suffix:
    - lowercase
    - replace non-alnum with underscore
    - trim underscores
    """
    s = org_name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"^_+|_+$", "", s)
    return s or "org_default"


def tenant_collection_name(org_name: str) -> str:
    return f"org_{sanitize_org_name(org_name)}"


def create_tenant_collection(org_name: str):
    """
    Creates a tenant collection if not exists.
    Returns the collection object.
    """
    client = get_client()
    db = client[settings.MASTER_DB]  # using master_db for meta, tenants may use same server
    coll_name = tenant_collection_name(org_name)
    # creating collection explicitly (Mongo creates lazily on first insert otherwise)
    if coll_name not in db.list_collection_names():
        db.create_collection(coll_name)
    return db[coll_name]


def delete_tenant_collection(org_name: str):
    coll_name = tenant_collection_name(org_name)
    db = get_master_db()
    if coll_name in db.list_collection_names():
        db.drop_collection(coll_name)
        return True
    return False
