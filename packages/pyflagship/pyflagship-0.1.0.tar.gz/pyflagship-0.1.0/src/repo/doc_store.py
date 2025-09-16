"""
Implements a document storage repo for MongoDB.
"""

from dataclasses import asdict
from typing import Any

from src.clients.mongo_db_client import MongoDBAsyncClient
from src.domain.flag import Flag

type MongoDBDocument = dict[str, Any]


def flag_to_document(flag: Flag) -> MongoDBDocument:
    """
    Convert a Flag instance to a dictionary suitable for MongoDB storage.
    """
    doc = asdict(flag)
    doc["_id"] = doc.pop("id")
    return doc


def document_to_flag(doc: MongoDBDocument) -> Flag:
    """
    Convert a MongoDB document to a Flag instance.
    """
    return Flag(id=str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"})


class DocStoreRepo:
    def __init__(self, client: MongoDBAsyncClient | None = None) -> None:
        self._client = client or MongoDBAsyncClient()

    async def store(self, flag: Flag) -> None:
        """
        Store a new Flag document in the MongoDB collection.
        """
        coll = self._client.get_flags_collection()
        await coll.insert_one(flag_to_document(flag=flag))

    async def get_by_id(self, _id: str) -> Flag | None:
        """
        Retrieve a Flag document by its ID from the MongoDB collection.
        """
        coll = self._client.get_flags_collection()
        if document := await coll.find_one({"_id": _id}):
            return document_to_flag(doc=document)
        return None

    async def get_by_name(self, name: str) -> Flag | None:
        """
        Retrieve a Flag document by its name from the MongoDB collection.
        """
        coll = self._client.get_flags_collection()
        if document := await coll.find_one({"name": name}):
            return document_to_flag(doc=document)
        return None

    async def get_all(self, limit: int = 100) -> list[Flag]:
        """
        Retrieve all Flag documents from the MongoDB collection, up to the specified limit.
        """
        coll = self._client.get_flags_collection()
        documents = await coll.find().to_list(limit)
        flags = [document_to_flag(doc=document) for document in documents]
        return flags

    async def update(self, flag: Flag) -> bool:
        """
        Update an existing Flag document in the MongoDB collection.
        """
        collection = self._client.get_flags_collection()
        result = await collection.replace_one({"_id": str(flag.id)}, flag_to_document(flag))
        return result.modified_count > 0

    async def delete(self, _id: str) -> bool:
        """
        Delete a Flag document by its ID from the MongoDB collection.
        """
        collection = self._client.get_flags_collection()
        result = await collection.delete_one({"_id": _id})
        return result.deleted_count > 0

    async def delete_all(self) -> None:
        """
        Delete all Flag documents from the MongoDB collection.
        """
        collection = self._client.get_flags_collection()
        await collection.delete_many({})
