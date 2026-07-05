import asyncio
import os
import sys

# Set Windows event loop policy BEFORE any async imports
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Set test environment variables BEFORE importing db_manager
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5433")

import pytest
import pytest_asyncio

from src.shared.db.db_manager import async_session_factory
from tests.utils.data_utils import DataUtils


@pytest.fixture
def user_register_data():
    data_utils = DataUtils()
    return dict(
        name=data_utils.gen_random_name(),
        email=data_utils.gen_random_email(),
        phone_number=data_utils.gen_phone_number(),
        password=data_utils.gen_password(),
    )


@pytest_asyncio.fixture
async def db_session():
    async with async_session_factory() as session:
        yield session
