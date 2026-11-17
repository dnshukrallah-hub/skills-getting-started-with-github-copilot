from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["student@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", deepcopy(activities))

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_participants = ["student@mergington.edu"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == expected_participants


def test_signup_adds_normalized_email(client):
    # Arrange
    email = " New.Student@Mergington.edu "

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == (
        "Signed up new.student@mergington.edu for Chess Club"
    )
    assert "new.student@mergington.edu" in client.get(
        "/activities"
    ).json()["Chess Club"]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = " STUDENT@MERGINGTON.EDU "

    # Act
    response = client.delete(
        "/activities/Chess%20Club/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == (
        "Unregistered student@mergington.edu from Chess Club"
    )
    assert client.get("/activities").json()["Chess Club"]["participants"] == []


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_unregistered_participant(client):
    # Arrange
    email = "not-registered@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not registered"


def test_root_redirects_to_activity_page(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location
