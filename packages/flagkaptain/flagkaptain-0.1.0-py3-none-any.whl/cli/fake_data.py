"""
Create and store some fake data for testing purposes.
"""

import asyncio

from faker import Faker
from loguru import logger

from src.clients.mongo_db_client import MongoDBAsyncClient
from src.domain.flag import Flag
from src.repo.doc_store import DocStoreRepo


def create_fake_flags(num_flags: int = 10) -> list[Flag]:
    """
    Create a list of fake Flag objects.
    """
    fake = Faker()
    flags = []
    for _ in range(num_flags):
        flag = Flag(
            name=fake.word(),
            desc=fake.sentence(),
            value=fake.boolean(),
            date_created=fake.date_time(),
            date_updated=fake.date_time(),
            expiration_date=fake.date_time() if fake.boolean(chance_of_getting_true=50) else None,
        )
        flags.append(flag)
    return flags


def store_fake_flags(flags: list[Flag]) -> None:
    """
    Store a list of Flag objects in the specified MongoDB collection.
    """
    logger.info("Storing fake flags in MongoDB...")

    async def _store() -> None:
        mongo_client = MongoDBAsyncClient()
        await mongo_client.connect()
        store = DocStoreRepo(client=mongo_client)
        for flag in flags:
            await store.store(flag)

    asyncio.run(_store())
    logger.info("Finished storing fake flags.")


def clean_collection() -> None:
    """
    Clean the MongoDB collection by removing all documents.
    """
    logger.info("Cleaning MongoDB collection...")

    async def _clean() -> None:
        mongo_client = MongoDBAsyncClient()
        await mongo_client.connect()
        repo = DocStoreRepo(client=mongo_client)
        await repo.delete_all()

    asyncio.run(_clean())
    logger.info("Finished cleaning MongoDB collection.")


if __name__ == "__main__":
    clean_collection()
    fake_flags = create_fake_flags(num_flags=10)
    store_fake_flags(flags=fake_flags)
