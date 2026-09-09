from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def restore_activity_state():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)
