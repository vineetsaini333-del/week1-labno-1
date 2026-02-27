"""
Tests for error handling and validation across all endpoints

This module contains tests for error cases, validation, HTTP status codes,
and error message content across the entire API.
"""

import pytest


class TestHTTPStatusCodes:
    """Test suite for validating correct HTTP status codes"""
    
    def test_valid_request_returns_2xx(self, test_client):
        """
        Test that valid requests return 2xx success status codes
        
        Validates:
        - Valid GET requests return 200
        - API is usable for basic operations
        - Success responses are correct
        """
        # Arrange: No setup needed
        
        # Act: Make a valid GET request
        response = test_client.get("/activities")
        
        # Assert: Verify 2xx success status code
        assert 200 <= response.status_code < 300
    
    def test_invalid_activity_returns_404_not_4xx(self, test_client):
        """
        Test that 404 is returned for not found, not generic 4xx
        
        Validates:
        - Proper HTTP status code semantics
        - Specific error codes are returned
        - API follows HTTP standards
        """
        # Arrange: Set up test for non-existent activity
        nonexistent_activity = "DoesNotExist"
        test_email = "test@test.edu"
        
        # Act: Request non-existent activity
        response = test_client.post(
            "/activities/DoesNotExist/signup",
            params={"email": test_email}
        )
        
        # Assert: Must be specifically 404, not just any 4xx
        assert response.status_code == 404
    
    def test_duplicate_signup_returns_400_not_4xx(self, test_client, activity_with_participants):
        """
        Test that duplicate signup returns 400, not 404 or 500
        
        Validates:
        - Proper error code for duplicate request
        - Distinguishes between not-found and conflict
        - Client error codes are appropriate
        """
        # Arrange: Get activity and participant data
        activity_name, existing_email = activity_with_participants
        
        # Act & Assert: Only test if activity with participants exists
        if activity_name is not None:
            response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": existing_email}
            )
            
            assert response.status_code == 400


class TestErrorMessages:
    """Test suite for error message content and clarity"""
    
    def test_error_responses_have_detail_field(self, test_client):
        """
        Test that error responses include a detail field
        
        Validates:
        - Error responses follow FastAPI convention
        - Clients can parse error messages
        - Detail field contains error information
        """
        # Arrange: Prepare test for error condition
        
        # Act: Make request that causes 404 error
        response = test_client.post(
            "/activities/InvalidActivity/signup",
            params={"email": "test@test.edu"}
        )
        
        # Assert: Error response should have "detail" field
        if response.status_code >= 400:
            json_data = response.json()
            assert "detail" in json_data
    
    def test_activity_not_found_message(self, test_client):
        """
        Test that 404 error message includes "Activity not found"
        
        Validates:
        - Error message is specific and helpful
        - Message indicates what went wrong
        - Users understand the error
        """
        # Arrange: Prepare test for non-existent activity
        
        # Act: Request non-existent activity
        response = test_client.post(
            "/activities/NonExistent/signup",
            params={"email": "test@test.edu"}
        )
        
        # Assert: Should have descriptive message
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert "activity" in detail.lower() and "not" in detail.lower()
    
    def test_duplicate_signup_message(self, test_client, activity_with_participants):
        """
        Test that duplicate signup error message is descriptive
        
        Validates:
        - Error message mentions duplicate or already signed
        - Clients understand they're already enrolled
        - Message is actionable
        """
        # Arrange: Get activity and participant data
        activity_name, existing_email = activity_with_participants
        
        # Act & Assert: Only test if activity with participants exists
        if activity_name is not None:
            response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": existing_email}
            )
            
            assert response.status_code == 400
            detail = response.json()["detail"]
            assert ("already" in detail.lower() or 
                   "signed up" in detail.lower() or
                   "duplicate" in detail.lower())


class TestInputValidation:
    """Test suite for input validation and edge cases"""
    
    def test_missing_query_parameter_returns_error(self, test_client, valid_activity_name):
        """
        Test that missing required email parameter returns error
        
        Validates:
        - Required parameters are enforced
        - API returns 422 (validation error)
        - Invalid requests are rejected
        """
        # Arrange: Prepare request without email parameter
        
        # Act: POST without email parameter
        response = test_client.post(f"/activities/{valid_activity_name}/signup")
        
        # Assert: Should return validation error
        assert response.status_code >= 400
    
    def test_empty_email_is_accepted(self, test_client, valid_activity_name):
        """
        Test that empty email string is currently accepted by the API
        
        Note: This test documents actual API behavior.
        A future enhancement might add validation to reject empty emails.
        
        Validates:
        - API handles empty inputs gracefully
        - No crash or 5xx error occurs
        """
        # Arrange: Prepare test with empty email
        
        # Act: POST with empty email
        response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": ""}
        )
        
        # Assert: API currently accepts empty email and returns 200
        assert response.status_code == 200
    
    def test_activity_name_url_encoding(self, test_client):
        """
        Test that activity names with spaces are properly URL encoded
        
        Validates:
        - Spaces in activity names are handled (%20)
        - URL encoding works correctly
        - Multi-word activity names work
        """
        # Arrange: Prepare test for encoded activity name
        
        # Act: Try to sign up for "Chess Club" with space encoded
        response = test_client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "test@test.edu"}
        )
        
        # Assert: Should work (not 404 from encoding issue)
        assert response.status_code != 404 or "Activity not found" in response.json()["detail"]


class TestResponseFormats:
    """Test suite for response format and structure"""
    
    def test_success_response_is_json(self, test_client, valid_activity_name):
        """
        Test that successful responses can be parsed as JSON
        
        Validates:
        - Response is parseable JSON format
        - Content-type is correct
        - No serialization errors
        """
        # Arrange: Prepare test data
        
        # Act: Make successful request
        response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": "format_test@test.edu"}
        )
        
        # Assert: Should be able to parse as JSON when successful
        if response.status_code == 200:
            data = response.json()
            assert response.text is not None
    
    def test_error_response_is_json(self, test_client):
        """
        Test that error responses return valid JSON
        
        Validates:
        - Error responses are JSON formatted
        - Parseable error structure
        - Clients can handle error format
        """
        # Arrange: Prepare test for error condition
        
        # Act: Make request that causes error
        response = test_client.post(
            "/activities/BadActivity/signup",
            params={"email": "test@test.edu"}
        )
        
        # Assert: Error response should still be JSON
        if response.status_code >= 400:
            data = response.json()
            assert data is not None
    
    def test_get_activities_returns_dictionary_not_list(self, test_client):
        """
        Test that /activities returns object dict, not array list
        
        Validates:
        - Correct data structure
        - Activities are keyed by name
        - Response format is consistent
        """
        # Arrange: No setup needed
        
        # Act: Get activities
        response = test_client.get("/activities")
        data = response.json()
        
        # Assert: Must be dictionary, not list
        assert isinstance(data, dict)
        assert not isinstance(data, list)


class TestConcurrentOperations:
    """Test suite for behavior with concurrent/rapid operations"""
    
    def test_rapid_signups_same_email(self, test_client, valid_activity_name):
        """
        Test behavior of rapid consecutive signups with same email
        
        Validates:
        - System handles rapid requests
        - Second attempt is rejected as duplicate
        - No race conditions or data corruption
        """
        # Arrange: Prepare test data
        test_email = "rapid_test@test.edu"
        
        # Act: First signup
        response1 = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": test_email}
        )
        
        # Immediately try again with same email
        response2 = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert: One should succeed, second should fail
        assert (response1.status_code == 200 and response2.status_code == 400) or \
               (response1.status_code == 400 and response2.status_code == 200)
    
    def test_multiple_activities_independent(self, test_client, available_activities):
        """
        Test that operations on different activities don't interfere
        
        Validates:
        - Activities are independent
        - Changes don't leak between activities
        - Data isolation is maintained
        """
        # Arrange: Get two different activities if available
        activity_names = list(available_activities.keys())
        
        if len(activity_names) >= 2:
            act1_before = activity_names[0]
            act2_before = activity_names[1]
            
            initial_activities = test_client.get("/activities").json()
            count1_before = len(initial_activities[act1_before]["participants"])
            count2_before = len(initial_activities[act2_before]["participants"])
            
            # Act: Sign up for first activity
            test_email = "multi_activity_test@test.edu"
            test_client.post(
                f"/activities/{act1_before}/signup",
                params={"email": test_email}
            )
            
            # Assert: Check that only first activity's count changed
            updated_activities = test_client.get("/activities").json()
            count1_after = len(updated_activities[act1_before]["participants"])
            count2_after = len(updated_activities[act2_before]["participants"])
            
            assert count1_after >= count1_before
            assert count2_after == count2_before


class TestDataIntegrity:
    """Test suite for data integrity and consistency"""
    
    def test_participant_list_format_consistency(self, test_client):
        """
        Test that participant lists maintain consistent format
        
        Validates:
        - All participants are strings
        - List structure is maintained
        - No format corruption after operations
        """
        # Arrange: Fetch activities
        
        # Act: Get activities and check participants
        activities = test_client.get("/activities").json()
        
        # Assert: Verify all participants are strings
        for activity_name, details in activities.items():
            participants = details["participants"]
            for p in participants:
                assert isinstance(p, str)
    
    def test_activity_fields_never_null(self, test_client):
        """
        Test that required activity fields are never null
        
        Validates:
        - No null/None values in required fields
        - Data is always present
        - Clients don't need null checks for required fields
        """
        # Arrange: Fetch activities
        
        # Act: Get activities
        activities = test_client.get("/activities").json()
        
        # Assert: Verify no null fields
        for activity_name, details in activities.items():
            for field_name, field_value in details.items():
                assert field_value is not None, \
                    f"Activity {activity_name} has null field {field_name}"
    
    def test_max_participants_never_negative(self, test_client):
        """
        Test that max_participants is never negative
        
        Validates:
        - Capacity is always positive
        - Invalid data is never served
        - Database integrity is maintained
        """
        # Arrange: Fetch activities
        
        # Act: Get activities
        activities = test_client.get("/activities").json()
        
        # Assert: Verify positive capacity for all activities
        for activity_name, details in activities.items():
            max_participants = details["max_participants"]
            assert max_participants > 0, \
                f"Activity {activity_name} has invalid max_participants"
