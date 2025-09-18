"""GainsightPX tap class."""
from datetime import date, timedelta
from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_gainsightpx.streams import (
    AccountsStream,
    CustomEventsStream,
    EmailEventsStream,
    EngagementsStream,
    EngagementViewEventsStream,
    FeatureMatchEventsStream,
    FeaturesStream,
    FormSubmitEventsStream,
    IdentifyEventsStream,
    LeadEventsStream,
    PageViewEventsStream,
    SegmentMatchEventsStream,
    SegmentsStream,
    SessionEventsStream,
    SurveyResponsesStream,
    UsersStream,
)

STREAM_TYPES = [
    AccountsStream,
    CustomEventsStream,
    EmailEventsStream,
    EngagementsStream,
    EngagementViewEventsStream,
    FeatureMatchEventsStream,
    FeaturesStream,
    FormSubmitEventsStream,
    IdentifyEventsStream,
    LeadEventsStream,
    PageViewEventsStream,
    SegmentMatchEventsStream,
    SegmentsStream,
    SessionEventsStream,
    SurveyResponsesStream,
    UsersStream,
]


class TapGainsightPX(Tap):
    """GainsightPX tap class."""

    name = "tap-gainsightpx"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_url",
            th.StringType,
            required=False,
            default="https://api.aptrinsic.com/v1",  # type: ignore[arg-type]
            description="The base url for GainsightPX service. See GainsightPX docs.",
        ),
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,
            description="The api key to authenticate against the GainsightPX service",
        ),
        th.Property(
            "page_size",
            th.IntegerType,
            required=False,
            default=500,  # type: ignore[arg-type]
            description="The number of records to return from the API in single page."
            "Default and max varies based on the endpoint.",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            default=(
                date.today() - timedelta(days=1)  # type: ignore[arg-type]
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            description="The earliest record date to sync (inclusive '>='). ISO Format",
        ),
        th.Property(
            "end_date",
            th.DateTimeType,
            default=(
                date.today() - timedelta(microseconds=1)  # type: ignore[arg-type]
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            description="The latest record date to sync (inclusive '<='). ISO format.",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapGainsightPX.cli()
