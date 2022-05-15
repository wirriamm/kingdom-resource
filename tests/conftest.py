from pymongo import MongoClient
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.setup import get_db, setup_indexes
from config import settings


@pytest.fixture
def get_db_for_test():
    client = MongoClient(settings.DATABASE_URL)
    if settings.TEST_DATABASE_NAME is None or settings.TEST_DATABASE_NAME == "":
        raise ValueError("TEST_DATABASE_NAME env variable missing")
    client.drop_database(settings.TEST_DATABASE_NAME)
    db = client[settings.TEST_DATABASE_NAME]
    setup_indexes(db)
    yield lambda: db  # FastAPI dependencies must be a callable
    client.drop_database(settings.TEST_DATABASE_NAME)


#
# NOTE
# When multiple t_client are called in a single test (via fixtures or otherwise),
#   they will still be calling on the same test database
#   because the t_client fixture will only tear down the db at the end of the test
#
@pytest.fixture
def t_client(get_db_for_test):
    app.dependency_overrides[get_db] = get_db_for_test
    client = TestClient(app)
    return client
