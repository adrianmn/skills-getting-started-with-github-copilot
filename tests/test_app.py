import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Copy of original activities for resetting between tests
original_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
        "max_participants": 22,
        "participants": []
    },
    "Art Club": {
        "description": "Explore various art forms and create masterpieces",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Act in plays and improve theatrical skills",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Debate Club": {
        "description": "Engage in debates and develop critical thinking",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": []
    },
    "Science Club": {
        "description": "Conduct experiments and learn about science",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": []
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    activities.clear()
    activities.update(original_activities)

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app, follow_redirects=False)

def test_root_redirect(client):
    """Test GET / redirects to static index"""
    # Arrange
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test GET /activities returns all activities"""
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # All activities present
    assert "Chess Club" in data
    assert "Programming Class" in data

    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success(client):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Basketball Team"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" == data["message"]

    # Verify participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity_name]["participants"]

def test_signup_activity_not_found(client):
    """Test signup for non-existent activity returns 404"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "test@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Activity not found"

def test_signup_already_signed_up(client):
    """Test signup when student is already signed up returns 400"""
    # Arrange
    activity_name = "Chess Club"
    email = "existing@mergington.edu"
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")
    # Act - Second signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Student already signed up for this activity"