from src.app import activities


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestActivities:
    def test_get_activities_returns_activity_details(self, client):
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        response_activities = response.json()
        assert set(activities) <= set(response_activities)
        for activity in response_activities.values():
            assert set(activity) == expected_fields
            assert isinstance(activity["participants"], list)


class TestSignup:
    def test_signup_adds_participant_and_returns_success(self, client):
        # Arrange
        activity_name = "Soccer Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )
        activities_response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in activities_response.json()[activity_name]["participants"]

    def test_duplicate_signup_returns_bad_request_without_duplicate(self, client):
        # Arrange
        activity_name = "Soccer Club"
        email = "student@mergington.edu"
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        assert activities[activity_name]["participants"].count(email) == 1

    def test_signup_for_unknown_activity_returns_not_found(self, client):
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

    def test_signup_without_email_returns_unprocessable_entity(self, client):
        # Arrange
        activity_name = "Soccer Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422


class TestUnregister:
    def test_unregister_removes_participant_and_allows_signup_again(self, client):
        # Arrange
        activity_name = "Soccer Club"
        email = "student@mergington.edu"
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert signup_response.status_code == 200

    def test_unregister_from_unknown_activity_returns_not_found(self, client):
        # Arrange
        activity_name = "Unknown Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/student%40mergington.edu"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_unknown_participant_returns_not_found(self, client):
        # Arrange
        activity_name = "Soccer Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_repeated_unregister_returns_not_found(self, client):
        # Arrange
        activity_name = "Soccer Club"
        email = "student@mergington.edu"
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        client.delete(f"/activities/{activity_name}/participants/{email}")

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student is not signed up for this activity"
