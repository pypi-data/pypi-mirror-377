"""REST client handling, including GainsightPXStream base class."""
from __future__ import annotations

from typing import Any, Dict, Optional

from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream

from tap_gainsightpx.paginators import (
    GainsightBasePageNumberPaginator,
    GainsightJSONPathPaginator,
)


class GainsightPXStream(RESTStream):
    """GainsightPX stream class."""

    current_record_count = 0

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]

    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Return a new authenticator object."""
        return APIKeyAuthenticator.create_for_stream(
            self,
            key="X-APTRINSIC-API-KEY",
            value=self.config["api_key"],
            location="header",
        )

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}

        page_size = self.config.get("page_size")
        if page_size:
            params["pageSize"] = page_size
        if self.replication_key:
            params["sort"] = self.replication_key

        return self.add_more_url_params(params, next_page_token)

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
            params["scrollId"] = next_page_token
        return params

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Get a fresh paginator for this API endpoint."""
        if self.next_page_token_jsonpath:
            return GainsightJSONPathPaginator(
                self.next_page_token_jsonpath, self.records_jsonpath
            )
        else:
            return GainsightBasePageNumberPaginator(0)
