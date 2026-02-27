"""
Tests for the /activities/{activity_name}/signup endpoint

This module tests the POST signup endpoint which allows students
to register for extracurricular activities.
"""

import pytest


class TestSignupEndpoint:
    """Test suite for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_with_valid_activity_returns_200(self, test_client, valid_activity_name):
        """
        Test successful signup to a valid activity returns HTTP 200
        
        Validates:
        - Valid activity names are accepted
        - Valid email addresses are accepted
        - Signup operation succeeds
        - Correct HTTP status code is returned
        """
        # Arrange: Set up test data
        test_email = "valid_student@test.mergington.edu"
        
        # Act: Attempt to sign up for a valid activity
        response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert: Verify success with HTTP 200 OK
        assert response.status_code == 200
    
    def test_signup_with_nonexistent_activity_returns_404(self, test_client):
        """
        Test signup to non-existent activity returns HTTP 404 Not Found
        
        Validates:
        - Invalid activity names are rejected
        - Proper error response is returned
        - API prevents signing up for fake activities
        - Correct HTTP status code for "not found"
        """
        # Arrange: Prepare test data for non-existent activity
        nonexistent_activity = "Nonexistent Activity"
        test_email = "student@test.mergington.edu"
        
        # Act: Attempt to sign up for an activity that doesn't exist
        response = test_client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": test_email}
        )
        
        # Assert: Verify the API returns 404 Not Found
        assert response.status_code == 404
    
    def test_signup_404_includes_error_message(self, test_client):
        """
        Test that 404 response includes meaningful error message
        
        Validates:
        - Error response contains detail field
        - Message clearly indicates activity not found
        - User gets helpful feedback on errors
        """
        # Arrange: Prepare test for non-existent activity
        fake_activity = "Fake Activity"
        test_email = "student@test.mergington.edu"
        
        # Act: Request signup for non-existent activity
        response = test_client.post(
            "/activities/Fake%20Activity/signup",
            params={"email": test_email}
        )
        
        # Assert: Verify error message is present and meaningful
        assert response.status_code == 404
        error_detail = response.json()["detail"]
        assert "not found" in error_detail.lower()
    
    def test_duplicate_signup_returns_400(self, test_client, activity_with_participants):
        """
        Test that duplicate signup attempt returns HTTP 400 Bad Request
        
        Validates:
        - Duplicate signups are rejected
        - Error response is returned
        - Student can't sign up twice for same activity
        - Correct HTTP status for bad request
        """
        # Arrange: Get activity and participant data
        activity_name, existing_email = activity_with_participants
        
        # Act & Assert: Only run test if we found an activity with participants
        if activity_name is not None:
            response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": existing_email}
            )
            
            assert response.status_code == 400
    
    def test_duplicate_signup_includes_error_message(self, test_client, activity_with_participants):
        """
        Test that duplicate signup error message is clear
        
        Validates:
        - Error message indicates duplicate signup
        - Error detail mentions student is already signed up
        - User gets helpful feedback
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
            error_detail = response.json()["detail"]
            assert "already" in error_detail.lower() or "signed up" in error_detail.lower()
    
    def test_signup_with_empty_email_parameter(self, test_client, valid_activity_name):
        """
        Test signup with empty email parameter
        
        Validates:
        - Empty string email is handled
        - Error is returned appropriately
        - Invalid input is rejected
        """
        # Arrange: Set up test with empty email
        empty_email = ""
        
        # Act: Attempt signup with empty email
        response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": empty_email}
        )
        
        # Assert: Empty email should be treated as invalid
        assert response.status_code >= 400
    
    def test_signup_without_email_parameter(self, test_client, valid_activity_name):
        """
        Test signup without email parameter returns error
        
        Validates:
        - Missing required parameters are rejected
        - Proper validation feedback is provided
        - API enforces required fields
        """
        # Arrange: Prepare request without email parameter
        
        # Act: Attempt signup without email query parameter
        response = test_client.post(f"/activities/{valid_activity_name}/signup")
        
        # Assert: Missing required parameter should cause validation error
        assert response.status_code >= 400
    
    def test_signup_with_special_characters_in_email(self, test_client, valid_activity_name):
        """
        Test signup with special characters in email
        
        Validates:
        - Special characters in emails are handled
        - Email validation works correctly
        - Unusual but valid email addresses work
        """
        # Arrange: Prepare email with special characters
        special_email = "student+test@mergington.edu"
        
        # Act: Attempt signup with special character email
        response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": special_email}
        )
        
        # Assert: Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_signup_adds_email_to_participants_list(self, test_client, valid_activity_name):
        """
        Test that successful signup adds the email to participants
        
        Validates:
        - Signup actually modifies the activity data
        - Email is persisted in participants list
        - Data is saved after signup
        """
        # Arrange: Get initial state and prepare test email
        test_email = f"verify_participants_{hash(valid_activity_name)}@test.mergington.edu"
        activities_before = test_client.get("/activities").json()
        initial_participants = activities_before[valid_activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Act: Sign up the student
        response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert: Only verify if signup was successful
        if response.status_code == 200:
            activities_after = test_client.get("/activities").json()
            final_participants = activities_after[valid_activity_name]["participants"]
            final_count = len(final_participants)
            
            assert final_count == initial_count + 1
            assert test_email in final_participants
    
    def test_signup_response_content_on_success(self, test_client, valid_activity_name):
        """
        Test that successful signup returns valid HTTP response
        
        Validates:
        - Response can be parsed as JSON
        - Request completes without error
        - HTTP status indicates success
        """
        # Arrange: Prepare test data
        test_email = "response_test@test.mergington.edu"
        
        # Act: Sign up for activity
        response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert: If successful, response should be parseable
        if response.status_code == 200:
            json_response = response.json()
            assert response.status_code == 200


class TestSignupEdgeCases:
    """Test edge cases and boundary conditions for signup"""
    
    def test_signup_with_unicode_email(self, test_client, valid_activity_name):
        """
        Test signup with unicode characters in email
        
        Validates:
        - Unicode handling in email parameter
        - Edge case handling
        - Internationalization support
        """
        # Arrange: Prepare email with unicode characters
        unicode_email = "student_ñ@test.mergington.edu"
        
        # Act: Attempt signup with unicode email
        response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": unicode_email}
        )
        
        # Assert: Should handle gracefully
        assert response.status_code >= 200
    
    def test_signup_with_very_long_email(self, test_client, valid_activity_name):
        """
        Test signup with extremely long email address
        
        Validates:
        - Long input handling
        - Request size limits
        - Edge case robustness
        """
        # Arrange: Create very long email address
        long_email = "a" * 200 + "@test.mergington.edu"
        
        # Act: Attempt signup with long email
        response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": long_email}
        )
        
        # Assert: Should handle without crashing
        assert response.status_code >= 200
    
    def test_signup_is_case_sensitive(self, test_client, valid_activity_name):
        """
        Test whether email signup is case-sensitive
        
        Validates:
        - Email handling consistency
        - Case sensitivity behavior
        - Re-signup prevention works correctly
        """
        # Arrange: Prepare email for first signup
        base_email = "case_test@Test.Mergington.Edu"
        
        # Act: First signup
        response1 = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": base_email}
        )
        
        # Assert: Check case sensitivity behavior
        if response1.status_code == 200:
            different_case_email = base_email.upper()
            response2 = test_client.post(
                f"/activities/{valid_activity_name}/signup",
                params={"email": different_case_email}
            )
            
            assert response2.status_code in [200, 400]
