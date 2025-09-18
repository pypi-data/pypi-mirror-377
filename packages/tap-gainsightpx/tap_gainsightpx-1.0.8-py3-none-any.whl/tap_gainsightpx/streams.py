"""Stream type classes for tap-gainsightpx."""
from __future__ import annotations

from typing import Any, Dict, Optional

from singer_sdk import typing as th

from tap_gainsightpx.client import GainsightPXStream


class AccountsStream(GainsightPXStream):
    """Accounts Stream."""

    name = "accounts"
    path = "/accounts"
    records_jsonpath = "$.accounts[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["id"]
    replication_key = "lastModifiedDate"
    schema = th.PropertiesList(
        th.Property("createDate", th.IntegerType),
        th.Property("customAttributes", th.ObjectType()),
        th.Property("dunsNumber", th.StringType),
        th.Property("id", th.StringType),
        th.Property("industry", th.StringType),
        th.Property("lastModifiedDate", th.IntegerType),
        th.Property("lastSeenDate", th.IntegerType),
        th.Property("location", th.ObjectType()),
        th.Property("naicsCode", th.StringType),
        th.Property("name", th.StringType),
        th.Property("numberOfEmployees", th.IntegerType),
        th.Property("numberOfUsers", th.IntegerType),
        th.Property("parentGroupId", th.StringType),
        th.Property("plan", th.StringType),
        th.Property("propertyKeys", th.ArrayType(th.StringType)),
        th.Property("sfdcId", th.StringType),
        th.Property("sicCode", th.StringType),
        th.Property("trackedSubscriptionId", th.StringType),
        th.Property("website", th.StringType),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {"pageSize": 100}

        if self.replication_key:
            params["sort"] = self.replication_key
        if next_page_token:
            params["scrollId"] = next_page_token

        return params


class CustomEventsStream(GainsightPXStream):
    """Custom Events Stream."""

    name = "custom_events"
    path = "/events/custom"
    records_jsonpath = "$.customEvents[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("sessionId", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("eventName", th.StringType),
        th.Property("attributes", th.ObjectType()),
        th.Property("url", th.StringType),
        th.Property("referrer", th.StringType),
        th.Property("remoteHost", th.StringType),
    ).to_dict()


class EmailEventsStream(GainsightPXStream):
    """Email Events Stream."""

    name = "email_events"
    path = "/events/email"
    records_jsonpath = "$.results[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("engagementId", th.StringType),
        th.Property("email", th.StringType),
        th.Property("emailTrackType", th.StringType),
        th.Property("status", th.StringType),
        th.Property("reason", th.StringType),
        th.Property("bounceType", th.StringType),
        th.Property("mtaResponse", th.StringType),
        th.Property("attempt", th.StringType),
        th.Property("linkIndex", th.IntegerType),
        th.Property("linkType", th.StringType),
        th.Property("linkUrl", th.StringType),
        th.Property("inferredLocation", th.ObjectType()),
    ).to_dict()


class EngagementViewEventsStream(GainsightPXStream):
    """Engagement View Events Stream."""

    name = "engagement_view_events"
    path = "/events/engagementView"
    records_jsonpath = "$.results[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("sessionId", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("engagementId", th.StringType),
        th.Property("engagementTrackType", th.StringType),
        th.Property("contentId", th.StringType),
        th.Property("contentType", th.StringType),
        th.Property("executionDate", th.IntegerType),
        th.Property("executionId", th.StringType),
        th.Property("viewEventId", th.StringType),
        th.Property("carouselState", th.StringType),
        th.Property("slideId", th.StringType),
        th.Property("sequenceNumber", th.IntegerType),
        th.Property("linkUrl", th.StringType),
        th.Property("guideState", th.StringType),
        th.Property("stepId", th.StringType),
        th.Property("surveyState", th.StringType),
        th.Property("contactMeAllowed", th.BooleanType),
        th.Property("score", th.IntegerType),
        th.Property("comment", th.StringType),
        th.Property("questionType", th.StringType),
        th.Property("selectionIds", th.ArrayType(th.StringType)),
        th.Property("path", th.StringType),
    ).to_dict()


class EngagementsStream(GainsightPXStream):
    """Engagements Stream."""

    name = "engagements"
    path = "/engagement"
    records_jsonpath = "$.engagements[*]"
    primary_keys = ["id"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("description", th.StringType),
        th.Property("envs", th.ArrayType(th.StringType)),
        th.Property("id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("propertyKeys", th.ArrayType(th.StringType)),
        th.Property("state", th.StringType),
        th.Property("type", th.StringType),
    ).to_dict()

    def add_more_url_params(
        self, params: dict, next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Add more params specific to the stream."""
        params["filter"] = ";".join(
            [
                f"date>={self.config['start_date']}",
                f"date<={self.config['end_date']}",
            ]
        )
        if next_page_token:
            params["pageNumber"] = next_page_token
        return params


class FeatureMatchEventsStream(GainsightPXStream):
    """Feature Match Events Stream."""

    name = "feature_match_events"
    path = "/events/feature_match"
    records_jsonpath = "$.featureMatchEvents[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("sessionId", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("featureId", th.StringType),
    ).to_dict()


class FeaturesStream(GainsightPXStream):
    """Features Stream."""

    name = "features"
    path = "/feature"
    records_jsonpath = "$.features[*]"
    primary_keys = ["id"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("type", th.StringType),
        th.Property("parentFeatureId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("status", th.StringType),
    ).to_dict()

    def add_more_url_params(
        self, params: dict, next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Add more params specific to the stream."""
        if params["pageSize"] > 200:
            params["pageSize"] = 200
        if next_page_token:
            params["pageNumber"] = next_page_token
        return params


class FormSubmitEventsStream(GainsightPXStream):
    """Form Submit Events Stream."""

    name = "form_submit_events"
    path = "/events/formSubmit"
    records_jsonpath = "$.results[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("sessionId", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("host", th.StringType),
        th.Property("path", th.StringType),
        th.Property("queryString", th.StringType),
        th.Property("hash", th.StringType),
        th.Property("queryParams", th.ObjectType()),
        th.Property("remoteHost", th.StringType),
        th.Property("referrer", th.StringType),
        th.Property("screenHeight", th.IntegerType),
        th.Property("screenWidth", th.IntegerType),
        th.Property("languages", th.ArrayType(th.StringType)),
        th.Property("pageTitle", th.StringType),
        th.Property("formData", th.ObjectType()),
    ).to_dict()


class IdentifyEventsStream(GainsightPXStream):
    """Identify Events Stream."""

    name = "identify_events"
    path = "/events/identify"
    records_jsonpath = "$.identifyEvents[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("sessionId", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("email", th.StringType),
    ).to_dict()


class LeadEventsStream(GainsightPXStream):
    """Lead Events Stream."""

    name = "lead_events"
    path = "/events/lead"
    records_jsonpath = "$.results[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("sessionId", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("email", th.StringType),
    ).to_dict()


class PageViewEventsStream(GainsightPXStream):
    """Page View Events Stream."""

    name = "page_view_events"
    path = "/events/pageView"
    records_jsonpath = "$.results[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("sessionId", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("scheme", th.StringType),
        th.Property("host", th.StringType),
        th.Property("path", th.StringType),
        th.Property("queryString", th.StringType),
        th.Property("hash", th.StringType),
        th.Property("queryParams", th.ObjectType()),
        th.Property("remoteHost", th.StringType),
        th.Property("referrer", th.StringType),
        th.Property("screenHeight", th.IntegerType),
        th.Property("screenWidth", th.IntegerType),
        th.Property("languages", th.ArrayType(th.StringType)),
        th.Property("pageTitle", th.StringType),
    ).to_dict()


class SegmentMatchEventsStream(GainsightPXStream):
    """Segment Match Events Stream."""

    name = "segment_match_events"
    path = "/events/segment_match"
    records_jsonpath = "$.featureMatchEvents[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("sessionId", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("segmentId", th.StringType),
    ).to_dict()


class SegmentsStream(GainsightPXStream):
    """Segments Stream."""

    name = "segments"
    path = "/segment"
    records_jsonpath = "$.segments[*]"
    primary_keys = ["id"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("name", th.StringType),
    ).to_dict()

    def add_more_url_params(
        self, params: dict, next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Add more params specific to the stream."""
        if params["pageSize"] > 200:
            params["pageSize"] = 200
        if next_page_token:
            params["pageNumber"] = next_page_token
        return params


class SessionEventsStream(GainsightPXStream):
    """Session Events Stream."""

    name = "session_events"
    path = "/events/session"
    records_jsonpath = "$.sessionInitializedEvents[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("sessionId", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("remoteHost", th.StringType),
        th.Property("inferredLocation", th.ObjectType()),
    ).to_dict()


class SurveyResponsesStream(GainsightPXStream):
    """Survey Responses Stream."""

    name = "survey_responses"
    path = "/survey/responses"
    records_jsonpath = "$.results[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["eventId"]
    replication_key = "date"
    schema = th.PropertiesList(
        th.Property("eventId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("propertyKey", th.StringType),
        th.Property("date", th.IntegerType),
        th.Property("eventType", th.StringType),
        th.Property("sessionId", th.StringType),
        th.Property("userType", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("globalContext", th.ObjectType()),
        th.Property("engagementId", th.StringType),
        th.Property("engagementTrackType", th.StringType),
        th.Property("contentId", th.StringType),
        th.Property("contentType", th.StringType),
        th.Property(
            "executionDate",
            th.IntegerType,
            description="Will be the same on all events related to a single "
            "engagement view, e.g. separate answers for "
            "multi-question surveys",
        ),
        th.Property(
            "executionId",
            th.StringType,
            description="Will be the same on all events related to a single "
            "engagement view, e.g. separate answers for "
            "multi-question surveys",
        ),
        th.Property("viewEventId", th.StringType),
        th.Property("carouselState", th.StringType),
        th.Property("slideId", th.StringType),
        th.Property("sequenceNumber", th.IntegerType),
        th.Property("linkUrl", th.StringType),
        th.Property("guideState", th.StringType),
        th.Property("stepId", th.StringType),
        th.Property("surveyState", th.StringType),
        th.Property("contactMeAllowed", th.BooleanType),
        th.Property("score", th.IntegerType),
        th.Property("comment", th.StringType),
        th.Property("questionType", th.StringType),
        th.Property("selectionIds", th.ArrayType(th.StringType)),
        th.Property("path", th.StringType),
    ).to_dict()

    def add_more_url_params(
        self, params: dict, next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Add more params specific to the stream."""
        if next_page_token:
            params["scrollId"] = next_page_token
        return params


class UsersStream(GainsightPXStream):
    """Users Stream."""

    name = "users"
    path = "/users"
    records_jsonpath = "$.users[*]"
    next_page_token_jsonpath = "$.scrollId"
    primary_keys = ["aptrinsicId"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("aptrinsicId", th.StringType),
        th.Property("identifyId", th.StringType),
        th.Property("type", th.StringType),
        th.Property("gender", th.StringType),
        th.Property("email", th.StringType),
        th.Property("firstName", th.StringType),
        th.Property("lastName", th.StringType),
        th.Property("lastSeenDate", th.IntegerType),
        th.Property("signUpDate", th.IntegerType),
        th.Property("firstVisitDate", th.IntegerType),
        th.Property("title", th.StringType),
        th.Property("phone", th.StringType),
        th.Property("score", th.IntegerType),
        th.Property("role", th.StringType),
        th.Property("subscriptionId", th.StringType),
        th.Property("accountId", th.StringType),
        th.Property("numberOfVisits", th.IntegerType),
        th.Property("location", th.ObjectType()),
        th.Property("propertyKeys", th.ArrayType(th.StringType)),
        th.Property("createDate", th.IntegerType),
        th.Property("lastModifiedDate", th.IntegerType),
        th.Property("customAttributes", th.ObjectType()),
        th.Property("globalUnsubscribe", th.BooleanType),
        th.Property("sfdcContactId", th.StringType),
        th.Property("lastVisitedUserAgentData", th.ArrayType(th.ObjectType())),
        th.Property("id", th.StringType),
        th.Property("lastInferredLocation", th.ObjectType()),
    ).to_dict()

    def add_more_url_params(
        self, params: dict, next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Add more params specific to the stream."""
        if next_page_token:
            params["scrollId"] = next_page_token
        return params
