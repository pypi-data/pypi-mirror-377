# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["WorkflowStopRunParams"]


class WorkflowStopRunParams(TypedDict, total=False):
    force: Required[bool]
    """Whether to force termination"""

    run_id: Required[Annotated[str, PropertyInfo(alias="runId")]]
    """Workflow run ID to stop"""
