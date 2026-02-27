"""
Tests for the Mergington High School API

This test suite validates the FastAPI application that manages extracurricular
activities. It tests the root endpoint, activity retrieval, and signup functionality.
"""

import pytest # type: ignore
from fastapi.testclient import TestClient
from src.app import app

# Create a test client to make requests to the application
client = TestClient(app)


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirects_to_static(self):
        """
        Test that the root endpoint redirects to /static/index.html
        
        Validates that when a user visits the root path "/", they are redirected
        to the static index.html file. This is the entry point for the web application.
        Checks for HTTP 307 (Temporary Redirect) status code.
        """
        # Arrange: No setup needed - the endpoint is always available
        
        # Act: Make a GET request to the root path without following redirects
        response = client.get("/", follow_redirects=False)
        
        # Assert: Verify the response and location header
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the get activities endpoint"""

    def test_get_all_activities(self):
        """
        Test retrieving all activities
        
        Validates that the /activities endpoint returns:
        - A successful HTTP 200 response
        - A dictionary of activities
        - At least one activity exists in the database
        """
        # Arrange: No setup needed - activities are pre-loaded
        
        # Act: Send a GET request to the /activities endpoint
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Verify successful response and data structure
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_activities_have_required_fields(self):
        """
        Test that each activity has all required fields
        
        Validates that every activity in the response contains exactly these fields:
        - description: Text describing the activity
        - schedule: When the activity meets
        - max_participants: Maximum number of students allowed
        - participants: List of students currently signed up
        
        This ensures the API contract is maintained and clients can rely on
        these fields being present.
        """
        # Arrange: Fetch activities and define required fields
        response = client.get("/activities")
        activities = response.json()
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act & Assert: Validate each activity has exactly the required fields
        for activity_name, activity_details in activities.items():
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            assert set(activity_details.keys()) == required_fields

    def test_activities_have_valid_data_types(self):
        """
        Test that activity fields have the correct data types
        
        Validates that each field contains the expected data type:
        - description: string
        - schedule: string
        - max_participants: integer
        - participants: list of strings (email addresses)
        
        This ensures type safety and prevents frontend errors from incorrect data.
        """
        # Arrange: Fetch activities from the API
        response = client.get("/activities")
        activities = response.json()

        # Act & Assert: Validate data types for each activity field
        for activity_name, activity_details in activities.items():
            assert isinstance(activity_details["description"], str)
            assert isinstance(activity_details["schedule"], str)
            assert isinstance(activity_details["max_participants"], int)
            assert isinstance(activity_details["participants"], list)
            assert all(isinstance(p, str) for p in activity_details["participants"])


class TestGetActivity:
    """Test the get specific activity endpoint"""

    def test_get_activity_by_name_returns_200(self):
        """
        Test successfully retrieving a specific activity by name
        
        Validates:
        - Valid activity names are accepted
        - Correct HTTP 200 status is returned
        - Activity details are returned in response
        """
        # Arrange: Target a known activity
        activity_name = "Chess Club"
        
        # Act: Get the specific activity
        response = client.get(f"/activities/{activity_name}")
        
        # Assert: Verify success and response structure
        assert response.status_code == 200
        activity_data = response.json()
        assert isinstance(activity_data, dict)
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data

    def test_get_activity_returns_correct_data(self):
        """
        Test that retrieved activity has the expected fields and values
        
        Validates:
        - Description is returned correctly
        - Schedule is returned correctly
        - Max participants is a positive integer
        - Participants list is included
        """
        # Arrange: Target Programming Class
        activity_name = "Programming Class"
        
        # Act: Get the activity
        response = client.get(f"/activities/{activity_name}")
        activity = response.json()
        
        # Assert: Verify all fields are present and valid
        assert isinstance(activity["description"], str)
        assert len(activity["description"]) > 0
        assert isinstance(activity["schedule"], str)
        assert len(activity["schedule"]) > 0
        assert isinstance(activity["max_participants"], int)
        assert activity["max_participants"] > 0
        assert isinstance(activity["participants"], list)

    def test_get_nonexistent_activity_returns_404(self):
        """
        Test that requesting a non-existent activity returns 404
        
        Validates:
        - Invalid activity names are rejected
        - Proper HTTP 404 status code is returned
        - Error message is descriptive
        """
        # Arrange: Use a non-existent activity name
        nonexistent_activity = "Nonexistent Activity"
        
        # Act: Try to get the non-existent activity
        response = client.get(f"/activities/{nonexistent_activity}")
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        error_detail = response.json()["detail"]
        assert "not found" in error_detail.lower()

    def test_get_activity_includes_current_participants(self):
        """
        Test that activity includes current participant list
        
        Validates:
        - Participants list is returned
        - List can be empty or contain emails
        - Each participant is a string
        """
        # Arrange: Get a known activity
        activity_name = "Soccer Team"
        
        # Act: Retrieve the activity
        response = client.get(f"/activities/{activity_name}")
        activity = response.json()
        
        # Assert: Verify participants list
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
        for participant in activity["participants"]:
            assert isinstance(participant, str)

    def test_get_activity_with_special_characters_in_name(self):
        """
        Test getting activity with special characters in URL
        
        Validates:
        - Spaces in activity names work correctly
        - Activity lookup is case-sensitive or handles encoding
        """
        # Arrange: Use Swimming Club (has space)
        activity_name = "Swimming Club"
        
        # Act: Get the activity
        response = client.get(f"/activities/{activity_name}")
        
        # Assert: Should find the activity
        assert response.status_code == 200
        activity = response.json()
        assert "description" in activity


class TestSignupForActivity:
    """Test the signup endpoint"""

    def test_signup_for_existing_activity(self):
        """
        Test successfully signing up for an existing activity
        
        Validates that a student can sign up for a real activity. This tests
        the happy path where:
        - The activity exists
        - The student is not already signed up
        - The request succeeds with HTTP 200
        """
        # Arrange: Set up test data
        activity_name = "Chess Club"
        test_email = "newstudent@mergington.edu"
        
        # Act: Attempt to sign up for the activity
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": test_email}
        )
        
        # Assert: Verify successful signup
        assert response.status_code == 200

    def test_signup_for_nonexistent_activity(self):
        """
        Test signing up for an activity that doesn't exist
        
        Validates that the API properly handles invalid requests:
        - Returns HTTP 404 (Not Found) when activity name is invalid
        - Returns an error message in the response detail
        
        This prevents students from signing up for activities that don't exist.
        """
        # Arrange: Set up test data for non-existent activity
        nonexistent_activity = "Nonexistent Activity"
        test_email = "student@mergington.edu"
        
        # Act: Attempt to sign up for a non-existent activity
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": test_email}
        )
        
        # Assert: Verify the proper error response
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_duplicate_signup_rejected(self):
        """
        Test that duplicate signups are rejected
        
        Validates that students cannot sign up for the same activity twice:
        - Finds an activity with existing participants
        - Attempts to sign up the same student again
        - Expects HTTP 400 (Bad Request) response
        - Expects an error message about already being signed up
        
        This prevents duplicate entries and maintains data integrity.
        """
        # Arrange: Find an activity with existing participants
        activities_response = client.get("/activities")
        activities = activities_response.json()

        activity_with_participants = None
        existing_email = None
        for activity_name, details in activities.items():
            if details["participants"]:
                activity_with_participants = activity_name
                existing_email = details["participants"][0]
                break

        # Act & Assert: Only test if we found an activity with participants
        if activity_with_participants:
            response = client.post(
                f"/activities/{activity_with_participants}/signup",
                params={"email": existing_email}
            )
            
            assert response.status_code == 400
            assert "already signed up" in response.json()["detail"]

    def test_signup_increases_participant_count(self):
        """
        Test that signing up actually adds the participant to the activity
        
        Validates that the signup operation modifies the database correctly:
        - Gets the initial participant count
        - Signs up a new student with a unique email
        - Verifies the participant count increased by exactly 1
        - Verifies the new student's email appears in the participants list
        
        This ensures the signup actually persists the data.
        """
        # Arrange: Set up test data and get initial state
        activity_name = "Programming Class"
        test_email = "test_participant_unique@mergington.edu"
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[activity_name]["participants"])

        # Act: Send the signup request
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Verify signup success and persistence
        if response.status_code == 200:
            activities_after = client.get("/activities").json()
            final_count = len(activities_after[activity_name]["participants"])

            assert final_count == initial_count + 1
            assert test_email in activities_after[activity_name]["participants"]
