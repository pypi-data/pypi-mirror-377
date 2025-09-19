# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["WorkflowListRunsParams"]


class WorkflowListRunsParams(TypedDict, total=False):
    config_id: Required[Annotated[str, PropertyInfo(alias="configId")]]
    """Filter by config ID"""

    label_filter: Required[Annotated[Dict[str, str], PropertyInfo(alias="labelFilter")]]
    """Filter by label"""

    max_results: Required[Annotated[int, PropertyInfo(alias="maxResults")]]
    """Maximum number of results to return"""

    page_token: Required[Annotated[str, PropertyInfo(alias="pageToken")]]
    """Pagination token"""

    status: Required[
        Literal[
            "WORKFLOW_RUN_STATUS_UNSPECIFIED",
            "WORKFLOW_RUN_STATUS_PENDING",
            "WORKFLOW_RUN_STATUS_DEPLOYING",
            "WORKFLOW_RUN_STATUS_RUNNING",
            "WORKFLOW_RUN_STATUS_DEGRADED",
            "WORKFLOW_RUN_STATUS_STOPPING",
            "WORKFLOW_RUN_STATUS_STOPPED",
            "WORKFLOW_RUN_STATUS_FAILED",
            "WORKFLOW_RUN_STATUS_COMPLETED",
            "WORKFLOW_RUN_STATUS_PAUSED",
        ]
    ]
    """Filter by status"""
