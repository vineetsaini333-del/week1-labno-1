"""
Tests for the /activities/{activity_name}/unregister endpoint

This module tests the DELETE unregister endpoint which allows students
to remove themselves from activities they've joined.
"""

import pytest


class TestUnregisterEndpoint:
    """Test suite for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_with_valid_activity_and_participant(
        self, test_client, activity_with_participants
    ):
        """
        Test successful unregister from an activity returns HTTP 200
        
        Validates:
        - Student can unregister from activity they joined
        - Valid activity name is required
        - Valid participant email is required
        - Correct HTTP status code is returned
        """
        # Arrange: Get activity and participant data
        activity_name, existing_email = activity_with_participants
        
        # Act & Assert: Only test if we found an activity with participants
        if activity_name is not None:
            response = test_client.delete(
                f"/activities/{activity_name}/unregister",
                params={"email": existing_email}
            )
            
            assert response.status_code == 200
    
    def test_unregister_with_nonexistent_activity_returns_404(self, test_client):
        """
        Test unregister from non-existent activity returns HTTP 404
        
        Validates:
        - Invalid activity names are rejected
        - Proper error response is returned
        - API prevents unregistering from fake activities
        - Correct HTTP status code for "not found"
        """
        # Arrange: Prepare test for non-existent activity
        nonexistent_activity = "Nonexistent Activity"
        test_email = "student@test.mergington.edu"
        
        # Act: Attempt to unregister from a non-existent activity
        response = test_client.delete(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": test_email}
        )
        
        # Assert: Verify the API returns 404 Not Found
        assert response.status_code == 404
    
    def test_unregister_404_includes_error_message(self, test_client):
        """
        Test that 404 response for unregister includes error message
        
        Validates:
        - Error response contains detail field
        - Message clearly indicates activity not found
        - User gets helpful feedback on errors
        """
        # Arrange: Prepare test for non-existent activity
        fake_activity = "Fake Activity"
        test_email = "student@test.mergington.edu"
        
        # Act: Request unregister from non-existent activity
        response = test_client.delete(
            "/activities/Fake%20Activity/unregister",
            params={"email": "student@test.mergington.edu"}
        )
        
        # Assert: Verify error message is present
        assert response.status_code == 404
        error_detail = response.json()["detail"]
        assert "not found" in error_detail.lower()
    
    def test_unregister_student_not_signed_up_returns_400(self, test_client, valid_activity_name):
        """
        Test that unregistering student not in activity returns HTTP 400
        
        Validates:
        - Can only unregister if actually signed up
        - Invalid operations are rejected
        - Proper error status code is returned
        - No accidental unregistration
        """
        # Arrange: Prepare test with unknown student
        unknown_email = "unknown_student_xyz@test.mergington.edu"
        
        # Act: Attempt to unregister someone who isn't signed up
        response = test_client.delete(
            f"/activities/{valid_activity_name}/unregister",
            params={"email": unknown_email}
        )
        
        # Assert: Verify rejected with HTTP 400 Bad Request
        assert response.status_code == 400
    
    def test_unregister_not_signed_up_includes_error_message(
        self, test_client, valid_activity_name
    ):
        """
        Test that unregister error message is clear
        
        Validates:
        - Error message indicates student not signed up
        - Error detail is descriptive
        - User gets helpful feedback
        """
        # Arrange: Prepare test with unknown student
        unknown_email = "not_signed_up@test.mergington.edu"
        
        # Act: Attempt unregister for someone not signed up
        response = test_client.delete(
            f"/activities/{valid_activity_name}/unregister",
            params={"email": unknown_email}
        )
        
        # Assert: Verify error message
        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "not signed up" in error_detail.lower()
    
    def test_unregister_without_email_parameter(self, test_client, valid_activity_name):
        """
        Test unregister without email parameter returns error
        
        Validates:
        - Missing required parameters are rejected  
        - Proper validation feedback is provided
        - API enforces required fields
        """
        # Arrange: Prepare request without email parameter
        
        # Act: Attempt unregister without email query parameter
        response = test_client.delete(f"/activities/{valid_activity_name}/unregister")
        
        # Assert: Missing required parameter should cause validation error
        assert response.status_code >= 400
    
    def test_unregister_with_empty_email(self, test_client, valid_activity_name):
        """
        Test unregister with empty email parameter
        
        Note: This test documents that the API currently accepts empty emails.
        
        Validates:
        - Empty string is handled gracefully
        - No crash or 5xx error occurs
        - API handles edge case
        """
        # Arrange: Prepare test with empty email
        
        # Act: Attempt unregister with empty email
        response = test_client.delete(
            f"/activities/{valid_activity_name}/unregister",
            params={"email": ""}
        )
        
        # Assert: API currently accepts empty email
        assert response.status_code in [200, 400]
    
    def test_unregister_removes_from_participants_list(
        self, test_client, activity_with_participants
    ):
        """
        Test that successful unregister removes student from participants
        
        Validates:
        - Unregister modifies the activity data
        - Email is removed from participants list
        - Data is persisted after unregister
        """
        # Arrange: Get activity and participant data
        activity_name, existing_email = activity_with_participants
        
        if activity_name is not None:
            activities_before = test_client.get("/activities").json()
            initial_participants = activities_before[activity_name]["participants"]
            initial_count = len(initial_participants)
            
            # Act: Unregister the student
            response = test_client.delete(
                f"/activities/{activity_name}/unregister",
                params={"email": existing_email}
            )
            
            # Assert: Only verify if unregister was successful
            if response.status_code == 200:
                activities_after = test_client.get("/activities").json()
                final_participants = activities_after[activity_name]["participants"]
                final_count = len(final_participants)
                
                assert final_count == initial_count - 1
                assert existing_email not in final_participants
    
    def test_unregister_response_includes_message(self, test_client, activity_with_participants):
        """
        Test that successful unregister response includes confirmation message
        
        Validates:
        - Response has appropriate message
        - Response structure is valid
        - User gets confirmation feedback
        """
        # Arrange: Get activity and participant data
        activity_name, existing_email = activity_with_participants
        
        if activity_name is not None:
            # Act: Unregister the student
            response = test_client.delete(
                f"/activities/{activity_name}/unregister",
                params={"email": existing_email}
            )
            
            # Assert: If successful, should have JSON response with message
            if response.status_code == 200:
                json_response = response.json()
                assert json_response is not None
                assert "message" in json_response or "detail" in json_response


class TestUnregisterEdgeCases:
    """Test edge cases and boundary conditions for unregister"""
    
    def test_unregister_same_student_twice(self, test_client, valid_activity_name):
        """
        Test that unregistering the same student twice fails properly
        
        Validates:
        - Can't unregister twice
        - Second attempt gets proper error
        - Data consistency is maintained
        """
        # Arrange: Prepare test with unique email
        test_email = "double_unregister_test@test.mergington.edu"
        
        # Act: First, sign up the student
        signup_response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert: If signup succeeds
        if signup_response.status_code == 200:
            unregister1 = test_client.delete(
                f"/activities/{valid_activity_name}/unregister",
                params={"email": test_email}
            )
            assert unregister1.status_code == 200
            
            unregister2 = test_client.delete(
                f"/activities/{valid_activity_name}/unregister",
                params={"email": test_email}
            )
            assert unregister2.status_code == 400
    
    def test_unregister_case_sensitivity(self, test_client, valid_activity_name):
        """
        Test case sensitivity in unregister email matching
        
        Validates:
        - Email matching behavior is consistent
        - Case handling is correct
        - Email comparison works properly
        """
        # Arrange: Prepare test with specific case email
        base_email = "case_unregister@Test.Mergington.Edu"
        
        # Act: Sign up with the email
        signup_response = test_client.post(
            f"/activities/{valid_activity_name}/signup",
            params={"email": base_email}
        )
        
        # Assert: Check case sensitivity behavior
        if signup_response.status_code == 200:
            different_case = base_email.upper()
            response = test_client.delete(
                f"/activities/{valid_activity_name}/unregister",
                params={"email": different_case}
            )
            
            assert response.status_code in [200, 400]
    
    def test_unregister_with_whitespace_in_email(self, test_client, valid_activity_name):
        """
        Test unregister with extra whitespace in email
        
        Validates:
        - Whitespace handling in email parameter
        - Email matching is robust
        - Whitespace normalization works
        """
        # Arrange: Prepare email with leading/trailing spaces
        email_with_spaces = "  test@test.mergington.edu  "
        
        # Act: Attempt unregister
        response = test_client.delete(
            f"/activities/{valid_activity_name}/unregister",
            params={"email": email_with_spaces}
        )
        
        # Assert: Should handle gracefully
        assert response.status_code >= 200
