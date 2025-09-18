"""Pagination handling. Modifies base classes."""
from __future__ import annotations

import re
from typing import Any

from requests import Response
from singer_sdk.pagination import BasePageNumberPaginator, JSONPathPaginator


class GainsightJSONPathPaginator(JSONPathPaginator):
    """An API paginator object for Gainsight."""

    current_record_count: int = 0

    def __init__(
        self,
        jsonpath: str,
        records_jsonpath: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Create a new paginator."""
        super().__init__(jsonpath, *args, **kwargs)
        self._records_jsonpath = records_jsonpath

    def has_more(self, response: Response) -> bool:
        """Override this method to check if the endpoint has any pages left."""
        res = response.json()
        scroll_id = res.get("scrollId")
        total_hits = res.get("totalHits")
        records_key = re.findall(r"\$\.(.*)\[\*\]", self._records_jsonpath)[0]

        response_record_count = len(res[records_key])
        self.current_record_count += response_record_count
        if response_record_count == 0 or scroll_id is None:
            return False
        elif total_hits > self.current_record_count:
            return True

        return False

    def advance(self, response: Response) -> None:
        """Get a new page value and advance the current one."""
        self._page_count += 1

        if not self.has_more(response):
            self._finished = True
            return

        new_value = self.get_next(response)

        # Stop if new value None, empty string, 0, etc.
        if not new_value:
            self._finished = True
        else:
            self._value = new_value


class GainsightBasePageNumberPaginator(BasePageNumberPaginator):
    """Paginator class for APIs that use page number."""

    def has_more(self, response: Response) -> bool:
        """Indicate if the endpoint has more pages."""
        return not response.json().get("isLastPage")
