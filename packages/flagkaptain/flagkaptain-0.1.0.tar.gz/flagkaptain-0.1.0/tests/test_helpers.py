from datetime import datetime, timedelta

import pytest
from pytz import utc

from src.helpers import new_expiration_date

MODULE = "src.helpers"

MOCKED_DT_NOW = datetime(2024, 1, 1, 0, 0, 0, tzinfo=utc)


@pytest.mark.parametrize(
    "time_unit,value,expected_expiration_date",
    [
        pytest.param(
            "m",
            1,
            MOCKED_DT_NOW + timedelta(minutes=1),
            id="new expiration date can be updated by minutes",
        ),
        pytest.param(
            "h",
            1,
            MOCKED_DT_NOW + timedelta(hours=1),
            id="new expiration date can be updated by hours",
        ),
        pytest.param(
            "d",
            1,
            MOCKED_DT_NOW + timedelta(days=1),
            id="new expiration date can be updated by days",
        ),
        pytest.param(
            "w",
            1,
            MOCKED_DT_NOW + timedelta(weeks=1),
            id="new expiration date can be updated by weeks",
        ),
    ],
)
def test_new_expiration_date_from_now(time_unit, value, expected_expiration_date):
    """
    Given some `time unit` and a `value`
    When I call the `new_expiration_date` function,
    Then I expect to get a `datetime` object that is the current time plus the given value in the given unit
    """
    assert (
        new_expiration_date(current_datetime=MOCKED_DT_NOW, unit=time_unit, value=value)
        == expected_expiration_date
    )


def test_new_expiration_date_raises_value_error_on_invalid_time_unit():
    """
    Given an invalid `time unit`
    When I call the `new_expiration_date` function,
    Then I expect to get a `ValueError`
    """
    with pytest.raises(ValueError) as exc_info:
        new_expiration_date(current_datetime=MOCKED_DT_NOW, unit="invalid", value=1)
    assert "Invalid time unit: invalid" in str(exc_info.value)
