from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Robotics Club"
REGISTERED_EMAIL = "student@mergington.edu"
NEW_EMAIL = "new-student@mergington.edu"
TEST_ACTIVITIES = {
    ACTIVITY_NAME: {
        "description": "Build and program robots",
        "schedule": "Mondays, 3:30 PM - 4:30 PM",
        "max_participants": 3,
        "participants": [REGISTERED_EMAIL],
    }
}


@pytest.fixture
def client(monkeypatch):
    # Arrange fresh application state for each test.
    monkeypatch.setattr(app_module, "activities", deepcopy(TEST_ACTIVITIES))
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activities = deepcopy(TEST_ACTIVITIES)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_student_to_activity(client):
    # Arrange
    params = {"email": NEW_EMAIL}

    # Act
    response = client.post(f"/activities/{ACTIVITY_NAME}/signup", params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {NEW_EMAIL} for {ACTIVITY_NAME}"
    }
    activities_response = client.get("/activities")
    assert NEW_EMAIL in activities_response.json()[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_student(client):
    # Arrange
    params = {"email": REGISTERED_EMAIL}

    # Act
    response = client.post(f"/activities/{ACTIVITY_NAME}/signup", params=params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    activities_response = client.get("/activities")
    assert activities_response.json()[ACTIVITY_NAME]["participants"] == [REGISTERED_EMAIL]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{unknown_activity}/signup", params={"email": NEW_EMAIL}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_student_from_activity(client):
    # Arrange
    params = {"email": REGISTERED_EMAIL}

    # Act
    response = client.delete(f"/activities/{ACTIVITY_NAME}/signup", params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {REGISTERED_EMAIL} from {ACTIVITY_NAME}"
    }
    activities_response = client.get("/activities")
    assert activities_response.json()[ACTIVITY_NAME]["participants"] == []


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{unknown_activity}/signup", params={"email": REGISTERED_EMAIL}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_student(client):
    # Arrange
    params = {"email": NEW_EMAIL}

    # Act
    response = client.delete(f"/activities/{ACTIVITY_NAME}/signup", params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"