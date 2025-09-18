"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_standard_tap_tests

from tap_gainsightpx.tap import TapGainsightPX

MOCK_API_URL = "https://api.example.com/v1"

SAMPLE_CONFIG = {
    "api_url": MOCK_API_URL,
    "api_key": "api_key",
    "start_date": "2022-01-01T00:00:00Z",
    "end_date": "2022-01-01T00:00:00Z",
}


def json_resp():
    return {
        "results": [],
        # "scrollId": None,
        "isLastPage": True,
        "totalHits": 0,
        "accounts": [],
        "engagements": [],
        "features": [],
        "featureMatchEvents": [],
        "customEvents": [],
        "identifyEvents": [],
        "sessionInitializedEvents": [],
        "segments": [],
        "users": [],
    }


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests(requests_mock):
    """Run standard tap tests from the SDK."""
    requests_mock.get(
        "https://api.example.com/v1/engagement?pageSize=500&filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/survey/responses?pageSize=500&sort=date",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/accounts?pageSize=500&sort=lastModifiedDate",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/feature?pageSize=200",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/accounts?pageSize=100&sort=lastModifiedDate",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/events/pageView?pageSize=500&sort=date&filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/events/feature_match?pageSize=500&sort=date&filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/events/custom?pageSize=500&sort=date&filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/events/email?pageSize=500&sort=date&filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/events/engagementView?pageSize=500&sort=date&"
        "filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/events/formSubmit?pageSize=500&sort=date&filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/events/identify?pageSize=500&sort=date&filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/events/lead?pageSize=500&sort=date&filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/events/segment_match?pageSize=500&sort=date&filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/events/session?pageSize=500&sort=date&filter="
        "date%3E%3D2022-01-01T00%3A00%3A00Z%3B"
        "date%3C%3D2022-01-01T00%3A00%3A00Z",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/segment?pageSize=200",
        json=json_resp(),
    )
    requests_mock.get(
        "https://api.example.com/v1/users?pageSize=500",
        json=json_resp(),
    )
    tests = get_standard_tap_tests(TapGainsightPX, config=SAMPLE_CONFIG)
    for test in tests:
        test()
