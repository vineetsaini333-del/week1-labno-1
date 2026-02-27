"""
Shared test configuration and fixtures for backend FastAPI tests

This module provides pytest fixtures and setup used across all backend tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

# Module-level fixture: Create a single test client instance
# Scope="module" means it's created once per test module for efficiency
@pytest.fixture(scope="module")
def test_client():
    """
    Provides a TestClient instance connected to the FastAPI app
    
    The TestClient allows us to make HTTP requests to the application
    without starting a real server. This is used for all API tests.
    
    Yields:
        TestClient: A client for making requests to the FastAPI app
    """
    client = TestClient(app)
    return client


# Function-level fixture: Available activity names for testing
@pytest.fixture(scope="function")
def available_activities(test_client):
    """
    Fetches the current list of available activities from the API
    
    This fixture dynamically gets activity names from the /activities endpoint,
    ensuring tests use real activity data. Useful for tests that need to work
    with actual activities in the database.
    
    Args:
        test_client: The TestClient fixture to make API requests
        
    Returns:
        dict: Dictionary of activities with their details
    """
    response = test_client.get("/activities")
    return response.json()


@pytest.fixture(scope="function")
def valid_activity_name(available_activities):
    """
    Returns the first available activity name from the database
    
    This provides a known-good activity name for tests that need to
    perform operations on a real activity.
    
    Args:
        available_activities: The fixtures that retrieves all activities
        
    Returns:
        str: The name of the first activity in the database
    """
    return next(iter(available_activities.keys()))


@pytest.fixture(scope="function")
def activity_with_participants(available_activities):
    """
    Finds and returns an activity that has existing participants
    
    Useful for tests that need to work with a populated activity
    (e.g., testing duplicate signup or unregister functionality).
    
    Args:
        available_activities: The fixture that retrieves all activities
        
    Returns:
        tuple: (activity_name, existing_email) of an activity with participants,
               or (None, None) if no activities have participants
    """
    for activity_name, details in available_activities.items():
        if details["participants"]:
            return activity_name, details["participants"][0]
    return None, None


@pytest.fixture(scope="function")
def activity_without_participants(available_activities):
    """
    Finds and returns an activity with no current participants
    
    Useful for testing signup operations without conflicts from
    existing participants.
    
    Args:
        available_activities: The fixture that retrieves all activities
        
    Returns:
        str: The name of an activity with no participants,
             or None if all activities have participants
    """
    for activity_name, details in available_activities.items():
        if not details["participants"]:
            return activity_name
    return None
