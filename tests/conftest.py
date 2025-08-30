import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import os
import sys

# Add project root to path to allow imports from the main application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables for testing
os.environ['ENV'] = 'pytest'
os.environ['ALTCHA_HMAC_KEY'] = 'test-key'
# Use an in-memory SQLite DB for tests
os.environ['DATABASE_URL'] = "sqlite:///./test.db"


from infrastructure.database import Base, get_db, engine, TestingSessionLocal
from infrastructure.web.app import app, get_current_user
from infrastructure.web.auth import oauth2_scheme, TokenData

# Async test setup
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def override_get_current_user():
    # This will be replaced by set_current_user in tests that need to switch users
    return TokenData(username="default_test_user")

@pytest_asyncio.fixture
async def client():
    """A fixture that provides an async test client for the application."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[oauth2_scheme] = lambda: "fake-token"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides = {}

@pytest_asyncio.fixture(scope="function", autouse=True)
def create_test_database(client: AsyncClient):
    """
    A fixture that creates all database tables before each test
    and drops them after.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """A session-scoped fixture to clean up the testing database file."""
    def remove_db_file():
        db_path = "./test.db"
        if os.path.exists(db_path):
            os.remove(db_path)
    request.addfinalizer(remove_db_file)
