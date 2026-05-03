from fastapi.testclient import TestClient

from src.app import app


# Shared FastAPI test client for backend endpoint tests.
def _create_client() -> TestClient:
    return TestClient(app)


import pytest


@pytest.fixture
def client() -> TestClient:
    return _create_client()
