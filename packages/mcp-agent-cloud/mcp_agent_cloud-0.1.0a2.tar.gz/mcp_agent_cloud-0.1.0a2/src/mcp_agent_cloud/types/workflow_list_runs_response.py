# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["WorkflowListRunsResponse", "Run"]


class Run(BaseModel):
    completed_at: datetime = FieldInfo(alias="completedAt")
    """Completion timestamp (when execution completed, failed, or was terminated)"""

    config_id: str = FieldInfo(alias="configId")
    """ID of the Workflow configuration used"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Completion timestamp (when execution completed, failed, or was terminated)"""

    labels: Dict[str, str]
    """Labels/tags for the Workflow run"""

    metadata: Dict[str, str]
    """Additional metadata about the Workflow run"""

    name: str
    """Human-readable name"""

    principal_id: str = FieldInfo(alias="principalId")
    """Principal (user or service) that started this workflow run"""

    run_id: str = FieldInfo(alias="runId")
    """Unique ID for this Workflow run"""

    started_at: datetime = FieldInfo(alias="startedAt")
    """Completion timestamp (when execution completed, failed, or was terminated)"""

    status: Literal[
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
    """Workflow run status"""


class WorkflowListRunsResponse(BaseModel):
    next_page_token: str = FieldInfo(alias="nextPageToken")
    """Pagination token for next page"""

    runs: List[Run]

    total_count: int = FieldInfo(alias="totalCount")
    """Total count of runs matching the filter"""
