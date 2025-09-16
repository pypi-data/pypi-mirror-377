from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from loguru import logger
from pydantic_settings import BaseSettings
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import ServerSelectionTimeoutError


class MongoDBConfig(BaseSettings):
    uri: str = "mongodb://root:example@localhost:27017/flagship_db?authSource=admin"
    db: str = "flagship_db"
    collection: str = "flags"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class MongoDBAsyncClient:
    def __init__(
        self,
        config: MongoDBConfig | None = None,
        client: AsyncMongoClient | None = None,  # type: ignore
    ):
        self.config = config or MongoDBConfig()
        self._client = client or AsyncMongoClient

    @asynccontextmanager
    async def get_client(
        self,
    ) -> AsyncGenerator[AsyncMongoClient | None | type[AsyncMongoClient], Any]:  # type: ignore
        try:
            await self.connect()
            yield self._client

        finally:
            await self.close()

    async def _collection_check(self) -> None:
        db = self._client[self.config.db]
        existing_collections = await db.list_collection_names()
        if self.config.collection not in existing_collections:
            await db.create_collection(self.config.collection)
            logger.info(f"Collection '{self.config.collection}' created.")
        else:
            logger.info(f"Collection '{self.config.collection}' already exists.")

    async def connect(self) -> None:
        """
        PyMongoDB uses connection pooling by default. When you create a MongoClient instance,
        https://pymongo.readthedocs.io/en/stable/faq.html#how-does-connection-pooling-work-in-pymongo
        Spawning a subprocess:
        https://pymongo.readthedocs.io/en/stable/faq.html#using-pymongo-with-multiprocessing
        """
        logger.warning("Trying to connect to MongoDB...")
        try:
            self._client = self._client(self.config.uri, tz_aware=True)  # type: ignore
            await self._client.admin.command("ping")
            logger.success(f"Connected successfully to MongoDB with uri: {self.config.uri}")
        except ServerSelectionTimeoutError as error:
            logger.error(f"Could not connect to MongoDB: {error}")
            self._client = None  # type: ignore
            raise ConnectionError("Failed to connect to MongoDB") from None

        await self._collection_check()

    async def close(self) -> None:
        if self._client:
            await self._client.close()  # type: ignore
            logger.info("MongoDB connection closed")

    # @TODO handle this better, we should check if the client is connected before returning the collection

    def get_flags_collection(self) -> AsyncCollection[Any]:
        if self._client:
            db = self._client[self.config.db]
            return db[self.config.collection]  # type: ignore
        else:
            logger.error("MongoDB client is not connected.")
            return None  # type: ignore
