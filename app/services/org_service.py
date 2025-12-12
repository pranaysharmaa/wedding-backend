from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException, status
from ..database import get_master_db, tenant_collection_name, create_tenant_collection, sanitize_org_name
from ..utils.hashing import hash_password
from bson import ObjectId

class OrgService:
    MASTER_ORG_COLL = "organizations"
    MASTER_ADMIN_COLL = "admins"

    @classmethod
    def create_org(cls, org_name: str, email: str, password: str) -> dict:
        db = get_master_db()
        orgs = db[cls.MASTER_ORG_COLL]
        admins = db[cls.MASTER_ADMIN_COLL]

        # ensure unique org name (case-insensitive)
        if orgs.find_one({"name": {"$regex": f"^{org_name}$", "$options": "i"}}):
            raise HTTPException(status_code=400, detail="Organization already exists")

        coll_name = tenant_collection_name(org_name)
        create_tenant_collection(org_name)

        hashed = hash_password(password)
        admin_doc = {
            "email": email,
            "password": hashed,
            "org": org_name
        }
        try:
            admin_res = admins.insert_one(admin_doc)
        except DuplicateKeyError:
            raise HTTPException(status_code=400, detail="Admin email already used")

        org_doc = {
            "name": org_name,
            "collection": coll_name,
            "admin_id": str(admin_res.inserted_id)
        }
        org_res = orgs.insert_one(org_doc)

        return {
            "name": org_doc["name"],
            "collection": org_doc["collection"],
            "admin_email": email,
            "org_id": str(org_res.inserted_id)
        }

    @classmethod
    def get_org_by_name(cls, org_name: str) -> dict | None:
        db = get_master_db()
        orgs = db[cls.MASTER_ORG_COLL]
        org = orgs.find_one({"name": {"$regex": f"^{org_name}$", "$options": "i"}})
        if not org:
            return None
        # fetch admin email by admin_id
        admin_email = None
        admin_id = org.get("admin_id")
        if admin_id:
            try:
                admin_doc = db[cls.MASTER_ADMIN_COLL].find_one({"_id": ObjectId(admin_id)})
                if admin_doc:
                    admin_email = admin_doc.get("email")
            except Exception:
                admin_email = None
        return {
            "name": org["name"],
            "collection": org["collection"],
            "admin_email": admin_email,
            "admin_id": org.get("admin_id")
        }

    @classmethod
    def update_org_name(cls, current_name: str, new_name: str) -> dict:
        """
        Rename org from current_name to new_name:
        - Validate not conflicting
        - Create new tenant collection (copy documents)
        - Update master org doc (name & collection)
        - Update admins' org field pointing to new name
        - Drop old tenant collection
        """
        db = get_master_db()
        orgs = db[cls.MASTER_ORG_COLL]
        admins = db[cls.MASTER_ADMIN_COLL]

        # find existing org
        org = orgs.find_one({"name": {"$regex": f"^{current_name}$", "$options": "i"}})
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        # check new name not used
        if orgs.find_one({"name": {"$regex": f"^{new_name}$", "$options": "i"}}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New organization name already exists")

        old_coll = org["collection"]
        new_coll = tenant_collection_name(new_name)

        # create new collection and copy docs (safe copy)
        src_coll = db[old_coll]
        if new_coll in db.list_collection_names():
            # shouldn't happen, but avoid overwrite
            raise HTTPException(status_code=400, detail="Target collection already exists")

        db.create_collection(new_coll)
        dest_coll = db[new_coll]

        # Bulk copy in chunks
        cursor = src_coll.find({})
        batch = []
        BATCH_SIZE = 500
        count = 0
        for doc in cursor:
            # remove _id to let Mongo create new ids
            doc.pop("_id", None)
            batch.append(doc)
            if len(batch) >= BATCH_SIZE:
                dest_coll.insert_many(batch)
                count += len(batch)
                batch = []
        if batch:
            dest_coll.insert_many(batch)
            count += len(batch)

        # update master org doc
        orgs.update_one({"_id": org["_id"]}, {"$set": {"name": new_name, "collection": new_coll}})

        # update admins who had org reference
        admins.update_many({"org": org["name"]}, {"$set": {"org": new_name}})

        # drop old collection
        db.drop_collection(old_coll)

        return {"old_name": org["name"], "new_name": new_name, "new_collection": new_coll, "moved_docs": count}

    @classmethod
    def delete_org(cls, org_name: str) -> dict:
        """
        Deletes an organization and its tenant collection and admins.
        """
        db = get_master_db()
        orgs = db[cls.MASTER_ORG_COLL]
        admins = db[cls.MASTER_ADMIN_COLL]

        org = orgs.find_one({"name": {"$regex": f"^{org_name}$", "$options": "i"}})
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        # delete tenant collection
        coll = org.get("collection")
        if coll and coll in db.list_collection_names():
            db.drop_collection(coll)

        # remove admins for that org
        admins.delete_many({"org": org["name"]})

        # remove org doc
        orgs.delete_one({"_id": org["_id"]})

        return {"deleted": True, "org": org["name"]}
