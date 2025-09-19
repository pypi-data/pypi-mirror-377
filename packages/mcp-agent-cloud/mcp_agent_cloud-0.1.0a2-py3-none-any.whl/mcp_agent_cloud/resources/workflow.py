# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal

import httpx

from ..types import (
    workflow_stop_run_params,
    workflow_list_runs_params,
    workflow_start_run_params,
    workflow_get_config_params,
    workflow_list_configs_params,
    workflow_create_config_params,
    workflow_delete_config_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.workflow_stop_run_response import WorkflowStopRunResponse
from ..types.workflow_list_runs_response import WorkflowListRunsResponse
from ..types.workflow_start_run_response import WorkflowStartRunResponse
from ..types.workflow_get_config_response import WorkflowGetConfigResponse
from ..types.workflow_list_configs_response import WorkflowListConfigsResponse
from ..types.workflow_create_config_response import WorkflowCreateConfigResponse
from ..types.workflow_delete_config_response import WorkflowDeleteConfigResponse

__all__ = ["WorkflowResource", "AsyncWorkflowResource"]


class WorkflowResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WorkflowResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lastmile-ai/mcp-agent-cloud#accessing-raw-response-data-eg-headers
        """
        return WorkflowResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WorkflowResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lastmile-ai/mcp-agent-cloud#with_streaming_response
        """
        return WorkflowResourceWithStreamingResponse(self)

    def create_config(
        self,
        *,
        env_vars: Iterable[workflow_create_config_params.EnvVar],
        labels: Dict[str, str],
        name: str,
        parameters: Dict[str, str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowCreateConfigResponse:
        """
        Workflow Configuration Operations

        Args:
          labels: Labels/tags for the workflow

          name: Human-readable name for this workflow configuration

          parameters: Additional configuration parameters

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/workflow/create_config",
            body=maybe_transform(
                {
                    "env_vars": env_vars,
                    "labels": labels,
                    "name": name,
                    "parameters": parameters,
                },
                workflow_create_config_params.WorkflowCreateConfigParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowCreateConfigResponse,
        )

    def delete_config(
        self,
        *,
        config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowDeleteConfigResponse:
        """
        Description of delete_config

        Args:
          config_id: ID of the workflow configuration to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            "/api/workflow/delete_config",
            body=maybe_transform({"config_id": config_id}, workflow_delete_config_params.WorkflowDeleteConfigParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowDeleteConfigResponse,
        )

    def get_config(
        self,
        *,
        config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowGetConfigResponse:
        """
        Description of get_config

        Args:
          config_id: ID of the workflow configuration to retrieve

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/workflow/get_config",
            body=maybe_transform({"config_id": config_id}, workflow_get_config_params.WorkflowGetConfigParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowGetConfigResponse,
        )

    def list_configs(
        self,
        *,
        label_filter: Dict[str, str],
        max_results: int,
        page_token: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowListConfigsResponse:
        """
        Description of list_configs

        Args:
          label_filter: Filter by label

          max_results: Maximum number of results to return

          page_token: Pagination token

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/workflow/list_configs",
            body=maybe_transform(
                {
                    "label_filter": label_filter,
                    "max_results": max_results,
                    "page_token": page_token,
                },
                workflow_list_configs_params.WorkflowListConfigsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowListConfigsResponse,
        )

    def list_runs(
        self,
        *,
        config_id: str,
        label_filter: Dict[str, str],
        max_results: int,
        page_token: str,
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
        ],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowListRunsResponse:
        """
        Description of list_runs

        Args:
          config_id: Filter by config ID

          label_filter: Filter by label

          max_results: Maximum number of results to return

          page_token: Pagination token

          status: Filter by status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/workflow/list_runs",
            body=maybe_transform(
                {
                    "config_id": config_id,
                    "label_filter": label_filter,
                    "max_results": max_results,
                    "page_token": page_token,
                    "status": status,
                },
                workflow_list_runs_params.WorkflowListRunsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowListRunsResponse,
        )

    def start_run(
        self,
        *,
        config_id: str,
        env_var_overrides: Iterable[workflow_start_run_params.EnvVarOverride],
        label_overrides: Dict[str, str],
        name: str,
        parameter_overrides: Dict[str, str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowStartRunResponse:
        """
        Workflow Run Operations

        Args:
          config_id: ID of the workflow configuration to use

          label_overrides: Optional label overrides

          name: Optional name override for this run

          parameter_overrides: Optional parameter overrides

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/workflow/start_run",
            body=maybe_transform(
                {
                    "config_id": config_id,
                    "env_var_overrides": env_var_overrides,
                    "label_overrides": label_overrides,
                    "name": name,
                    "parameter_overrides": parameter_overrides,
                },
                workflow_start_run_params.WorkflowStartRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowStartRunResponse,
        )

    def stop_run(
        self,
        *,
        force: bool,
        run_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowStopRunResponse:
        """
        Description of stop_run

        Args:
          force: Whether to force termination

          run_id: Workflow run ID to stop

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/workflow/stop_run",
            body=maybe_transform(
                {
                    "force": force,
                    "run_id": run_id,
                },
                workflow_stop_run_params.WorkflowStopRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowStopRunResponse,
        )


class AsyncWorkflowResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWorkflowResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lastmile-ai/mcp-agent-cloud#accessing-raw-response-data-eg-headers
        """
        return AsyncWorkflowResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWorkflowResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lastmile-ai/mcp-agent-cloud#with_streaming_response
        """
        return AsyncWorkflowResourceWithStreamingResponse(self)

    async def create_config(
        self,
        *,
        env_vars: Iterable[workflow_create_config_params.EnvVar],
        labels: Dict[str, str],
        name: str,
        parameters: Dict[str, str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowCreateConfigResponse:
        """
        Workflow Configuration Operations

        Args:
          labels: Labels/tags for the workflow

          name: Human-readable name for this workflow configuration

          parameters: Additional configuration parameters

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/workflow/create_config",
            body=await async_maybe_transform(
                {
                    "env_vars": env_vars,
                    "labels": labels,
                    "name": name,
                    "parameters": parameters,
                },
                workflow_create_config_params.WorkflowCreateConfigParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowCreateConfigResponse,
        )

    async def delete_config(
        self,
        *,
        config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowDeleteConfigResponse:
        """
        Description of delete_config

        Args:
          config_id: ID of the workflow configuration to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            "/api/workflow/delete_config",
            body=await async_maybe_transform(
                {"config_id": config_id}, workflow_delete_config_params.WorkflowDeleteConfigParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowDeleteConfigResponse,
        )

    async def get_config(
        self,
        *,
        config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowGetConfigResponse:
        """
        Description of get_config

        Args:
          config_id: ID of the workflow configuration to retrieve

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/workflow/get_config",
            body=await async_maybe_transform(
                {"config_id": config_id}, workflow_get_config_params.WorkflowGetConfigParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowGetConfigResponse,
        )

    async def list_configs(
        self,
        *,
        label_filter: Dict[str, str],
        max_results: int,
        page_token: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowListConfigsResponse:
        """
        Description of list_configs

        Args:
          label_filter: Filter by label

          max_results: Maximum number of results to return

          page_token: Pagination token

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/workflow/list_configs",
            body=await async_maybe_transform(
                {
                    "label_filter": label_filter,
                    "max_results": max_results,
                    "page_token": page_token,
                },
                workflow_list_configs_params.WorkflowListConfigsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowListConfigsResponse,
        )

    async def list_runs(
        self,
        *,
        config_id: str,
        label_filter: Dict[str, str],
        max_results: int,
        page_token: str,
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
        ],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowListRunsResponse:
        """
        Description of list_runs

        Args:
          config_id: Filter by config ID

          label_filter: Filter by label

          max_results: Maximum number of results to return

          page_token: Pagination token

          status: Filter by status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/workflow/list_runs",
            body=await async_maybe_transform(
                {
                    "config_id": config_id,
                    "label_filter": label_filter,
                    "max_results": max_results,
                    "page_token": page_token,
                    "status": status,
                },
                workflow_list_runs_params.WorkflowListRunsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowListRunsResponse,
        )

    async def start_run(
        self,
        *,
        config_id: str,
        env_var_overrides: Iterable[workflow_start_run_params.EnvVarOverride],
        label_overrides: Dict[str, str],
        name: str,
        parameter_overrides: Dict[str, str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowStartRunResponse:
        """
        Workflow Run Operations

        Args:
          config_id: ID of the workflow configuration to use

          label_overrides: Optional label overrides

          name: Optional name override for this run

          parameter_overrides: Optional parameter overrides

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/workflow/start_run",
            body=await async_maybe_transform(
                {
                    "config_id": config_id,
                    "env_var_overrides": env_var_overrides,
                    "label_overrides": label_overrides,
                    "name": name,
                    "parameter_overrides": parameter_overrides,
                },
                workflow_start_run_params.WorkflowStartRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowStartRunResponse,
        )

    async def stop_run(
        self,
        *,
        force: bool,
        run_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowStopRunResponse:
        """
        Description of stop_run

        Args:
          force: Whether to force termination

          run_id: Workflow run ID to stop

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/workflow/stop_run",
            body=await async_maybe_transform(
                {
                    "force": force,
                    "run_id": run_id,
                },
                workflow_stop_run_params.WorkflowStopRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowStopRunResponse,
        )


class WorkflowResourceWithRawResponse:
    def __init__(self, workflow: WorkflowResource) -> None:
        self._workflow = workflow

        self.create_config = to_raw_response_wrapper(
            workflow.create_config,
        )
        self.delete_config = to_raw_response_wrapper(
            workflow.delete_config,
        )
        self.get_config = to_raw_response_wrapper(
            workflow.get_config,
        )
        self.list_configs = to_raw_response_wrapper(
            workflow.list_configs,
        )
        self.list_runs = to_raw_response_wrapper(
            workflow.list_runs,
        )
        self.start_run = to_raw_response_wrapper(
            workflow.start_run,
        )
        self.stop_run = to_raw_response_wrapper(
            workflow.stop_run,
        )


class AsyncWorkflowResourceWithRawResponse:
    def __init__(self, workflow: AsyncWorkflowResource) -> None:
        self._workflow = workflow

        self.create_config = async_to_raw_response_wrapper(
            workflow.create_config,
        )
        self.delete_config = async_to_raw_response_wrapper(
            workflow.delete_config,
        )
        self.get_config = async_to_raw_response_wrapper(
            workflow.get_config,
        )
        self.list_configs = async_to_raw_response_wrapper(
            workflow.list_configs,
        )
        self.list_runs = async_to_raw_response_wrapper(
            workflow.list_runs,
        )
        self.start_run = async_to_raw_response_wrapper(
            workflow.start_run,
        )
        self.stop_run = async_to_raw_response_wrapper(
            workflow.stop_run,
        )


class WorkflowResourceWithStreamingResponse:
    def __init__(self, workflow: WorkflowResource) -> None:
        self._workflow = workflow

        self.create_config = to_streamed_response_wrapper(
            workflow.create_config,
        )
        self.delete_config = to_streamed_response_wrapper(
            workflow.delete_config,
        )
        self.get_config = to_streamed_response_wrapper(
            workflow.get_config,
        )
        self.list_configs = to_streamed_response_wrapper(
            workflow.list_configs,
        )
        self.list_runs = to_streamed_response_wrapper(
            workflow.list_runs,
        )
        self.start_run = to_streamed_response_wrapper(
            workflow.start_run,
        )
        self.stop_run = to_streamed_response_wrapper(
            workflow.stop_run,
        )


class AsyncWorkflowResourceWithStreamingResponse:
    def __init__(self, workflow: AsyncWorkflowResource) -> None:
        self._workflow = workflow

        self.create_config = async_to_streamed_response_wrapper(
            workflow.create_config,
        )
        self.delete_config = async_to_streamed_response_wrapper(
            workflow.delete_config,
        )
        self.get_config = async_to_streamed_response_wrapper(
            workflow.get_config,
        )
        self.list_configs = async_to_streamed_response_wrapper(
            workflow.list_configs,
        )
        self.list_runs = async_to_streamed_response_wrapper(
            workflow.list_runs,
        )
        self.start_run = async_to_streamed_response_wrapper(
            workflow.start_run,
        )
        self.stop_run = async_to_streamed_response_wrapper(
            workflow.stop_run,
        )
