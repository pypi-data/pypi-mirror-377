from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_user_can_retrieve_all_flags(client, fake_flags_fixture):
    """
    Given some existing `Flags` in the `database/system`
    When I call the `/flags` endpoint,
    Then I'm expecting a list of `Flags` to be returned,
         and the response status code to be `200`
    """
    # Given

    await fake_flags_fixture(10)

    # When
    response = client.get("/flags")

    # Then
    assert response.status_code == HTTPStatus.OK, "Expected status code 200"
    data = response.json()
    assert isinstance(data, list), "Expected response to be a list"
    assert len(data) == 10, "Expected 10 flags in the response"


@pytest.mark.asyncio
async def test_user_can_retrieve_a_single_flag(client, fake_flags_fixture):
    """
    Given an existing `Flag` in the `database/system`
    When I call the `/flags/{flag_id}` endpoint,
    Then I'm expecting the `Flag` to be returned,
         and the response status code to be `200`
    """
    # Given
    await fake_flags_fixture(1)
    response_all = client.get("/flags")
    flag_id = response_all.json()[0]["id"]

    # When
    response = client.get(f"/flags/{flag_id}")

    # Then
    assert response.status_code == HTTPStatus.OK, "Expected status code 200"
    expected_response = response.json()
    assert expected_response["id"] == flag_id, "Flag ID should match"
    assert "name" in expected_response, "Response should contain flag name"
    assert "value" in expected_response, "Response should contain flag value"
    assert "desc" in expected_response, "Response should contain flag description"


def test_user_can_create_a_new_flag(client):
    """
    Given a new `Flag` data
    When I call the `/flags` endpoint with a POST request,
    Then I'm expecting the flag to be created,
         and the response status code to be `201`
    """
    # Given
    new_flag_data = {
        "name": "new_feature",
        "value": True,
        "desc": "A new feature flag for testing",
    }

    # When
    response = client.post("/flags", json=new_flag_data)

    # Then
    assert response.status_code == HTTPStatus.CREATED, "Expected status code 201"
    expected_response = response.json()
    assert expected_response["name"] == new_flag_data["name"], "Flag name should match"
    assert expected_response["value"] == new_flag_data["value"], "Flag value should match"
    assert expected_response["desc"] == new_flag_data["desc"], "Flag description should match"
    assert "id" in expected_response, "Response should contain flag ID"


@pytest.mark.asyncio
async def test_user_can_update_an_existing_flag(client, fake_flags_fixture):
    """
    Given an existing `Flag` in the `database/system`
    When I call the `/flags/{flag_id}` endpoint with a PATCH request,
    Then I'm expecting the flag to be updated,
         and the response status code to be `200`
    """
    # Given
    await fake_flags_fixture(1)
    response_all = client.get("/flags")
    flag = response_all.json()[0]
    flag_id = flag["id"]
    updated_data = {
        "name": "updated_feature",
        "value": False,
        "desc": "An updated feature flag for testing",
    }

    # When
    response = client.patch(f"/flags/{flag_id}", json=updated_data)

    # Then
    assert response.status_code == HTTPStatus.OK, "Expected status code 200"
    expected_response = response.json()
    assert expected_response["id"] == flag_id, "Flag ID should match"
    assert expected_response["name"] == updated_data["name"], "Flag name should match"
    assert expected_response["value"] == updated_data["value"], "Flag value should match"
    assert expected_response["desc"] == updated_data["desc"], "Flag description should match"


def test_user_cannot_update_a_non_existing_flag(client):
    """
    Given a non-existing `Flag` ID
    When I call the `/flags/{flag_id}` endpoint with a PATCH request,
    Then I'm expecting a `404` status code
    """
    # Given
    non_existing_flag_id = "non-existing-id"
    updated_data = {
        "name": "updated_feature",
        "value": False,
        "desc": "An updated feature flag for testing",
    }

    # When
    response = client.patch(f"/flags/{non_existing_flag_id}", json=updated_data)

    # Then
    assert response.status_code == HTTPStatus.NOT_FOUND, "Expected status code 404"


@pytest.mark.asyncio
async def test_user_can_delete_an_existing_flag(client, fake_flags_fixture):
    """
    Given an existing `Flag` in the `database/system`
    When I call the `/flags/{flag_id}` endpoint with a DELETE request,
    Then I'm expecting the flag to be deleted,
         and the response status code to be `204`
    """
    # Given
    flags = await fake_flags_fixture(1)
    flag_id = flags[0].id
    # When
    response = client.delete(f"/flags/{flag_id}")

    # Then
    assert response.status_code == HTTPStatus.NO_CONTENT, "Expected status code 204"

    # Verify deletion
    get_response = client.get(f"/flags/{flag_id}")
    assert get_response.status_code == HTTPStatus.NOT_FOUND, (
        "Expected status code 404 after deletion"
    )


def test_user_cannot_delete_a_non_existing_flag(client):
    """
    Given a non-existing `Flag` ID
    When I call the `/flags/{flag_id}` endpoint with a DELETE request,
    Then I'm expecting a `404` status code
    """
    # Given
    non_existing_flag_id = "non-existing-id"

    # When
    response = client.delete(f"/flags/{non_existing_flag_id}")

    # Then
    assert response.status_code == HTTPStatus.NOT_FOUND, "Expected status code 404"
