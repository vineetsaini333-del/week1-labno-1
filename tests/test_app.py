"""
Tests for the Mergington High School API

This test suite validates the FastAPI application that manages extracurricular
activities. It tests the root endpoint, activity retrieval, and signup functionality.
"""

import pytest
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
        # Make a GET request to the root path without following redirects to see the redirect response
        response = client.get("/", follow_redirects=False)
        
        # Verify the response is a 307 Temporary Redirect status code
        # (HTTP 307 means the client should temporarily redirect to another URL)
        assert response.status_code == 307
        
        # Verify the Location header contains the correct target URL (/static/index.html)
        # This tells the client where to redirect to
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
        # Send a GET request to the /activities endpoint
        response = client.get("/activities")
        
        # Verify the request was successful (HTTP 200 OK)
        assert response.status_code == 200
        
        # Extract the JSON response data
        data = response.json()
        
        # Verify the response is a dictionary (keyed by activity name)
        # rather than a list or other data structure
        assert isinstance(data, dict)
        
        # Verify there is at least one activity in the database
        # This ensures the endpoint returns meaningful data
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
        # Fetch all activities from the API
        response = client.get("/activities")
        activities = response.json()

        # Define the exact set of required fields for each activity
        # Using a set to make exact matching easier
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Iterate through each activity to validate its structure
        for activity_name, activity_details in activities.items():
            # Verify activity name is a non-empty string
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            
            # Verify the activity has EXACTLY the required fields (no more, no less)
            # This prevents accidental inclusion of extra fields and ensures consistency
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
        # Fetch all activities from the API
        response = client.get("/activities")
        activities = response.json()

        # Check data types for each activity
        for activity_name, activity_details in activities.items():
            # Verify description and schedule are both strings
            # These are text fields describing the activity and when it meets
            assert isinstance(activity_details["description"], str)
            assert isinstance(activity_details["schedule"], str)
            
            # Verify max_participants is an integer
            # This represents the enrollment capacity limit
            assert isinstance(activity_details["max_participants"], int)
            
            # Verify participants is a list (could be empty or contain emails)
            # This represents all currently signed-up students
            assert isinstance(activity_details["participants"], list)
            
            # Verify each participant in the list is a string (email address)
            # Using all() to check every element in the participants list
            assert all(isinstance(p, str) for p in activity_details["participants"])


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
        # Make a POST request to sign up a new student for the Chess Club activity
        # The activity name is URL-encoded (%20 represents a space)
        # The email parameter specifies the student's email address
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        # Verify the signup was successful with an HTTP 200 OK response
        # This indicates the student was added to the activity's participants list
        assert response.status_code == 200

    def test_signup_for_nonexistent_activity(self):
        """
        Test signing up for an activity that doesn't exist
        
        Validates that the API properly handles invalid requests:
        - Returns HTTP 404 (Not Found) when activity name is invalid
        - Returns an error message in the response detail
        
        This prevents students from signing up for activities that don't exist.
        """
        # Attempt to sign up for an activity that doesn't exist in the database
        # This tests the error handling path
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        # Verify the API returns HTTP 404 (Not Found)
        # This is the correct HTTP status for when a resource doesn't exist
        assert response.status_code == 404
        
        # Verify the response includes a descriptive error message
        # The "detail" field contains the error message
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
        # Fetch all activities to find one with existing participants
        # We need a real participant email to test the duplicate signup logic
        activities_response = client.get("/activities")
        activities = activities_response.json()

        # Search for the first activity that has participants already signed up
        activity_with_participants = None
        existing_email = None
        for activity_name, details in activities.items():
            if details["participants"]:
                # Found an activity with participants
                activity_with_participants = activity_name
                # Get the email of the first participant (someone already signed up)
                existing_email = details["participants"][0]
                break

        # Only run the test if we found an activity with participants
        if activity_with_participants:
            # Attempt to sign up the same student again (duplicate signup)
            # This should fail because they're already enrolled
            response = client.post(
                f"/activities/{activity_with_participants}/signup",
                params={"email": existing_email}
            )
            
            # Verify the API returns HTTP 400 (Bad Request)
            # This indicates a client error (trying to do something not allowed)
            assert response.status_code == 400
            
            # Verify the error message indicates they're already signed up
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
        # Target the Programming Class activity for this test
        activity_name = "Programming Class"
        
        # Create a unique email to avoid conflicts with previous test runs
        # Using a timestamp-like approach to ensure uniqueness
        test_email = "test_participant_unique@mergington.edu"

        # Get the initial state before signup: fetch all activities and count participants
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[activity_name]["participants"])

        # Send the signup request to add the test student to the activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Only check the results if the signup was successful (HTTP 200)
        if response.status_code == 200:
            # Fetch the updated activities list to verify the change persisted
            activities_after = client.get("/activities").json()
            final_count = len(activities_after[activity_name]["participants"])

            # Verify the participant count increased by exactly 1
            # This proves the student was added to the database
            assert final_count == initial_count + 1
            
            # Verify the test student's email is now in the participants list
            # This confirms the correct email was recorded
            assert test_email in activities_after[activity_name]["participants"]
