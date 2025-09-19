# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["WorkflowListConfigsResponse", "Config", "ConfigEnvVar"]


class ConfigEnvVar(BaseModel):
    name: str

    value: str


class Config(BaseModel):
    config_id: str = FieldInfo(alias="configId")
    """Unique ID for this Workflow configuration"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Completion timestamp (when execution completed, failed, or was terminated)"""

    env_vars: List[ConfigEnvVar] = FieldInfo(alias="envVars")

    labels: Dict[str, str]
    """Labels/tags for the Workflow"""

    name: str
    """Human-readable name for this Workflow configuration"""

    parameters: Dict[str, str]
    """Additional configuration parameters"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Completion timestamp (when execution completed, failed, or was terminated)"""


class WorkflowListConfigsResponse(BaseModel):
    configs: List[Config]

    next_page_token: str = FieldInfo(alias="nextPageToken")
    """Pagination token for next page"""

    total_count: int = FieldInfo(alias="totalCount")
    """Total count of configurations matching the filter"""
