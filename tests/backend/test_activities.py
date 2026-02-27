"""
Tests for the /activities endpoint

This module tests the GET /activities endpoint which retrieves
all available activities and their details.
"""

import pytest


class TestActivitiesEndpoint:
    """Test suite for the /activities GET endpoint"""
    
    def test_activities_endpoint_returns_200(self, test_client):
        """
        Test that /activities returns HTTP 200 OK
        
        Validates:
        - The endpoint is accessible
        - The request is successful
        - No server errors occur
        """
        # Arrange: No setup needed - endpoint is always available
        
        # Act: Make a GET request to the activities endpoint
        response = test_client.get("/activities")
        
        # Assert: Verify HTTP 200 response
        assert response.status_code == 200
    
    def test_activities_endpoint_returns_dict(self, test_client):
        """
        Test that /activities returns data as a dictionary (object)
        
        Validates:
        - Response is not a list or array
        - Activities are keyed by name (not in array form)
        - Data structure matches API contract
        """
        # Arrange: No setup needed
        
        # Act: Make the request and get JSON data
        response = test_client.get("/activities")
        data = response.json()
        
        # Assert: Verify response is a dictionary
        assert isinstance(data, dict)
    
    def test_activities_endpoint_has_content(self, test_client):
        """
        Test that /activities returns at least one activity
        
        Validates:
        - Database is not empty
        - Endpoint returns meaningful data
        - Activities exist for students to join
        """
        # Arrange: No setup needed
        
        # Act: Get activities from API
        response = test_client.get("/activities")
        activities = response.json()
        
        # Assert: Verify activities dictionary is not empty
        assert len(activities) > 0
    
    def test_each_activity_has_name(self, available_activities):
        """
        Test that each activity has a non-empty name/key
        
        Validates:
        - Activity names are valid identifiers
        - Activity names are not empty strings
        - Activity dictionary has proper structure
        """
        # Arrange: Get available activities fixture
        
        # Act & Assert: Iterate through all activities and validate names
        for activity_name in available_activities.keys():
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
    
    def test_each_activity_has_all_fields(self, available_activities):
        """
        Test that each activity contains all required fields
        
        Validates:
        - Required fields: description, schedule, max_participants, participants
        - No missing fields
        - API contract is maintained
        - Clients can rely on consistent structure
        """
        # Arrange: Define the fields every activity must have
        required_fields = {
            "description",
            "schedule",
            "max_participants",
            "participants"
        }
        
        # Act & Assert: Check each activity
        for activity_name, details in available_activities.items():
            actual_fields = set(details.keys())
            assert actual_fields == required_fields, \
                f"Activity '{activity_name}' has fields {actual_fields}, " \
                f"expected {required_fields}"
    
    def test_description_field_is_string(self, available_activities):
        """
        Test that description field contains a non-empty string
        
        Validates:
        - Description exists and is a string
        - Description is not empty
        - Students get meaningful activity descriptions
        """
        # Arrange: Get activities fixture
        
        # Act & Assert: Check description for each activity
        for activity_name, details in available_activities.items():
            description = details["description"]
            assert isinstance(description, str), \
                f"Activity '{activity_name}' description is not a string"
            assert len(description) > 0, \
                f"Activity '{activity_name}' description is empty"
    
    def test_schedule_field_is_string(self, available_activities):
        """
        Test that schedule field contains a non-empty string
        
        Validates:
        - Schedule exists and is a string
        - Schedule is not empty
        - Students get meeting time information
        """
        # Arrange: Get activities fixture
        
        # Act & Assert: Check schedule for each activity
        for activity_name, details in available_activities.items():
            schedule = details["schedule"]
            assert isinstance(schedule, str), \
                f"Activity '{activity_name}' schedule is not a string"
            assert len(schedule) > 0, \
                f"Activity '{activity_name}' schedule is empty"
    
    def test_max_participants_is_positive_integer(self, available_activities):
        """
        Test that max_participants is a valid positive integer
        
        Validates:
        - max_participants is an integer (not float or string)
        - max_participants is positive (capacity > 0)
        - Activity capacity makes sense
        """
        # Arrange: Get activities fixture
        
        # Act & Assert: Check max_participants for each activity
        for activity_name, details in available_activities.items():
            max_participants = details["max_participants"]
            assert isinstance(max_participants, int), \
                f"Activity '{activity_name}' max_participants is not an integer"
            assert max_participants > 0, \
                f"Activity '{activity_name}' max_participants is not positive"
    
    def test_participants_is_list(self, available_activities):
        """
        Test that participants field is a list
        
        Validates:
        - participants is a list (can be empty or contain emails)
        - participants can hold multiple entries
        - Data structure supports student roster
        """
        # Arrange: Get activities fixture
        
        # Act & Assert: Check participants for each activity
        for activity_name, details in available_activities.items():
            participants = details["participants"]
            assert isinstance(participants, list), \
                f"Activity '{activity_name}' participants is not a list"
    
    def test_participants_are_strings(self, available_activities):
        """
        Test that each participant entry is a string (email address)
        
        Validates:
        - Every participant is a string
        - Likely to be email addresses
        - No invalid data types mixed in participants list
        """
        # Arrange: Get activities fixture
        
        # Act & Assert: Check each participant in each activity
        for activity_name, details in available_activities.items():
            participants = details["participants"]
            for participant in participants:
                assert isinstance(participant, str), \
                    f"Activity '{activity_name}' has non-string participant: {participant}"
    
    def test_participant_count_not_exceeds_max(self, available_activities):
        """
        Test that current participants don't exceed max capacity
        
        Validates:
        - Data consistency (no overbooking)
        - max_participants is a real limit
        - Database integrity rules are enforced
        """
        # Arrange: Get activities fixture
        
        # Act & Assert: Check participant count vs max for each activity
        for activity_name, details in available_activities.items():
            current_count = len(details["participants"])
            max_count = details["max_participants"]
            
            assert current_count <= max_count, \
                f"Activity '{activity_name}' has {current_count} participants " \
                f"but max is {max_count}"
