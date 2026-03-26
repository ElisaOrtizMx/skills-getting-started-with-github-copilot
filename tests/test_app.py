"""
Tests for the Mergington High School Activities API
Using the AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_list(self):
        """Test that GET /activities returns activities list"""
        # Arrange
        expected_status = 200
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert isinstance(activities, dict)
        assert len(activities) > 0
    
    def test_get_activities_contains_expected_fields(self):
        """Test that activities have required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Field '{field}' missing from {activity_name}"
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_contains_chess_club(self):
        """Test that Chess Club exists in activities"""
        # Arrange
        expected_activity = "Chess Club"
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert expected_activity in activities


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        test_email = "newstudent@mergington.edu"
        expected_status = 200
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        response_data = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert "message" in response_data
        assert test_email in response_data["message"]
        assert activity_name in response_data["message"]
    
    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        test_email = "student@mergington.edu"
        expected_status = 404
        expected_detail = "Activity not found"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={test_email}"
        )
        response_data = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert response_data["detail"] == expected_detail
    
    def test_signup_duplicate_email(self):
        """Test signup with email already registered"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        expected_status = 400
        expected_message = "already signed up"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        response_data = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert expected_message in response_data["detail"]
    
    def test_signup_same_email_different_activity(self):
        """Test that same email can sign up for different activities"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Programming Class"
        expected_status = 200
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == expected_status
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self):
        """Test successful removal of a participant"""
        # Arrange
        activity_name = "Chess Club"
        get_response = client.get("/activities")
        participants_before = get_response.json()[activity_name]["participants"]
        email_to_remove = participants_before[0]
        expected_status = 200
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        response_data = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert "Removed" in response_data["message"]
        assert email_to_remove in response_data["message"]
    
    def test_remove_participant_activity_not_found(self):
        """Test removing participant from non-existent activity"""
        # Arrange
        fake_activity = "Fake Activity"
        test_email = "student@mergington.edu"
        expected_status = 404
        expected_detail = "Activity not found"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/participants/{test_email}"
        )
        response_data = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert response_data["detail"] == expected_detail
    
    def test_remove_nonexistent_participant(self):
        """Test removing non-existent participant from activity"""
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "nonexistent@mergington.edu"
        expected_status = 404
        expected_message = "Participant not found"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        response_data = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert expected_message in response_data["detail"]


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_signup_and_remove_workflow(self):
        """Test complete workflow: signup, verify, and remove"""
        # Arrange
        test_email = "workflow_test@mergington.edu"
        activity_name = "Art Studio"
        
        # Act - Step 1: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        
        # Assert - Step 1
        assert signup_response.status_code == 200
        
        # Act - Step 2: Verify participant is in the list
        get_response = client.get("/activities")
        activities = get_response.json()
        participant_found = test_email in activities[activity_name]["participants"]
        
        # Assert - Step 2
        assert participant_found, f"{test_email} not found in {activity_name}"
        
        # Act - Step 3: Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        
        # Assert - Step 3
        assert remove_response.status_code == 200
        
        # Act - Step 4: Verify participant is removed
        get_response = client.get("/activities")
        activities = get_response.json()
        participant_removed = test_email not in activities[activity_name]["participants"]
        
        # Assert - Step 4
        assert participant_removed, f"{test_email} still found in {activity_name}"
