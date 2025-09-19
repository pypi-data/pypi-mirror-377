# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["WorkflowDeleteConfigParams"]


class WorkflowDeleteConfigParams(TypedDict, total=False):
    config_id: Required[Annotated[str, PropertyInfo(alias="configId")]]
    """ID of the workflow configuration to delete"""
