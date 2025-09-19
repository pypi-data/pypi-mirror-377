# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["WorkflowCreateConfigParams", "EnvVar"]


class WorkflowCreateConfigParams(TypedDict, total=False):
    env_vars: Required[Annotated[Iterable[EnvVar], PropertyInfo(alias="envVars")]]

    labels: Required[Dict[str, str]]
    """Labels/tags for the workflow"""

    name: Required[str]
    """Human-readable name for this workflow configuration"""

    parameters: Required[Dict[str, str]]
    """Additional configuration parameters"""


class EnvVar(TypedDict, total=False):
    name: Required[str]

    value: Required[str]
