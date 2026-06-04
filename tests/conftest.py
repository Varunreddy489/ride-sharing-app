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
