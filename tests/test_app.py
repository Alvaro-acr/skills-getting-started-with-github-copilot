import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as activities_data

client = TestClient(app)

INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": [],
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
        "max_participants": 22,
        "participants": [],
    },
    "Art Club": {
        "description": "Explore painting, drawing, and other artistic mediums",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 10,
        "participants": [],
    },
    "Drama Club": {
        "description": "Act in plays and improve theatrical skills",
        "schedule": "Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": [],
    },
    "Debate Club": {
        "description": "Practice argumentation and public speaking",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 15,
        "participants": [],
    },
    "Science Club": {
        "description": "Conduct experiments and learn about science",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": [],
    },
}


@pytest.fixture(autouse=True)
def reset_activities():
    activities_data.clear()
    activities_data.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities_returns_available_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_creates_new_participant():
    # Arrange
    email = "newstudent1@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == f"Signed up {email} for {activity_name}"

    response = client.get("/activities")
    data = response.json()
    assert email in data[activity_name]["participants"]


def test_signup_duplicate_returns_bad_request():
    # Arrange
    email = "duplicate@mergington.edu"
    activity_name = "Programming Class"

    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    body = response.json()
    assert "Student already signed up for this activity" in body["detail"]


def test_signup_invalid_activity_returns_not_found():
    # Arrange
    email = "teststudent@mergington.edu"
    activity_name = "Nonexistent Activity"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    body = response.json()
    assert "Activity not found" in body["detail"]


def test_unregister_removes_participant():
    # Arrange
    email = "removeme@mergington.edu"
    activity_name = "Gym Class"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == f"Unregistered {email} from {activity_name}"

    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity_name]["participants"]


def test_unregister_not_signed_up_returns_bad_request():
    # Arrange
    email = "notinsignups@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    body = response.json()
    assert "Student not signed up for this activity" in body["detail"]


def test_unregister_invalid_activity_returns_not_found():
    # Arrange
    email = "teststudent@mergington.edu"
    activity_name = "Unknown Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    body = response.json()
    assert "Activity not found" in body["detail"]
