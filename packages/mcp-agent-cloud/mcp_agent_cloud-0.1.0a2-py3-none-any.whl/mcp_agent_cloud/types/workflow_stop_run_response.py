# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["WorkflowStopRunResponse"]


class WorkflowStopRunResponse(BaseModel):
    run_id: str = FieldInfo(alias="runId")
    """Workflow run ID that was stopped"""

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
    """Final status of the workflow run"""
