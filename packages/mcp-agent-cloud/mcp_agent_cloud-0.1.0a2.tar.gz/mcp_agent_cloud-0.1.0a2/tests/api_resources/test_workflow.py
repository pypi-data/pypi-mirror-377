# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from mcp_agent_cloud import MCPAgentCloud, AsyncMCPAgentCloud
from mcp_agent_cloud.types import (
    WorkflowStopRunResponse,
    WorkflowListRunsResponse,
    WorkflowStartRunResponse,
    WorkflowGetConfigResponse,
    WorkflowListConfigsResponse,
    WorkflowCreateConfigResponse,
    WorkflowDeleteConfigResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWorkflow:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_config(self, client: MCPAgentCloud) -> None:
        workflow = client.workflow.create_config(
            env_vars=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            labels={"foo": "string"},
            name="name",
            parameters={"foo": "string"},
        )
        assert_matches_type(WorkflowCreateConfigResponse, workflow, path=["response"])

    @parametrize
    def test_raw_response_create_config(self, client: MCPAgentCloud) -> None:
        response = client.workflow.with_raw_response.create_config(
            env_vars=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            labels={"foo": "string"},
            name="name",
            parameters={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = response.parse()
        assert_matches_type(WorkflowCreateConfigResponse, workflow, path=["response"])

    @parametrize
    def test_streaming_response_create_config(self, client: MCPAgentCloud) -> None:
        with client.workflow.with_streaming_response.create_config(
            env_vars=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            labels={"foo": "string"},
            name="name",
            parameters={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = response.parse()
            assert_matches_type(WorkflowCreateConfigResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete_config(self, client: MCPAgentCloud) -> None:
        workflow = client.workflow.delete_config(
            config_id="configId",
        )
        assert_matches_type(WorkflowDeleteConfigResponse, workflow, path=["response"])

    @parametrize
    def test_raw_response_delete_config(self, client: MCPAgentCloud) -> None:
        response = client.workflow.with_raw_response.delete_config(
            config_id="configId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = response.parse()
        assert_matches_type(WorkflowDeleteConfigResponse, workflow, path=["response"])

    @parametrize
    def test_streaming_response_delete_config(self, client: MCPAgentCloud) -> None:
        with client.workflow.with_streaming_response.delete_config(
            config_id="configId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = response.parse()
            assert_matches_type(WorkflowDeleteConfigResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_config(self, client: MCPAgentCloud) -> None:
        workflow = client.workflow.get_config(
            config_id="configId",
        )
        assert_matches_type(WorkflowGetConfigResponse, workflow, path=["response"])

    @parametrize
    def test_raw_response_get_config(self, client: MCPAgentCloud) -> None:
        response = client.workflow.with_raw_response.get_config(
            config_id="configId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = response.parse()
        assert_matches_type(WorkflowGetConfigResponse, workflow, path=["response"])

    @parametrize
    def test_streaming_response_get_config(self, client: MCPAgentCloud) -> None:
        with client.workflow.with_streaming_response.get_config(
            config_id="configId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = response.parse()
            assert_matches_type(WorkflowGetConfigResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_configs(self, client: MCPAgentCloud) -> None:
        workflow = client.workflow.list_configs(
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
        )
        assert_matches_type(WorkflowListConfigsResponse, workflow, path=["response"])

    @parametrize
    def test_raw_response_list_configs(self, client: MCPAgentCloud) -> None:
        response = client.workflow.with_raw_response.list_configs(
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = response.parse()
        assert_matches_type(WorkflowListConfigsResponse, workflow, path=["response"])

    @parametrize
    def test_streaming_response_list_configs(self, client: MCPAgentCloud) -> None:
        with client.workflow.with_streaming_response.list_configs(
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = response.parse()
            assert_matches_type(WorkflowListConfigsResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_runs(self, client: MCPAgentCloud) -> None:
        workflow = client.workflow.list_runs(
            config_id="configId",
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
            status="WORKFLOW_RUN_STATUS_UNSPECIFIED",
        )
        assert_matches_type(WorkflowListRunsResponse, workflow, path=["response"])

    @parametrize
    def test_raw_response_list_runs(self, client: MCPAgentCloud) -> None:
        response = client.workflow.with_raw_response.list_runs(
            config_id="configId",
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
            status="WORKFLOW_RUN_STATUS_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = response.parse()
        assert_matches_type(WorkflowListRunsResponse, workflow, path=["response"])

    @parametrize
    def test_streaming_response_list_runs(self, client: MCPAgentCloud) -> None:
        with client.workflow.with_streaming_response.list_runs(
            config_id="configId",
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
            status="WORKFLOW_RUN_STATUS_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = response.parse()
            assert_matches_type(WorkflowListRunsResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_start_run(self, client: MCPAgentCloud) -> None:
        workflow = client.workflow.start_run(
            config_id="configId",
            env_var_overrides=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            label_overrides={"foo": "string"},
            name="name",
            parameter_overrides={"foo": "string"},
        )
        assert_matches_type(WorkflowStartRunResponse, workflow, path=["response"])

    @parametrize
    def test_raw_response_start_run(self, client: MCPAgentCloud) -> None:
        response = client.workflow.with_raw_response.start_run(
            config_id="configId",
            env_var_overrides=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            label_overrides={"foo": "string"},
            name="name",
            parameter_overrides={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = response.parse()
        assert_matches_type(WorkflowStartRunResponse, workflow, path=["response"])

    @parametrize
    def test_streaming_response_start_run(self, client: MCPAgentCloud) -> None:
        with client.workflow.with_streaming_response.start_run(
            config_id="configId",
            env_var_overrides=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            label_overrides={"foo": "string"},
            name="name",
            parameter_overrides={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = response.parse()
            assert_matches_type(WorkflowStartRunResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_stop_run(self, client: MCPAgentCloud) -> None:
        workflow = client.workflow.stop_run(
            force=True,
            run_id="runId",
        )
        assert_matches_type(WorkflowStopRunResponse, workflow, path=["response"])

    @parametrize
    def test_raw_response_stop_run(self, client: MCPAgentCloud) -> None:
        response = client.workflow.with_raw_response.stop_run(
            force=True,
            run_id="runId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = response.parse()
        assert_matches_type(WorkflowStopRunResponse, workflow, path=["response"])

    @parametrize
    def test_streaming_response_stop_run(self, client: MCPAgentCloud) -> None:
        with client.workflow.with_streaming_response.stop_run(
            force=True,
            run_id="runId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = response.parse()
            assert_matches_type(WorkflowStopRunResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncWorkflow:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create_config(self, async_client: AsyncMCPAgentCloud) -> None:
        workflow = await async_client.workflow.create_config(
            env_vars=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            labels={"foo": "string"},
            name="name",
            parameters={"foo": "string"},
        )
        assert_matches_type(WorkflowCreateConfigResponse, workflow, path=["response"])

    @parametrize
    async def test_raw_response_create_config(self, async_client: AsyncMCPAgentCloud) -> None:
        response = await async_client.workflow.with_raw_response.create_config(
            env_vars=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            labels={"foo": "string"},
            name="name",
            parameters={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = await response.parse()
        assert_matches_type(WorkflowCreateConfigResponse, workflow, path=["response"])

    @parametrize
    async def test_streaming_response_create_config(self, async_client: AsyncMCPAgentCloud) -> None:
        async with async_client.workflow.with_streaming_response.create_config(
            env_vars=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            labels={"foo": "string"},
            name="name",
            parameters={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = await response.parse()
            assert_matches_type(WorkflowCreateConfigResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete_config(self, async_client: AsyncMCPAgentCloud) -> None:
        workflow = await async_client.workflow.delete_config(
            config_id="configId",
        )
        assert_matches_type(WorkflowDeleteConfigResponse, workflow, path=["response"])

    @parametrize
    async def test_raw_response_delete_config(self, async_client: AsyncMCPAgentCloud) -> None:
        response = await async_client.workflow.with_raw_response.delete_config(
            config_id="configId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = await response.parse()
        assert_matches_type(WorkflowDeleteConfigResponse, workflow, path=["response"])

    @parametrize
    async def test_streaming_response_delete_config(self, async_client: AsyncMCPAgentCloud) -> None:
        async with async_client.workflow.with_streaming_response.delete_config(
            config_id="configId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = await response.parse()
            assert_matches_type(WorkflowDeleteConfigResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_config(self, async_client: AsyncMCPAgentCloud) -> None:
        workflow = await async_client.workflow.get_config(
            config_id="configId",
        )
        assert_matches_type(WorkflowGetConfigResponse, workflow, path=["response"])

    @parametrize
    async def test_raw_response_get_config(self, async_client: AsyncMCPAgentCloud) -> None:
        response = await async_client.workflow.with_raw_response.get_config(
            config_id="configId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = await response.parse()
        assert_matches_type(WorkflowGetConfigResponse, workflow, path=["response"])

    @parametrize
    async def test_streaming_response_get_config(self, async_client: AsyncMCPAgentCloud) -> None:
        async with async_client.workflow.with_streaming_response.get_config(
            config_id="configId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = await response.parse()
            assert_matches_type(WorkflowGetConfigResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_configs(self, async_client: AsyncMCPAgentCloud) -> None:
        workflow = await async_client.workflow.list_configs(
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
        )
        assert_matches_type(WorkflowListConfigsResponse, workflow, path=["response"])

    @parametrize
    async def test_raw_response_list_configs(self, async_client: AsyncMCPAgentCloud) -> None:
        response = await async_client.workflow.with_raw_response.list_configs(
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = await response.parse()
        assert_matches_type(WorkflowListConfigsResponse, workflow, path=["response"])

    @parametrize
    async def test_streaming_response_list_configs(self, async_client: AsyncMCPAgentCloud) -> None:
        async with async_client.workflow.with_streaming_response.list_configs(
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = await response.parse()
            assert_matches_type(WorkflowListConfigsResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_runs(self, async_client: AsyncMCPAgentCloud) -> None:
        workflow = await async_client.workflow.list_runs(
            config_id="configId",
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
            status="WORKFLOW_RUN_STATUS_UNSPECIFIED",
        )
        assert_matches_type(WorkflowListRunsResponse, workflow, path=["response"])

    @parametrize
    async def test_raw_response_list_runs(self, async_client: AsyncMCPAgentCloud) -> None:
        response = await async_client.workflow.with_raw_response.list_runs(
            config_id="configId",
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
            status="WORKFLOW_RUN_STATUS_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = await response.parse()
        assert_matches_type(WorkflowListRunsResponse, workflow, path=["response"])

    @parametrize
    async def test_streaming_response_list_runs(self, async_client: AsyncMCPAgentCloud) -> None:
        async with async_client.workflow.with_streaming_response.list_runs(
            config_id="configId",
            label_filter={"foo": "string"},
            max_results=0,
            page_token="pageToken",
            status="WORKFLOW_RUN_STATUS_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = await response.parse()
            assert_matches_type(WorkflowListRunsResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_start_run(self, async_client: AsyncMCPAgentCloud) -> None:
        workflow = await async_client.workflow.start_run(
            config_id="configId",
            env_var_overrides=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            label_overrides={"foo": "string"},
            name="name",
            parameter_overrides={"foo": "string"},
        )
        assert_matches_type(WorkflowStartRunResponse, workflow, path=["response"])

    @parametrize
    async def test_raw_response_start_run(self, async_client: AsyncMCPAgentCloud) -> None:
        response = await async_client.workflow.with_raw_response.start_run(
            config_id="configId",
            env_var_overrides=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            label_overrides={"foo": "string"},
            name="name",
            parameter_overrides={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = await response.parse()
        assert_matches_type(WorkflowStartRunResponse, workflow, path=["response"])

    @parametrize
    async def test_streaming_response_start_run(self, async_client: AsyncMCPAgentCloud) -> None:
        async with async_client.workflow.with_streaming_response.start_run(
            config_id="configId",
            env_var_overrides=[
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            label_overrides={"foo": "string"},
            name="name",
            parameter_overrides={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = await response.parse()
            assert_matches_type(WorkflowStartRunResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_stop_run(self, async_client: AsyncMCPAgentCloud) -> None:
        workflow = await async_client.workflow.stop_run(
            force=True,
            run_id="runId",
        )
        assert_matches_type(WorkflowStopRunResponse, workflow, path=["response"])

    @parametrize
    async def test_raw_response_stop_run(self, async_client: AsyncMCPAgentCloud) -> None:
        response = await async_client.workflow.with_raw_response.stop_run(
            force=True,
            run_id="runId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workflow = await response.parse()
        assert_matches_type(WorkflowStopRunResponse, workflow, path=["response"])

    @parametrize
    async def test_streaming_response_stop_run(self, async_client: AsyncMCPAgentCloud) -> None:
        async with async_client.workflow.with_streaming_response.stop_run(
            force=True,
            run_id="runId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workflow = await response.parse()
            assert_matches_type(WorkflowStopRunResponse, workflow, path=["response"])

        assert cast(Any, response.is_closed) is True
