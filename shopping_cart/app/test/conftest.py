import pytest
from dotenv import load_dotenv
import os

load_dotenv(".env.test",override=True)

@pytest.fixture(scope="session",autouse=True)
def show_test_db():
    print("Using test DB:",os.getenv("TEST_DATABASE_URL"))