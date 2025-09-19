# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["WorkflowStartRunParams", "EnvVarOverride"]


class WorkflowStartRunParams(TypedDict, total=False):
    config_id: Required[Annotated[str, PropertyInfo(alias="configId")]]
    """ID of the workflow configuration to use"""

    env_var_overrides: Required[Annotated[Iterable[EnvVarOverride], PropertyInfo(alias="envVarOverrides")]]

    label_overrides: Required[Annotated[Dict[str, str], PropertyInfo(alias="labelOverrides")]]
    """Optional label overrides"""

    name: Required[str]
    """Optional name override for this run"""

    parameter_overrides: Required[Annotated[Dict[str, str], PropertyInfo(alias="parameterOverrides")]]
    """Optional parameter overrides"""


class EnvVarOverride(TypedDict, total=False):
    name: Required[str]

    value: Required[str]
