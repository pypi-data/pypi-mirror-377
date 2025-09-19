# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["WorkflowDeleteConfigResponse"]


class WorkflowDeleteConfigResponse(BaseModel):
    config_id: str = FieldInfo(alias="configId")
    """ID of the deleted workflow configuration"""
