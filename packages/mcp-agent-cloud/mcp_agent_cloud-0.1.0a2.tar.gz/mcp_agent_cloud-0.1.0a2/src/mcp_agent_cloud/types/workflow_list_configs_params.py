# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["WorkflowListConfigsParams"]


class WorkflowListConfigsParams(TypedDict, total=False):
    label_filter: Required[Annotated[Dict[str, str], PropertyInfo(alias="labelFilter")]]
    """Filter by label"""

    max_results: Required[Annotated[int, PropertyInfo(alias="maxResults")]]
    """Maximum number of results to return"""

    page_token: Required[Annotated[str, PropertyInfo(alias="pageToken")]]
    """Pagination token"""
