from datetime import datetime, timedelta

import pytest
from pytz import utc

from src.exceptions import FlagNotFoundException
from src.repo.fake_repo import FakeInMemoryRepo
from src.services.flagship import FlagAllowedUpdates, FlagShipService


@pytest.mark.asyncio
async def test_user_can_add_a_new_flag():
    """
    Given a `flag` name and some initial `boolean` value
    When I call the `create_flag` method from `FlagShipService,`
    Then I'm expected a new `Flag` instance to be return
         with the right arguments.
    """

    # Given
    flagship = FlagShipService(repo=FakeInMemoryRepo())
    flag_name = "my first flag"
    value = False

    # When
    expected_flag = await flagship.create_flag(name=flag_name, value=value)

    # Then
    assert expected_flag.name == flag_name, "Store flag name should be the same as the input"
    assert expected_flag.value == value, "Store flag value should  be the same as the input"
    assert isinstance(expected_flag.id, str), "Each flash should be associated with one uuid"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "updated_field_name,updated_field_value",
    [
        pytest.param("desc", "my updated desc", id="Flag description can be updated"),
        pytest.param("name", "my updated name", id="Flag name can be updated"),
        pytest.param("value", True, id="Flag value can be updated"),
    ],
)
async def test_user_can_update_an_existing_flag_by_its_flag_id_and_the_new_fields(
    updated_field_name, updated_field_value
):
    """
    Given an existing `Flag` and some new fields to update
    When I call the `update_flag` method from `FlagShipService`
    Then I'm expecting the `Flag` to be updated with the new value
    """
    # Given
    flagship = FlagShipService(repo=FakeInMemoryRepo())
    existing_flag = await flagship.create_flag("my flag", value=True)

    updated_data = {updated_field_name: updated_field_value}
    updated_fields = FlagAllowedUpdates(**updated_data)

    # When
    updated_flag = await flagship.update_flag(
        flag_id=str(existing_flag.id), updated_fields=updated_fields
    )

    # Then
    assert getattr(updated_flag, updated_field_name) == updated_field_value, (
        f"Flag: `{updated_field_name}` should be updated"
    )


@pytest.mark.asyncio
async def test_user_cannot_update_flag_that_does_not_exist():
    """
    Given a non-existing `Flag`
    When I call the `update_flag` method from `FlagShipService`
    Then I'm expecting a `ValueError` to be raised
    """
    # Given
    flagship = FlagShipService(repo=FakeInMemoryRepo())
    updated_fields = FlagAllowedUpdates(name="new name")

    # When / Then
    with pytest.raises(FlagNotFoundException):
        await flagship.update_flag(flag_id="non-existing-flag-id", updated_fields=updated_fields)


@pytest.mark.asyncio
async def test_user_can_see_all_flags():
    """
    Given some `Flags`
    When I call the `list` method from `FlagShipService`
    Then I'm expecting an Iterable of flags
    """
    # Given
    flagship = FlagShipService(repo=FakeInMemoryRepo())
    await flagship.create_flag("first flag", value=True)
    await flagship.create_flag("second flag", value=False)

    # When
    flags_iter = await flagship.get_all_flags()

    # Then
    flags = list(flags_iter)
    assert len(flags) == 2, "We should have only two flags"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "flag_value,expected_value",
    [
        pytest.param(True, True, id="Flag should be enabled"),
        pytest.param(False, False, id="Flag should be disabled"),
    ],
)
async def test_user_can_get_flag_value_with_is_enabled_method_if_its_not_expired(
    flag_value, expected_value
):
    """
    Given a `Flag` which is `enabled`/ it's value is True.
    When I call the `is_enabled` method
    Then I'm expecting `True`
    """
    # Given
    flagship = FlagShipService(repo=FakeInMemoryRepo())
    await flagship.create_flag("first flag", value=flag_value)
    # When
    received_value = await flagship.is_enabled("first flag")
    # Then
    assert received_value == expected_value, "Something wrong happened"


@pytest.mark.asyncio
async def test_user_can_see_flag_as_disabled_even_if_value_is_true_but_its_expired():
    """
    Given a `Flag` which is `enabled`/ it's value is True, but it's expired
    When I call the `is_enabled` method
    Then I'm expecting `False`
    """
    # Given
    flagship = FlagShipService(repo=FakeInMemoryRepo())
    flag = await flagship.create_flag("first flag", value=True)
    flag.expiration_date = datetime.now(tz=utc) - timedelta(days=1)
    # When
    received_value = await flagship.is_enabled("first flag")
    # Then
    assert received_value is False, "Something wrong happened, flag is expired!"
