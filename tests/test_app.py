def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_json_object(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload


def _activity_name_for_url(activity_name):
    return activity_name.replace(" ", "%20")


def _get_activity(client, activity_name="Chess Club"):
    response = client.get("/activities")
    assert response.status_code == 200
    payload = response.json()
    assert activity_name in payload
    return payload[activity_name]


def _participants_for_activity(activity_payload):
    participants = activity_payload.get("participants", [])
    assert isinstance(participants, list)
    return participants


def _capacity_for_activity(activity_payload):
    for key in ("capacity", "max_capacity", "maxParticipants", "max_participants"):
        if key in activity_payload:
            return activity_payload[key]
    raise AssertionError("Activity payload does not expose a capacity field")


def _signup(client, activity_name, participant_name):
    encoded_name = _activity_name_for_url(activity_name)
    return client.post(
        f"/activities/{encoded_name}/signup",
        json={"name": participant_name},
    )


def _unregister(client, activity_name, participant_name):
    encoded_name = _activity_name_for_url(activity_name)
    return client.post(
        f"/activities/{encoded_name}/unregister",
        json={"name": participant_name},
    )


def test_signup_twice_returns_400(client):
    activity_name = "Chess Club"
    participant_name = "duplicate-signup-user"

    first_response = _signup(client, activity_name, participant_name)
    assert first_response.status_code == 200

    second_response = _signup(client, activity_name, participant_name)
    assert second_response.status_code == 400


def test_signup_when_activity_is_full_returns_400(client):
    activity_name = "Chess Club"
    activity = _get_activity(client, activity_name)
    participants = _participants_for_activity(activity)
    capacity = _capacity_for_activity(activity)

    for i in range(len(participants), capacity):
        response = _signup(client, activity_name, f"capacity-user-{i}")
        assert response.status_code == 200

    full_response = _signup(client, activity_name, "capacity-user-overflow")
    assert full_response.status_code == 400


def test_unregister_removes_participant_and_returns_200(client):
    activity_name = "Chess Club"
    participant_name = "removable-user"

    signup_response = _signup(client, activity_name, participant_name)
    assert signup_response.status_code == 200

    unregister_response = _unregister(client, activity_name, participant_name)
    assert unregister_response.status_code == 200

    activity = _get_activity(client, activity_name)
    participants = _participants_for_activity(activity)
    assert participant_name not in participants


def test_unregistering_non_member_returns_error(client):
    activity_name = "Chess Club"
    participant_name = "not-a-member"

    response = _unregister(client, activity_name, participant_name)
    assert response.status_code in {400, 404}
