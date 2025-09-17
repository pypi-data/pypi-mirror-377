import logging
import time
from typing import Any
from uuid import UUID

import httpx
from httpx import Response
from pydantic import HttpUrl, SecretStr

from .api import ApiError
from .config import Config, print_config_error_help
from .models import QECExperiment

logger = logging.getLogger(__package__)


class LoomClient:
    def __init__(
        self,
        api_url: str | HttpUrl | None = None,
        api_token: str | SecretStr | None = None,
    ):
        if isinstance(api_token, str):
            api_token = SecretStr(api_token)

        if isinstance(api_url, str):
            api_url = HttpUrl(api_url)

        kwargs = {}
        if api_token is not None:
            kwargs["api_token"] = api_token
        if api_url is not None:
            kwargs["api_url"] = api_url

        self._config: Config = Config(**kwargs)

        if not self._config.api_url or not self._config.api_token:
            print_config_error_help()

            raise ValueError("API URL and token must be set via env or config")

    ################################################################################################
    ## INTERNALS
    ################################################################################################

    def __endpoint_url(self, endpoint: str) -> str:
        """
        Constructs the absolute URL for a given API endpoint.
        """
        # Sanity check: we already check this in __init__
        assert self._config.api_url, "Loom API URL must be set"

        endpoint = endpoint.lstrip("/")
        base_url = str(self._config.api_url).rstrip("/")

        return f"{base_url}/{endpoint}"

    def __default_request_headers(self) -> dict[str, str]:
        if self._config.api_token is None:
            raise ValueError("Loom API token must be set")

        api_token = self._config.api_token.get_secret_value()

        return {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def __get(self, endpoint: str, params: dict[str, Any] | None = None) -> Response:
        return httpx.get(
            url=self.__endpoint_url(endpoint),
            headers=self.__default_request_headers(),
            params=params,
        )

    async def __get_async(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Response:
        return await client.get(
            url=self.__endpoint_url(endpoint),
            headers=self.__default_request_headers(),
            params=params,
        )

    def __post(
        self, endpoint: str, data: dict[str, Any] | str | None = None
    ) -> Response:
        """
        Post data to the Loom API.

        Accepted data types:
            - dict[str, Any]: Will be converted to a JSON payload
            - str: JSON string (will be sent as raw data with correct content type)

        Raises:
            ValueError: If the Loom API URL is not set.
        """
        url = self.__endpoint_url(endpoint)

        if isinstance(data, str):
            # If data is a JSON string, pass it directly as raw text, headers will set content type
            return httpx.post(
                url=url, headers=self.__default_request_headers(), content=data
            )
        else:
            # If data is a dict or None, use json parameter from `requests`
            return httpx.post(
                url=url, headers=self.__default_request_headers(), json=data
            )

    def __is_completed_state(self, state: str) -> bool:
        """
        Check if the given state indicates a completed run
        """
        return state in ["Completed"]

    def __raise_for_failure_state(
        self,
        run_id: UUID,
        status_response: dict[str, Any],
    ):
        """
        Raise an exception if the run is in a cancelling, cancelled or failure states.

        Args:
            state: Current state of the run
            run_id: UUID of the experiment run
            start_time: Time when the run started (extra context for timeout error reporting)
        Raises:
            RuntimeError: If the run is in a failure state
            TimeoutError: If the run has timed out
        """

        state = status_response.get("state")
        failed_reason = status_response.get("reason")

        match state:
            case "Cancelling":
                raise RuntimeError(f"Experiment run '{run_id}' is being cancelled")
            case "Cancelled":
                raise RuntimeError(f"Experiment run '{run_id}' was cancelled")
            case "Failed":
                if isinstance(failed_reason, str):
                    raise RuntimeError(
                        f"Experiment run '{run_id}' failed: {failed_reason}"
                    )

                raise RuntimeError(
                    f"Experiment run '{run_id}' failed due an internal error"
                )
            case "Scheduled" | "Pending" | "Running" | "Paused" | "Completed":
                return
            case _:
                raise RuntimeError(
                    f"Experiment run '{run_id}' is in unexpected state '{state}'"
                )

    def __raise_for_timeout(self, start_time: float, timeout: int):
        """
        Raise a TimeoutError if the run has exceeded the specified timeout.
        Args:
            start_time: Time when the run started
            timeout: Timeout in seconds
        Raises:
            TimeoutError: If the run has exceeded the timeout
        """
        if (time.time() - start_time) > timeout:
            raise TimeoutError(f"The request timed out after {timeout} seconds")

    def __raise_for_error_response(self, response: Response):
        """
        Raise an ApiError or HTTPStatusError if the response indicates an error.

        Use this instead of response.raise_for_status() to handle API-specific errors.

        Args:
            response: HTTP response object
        Raises:
            ApiError: If the response indicates an API error (client or server error)
            HTTPStatusError: If the response is indicates other HTTP errors
        """

        # Catch and convert HTTPStatusError (only client or server errors)
        if response.is_client_error or response.is_server_error:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as http_status_error:
                raise ApiError(http_status_error)

        # Fallback
        response.raise_for_status()

    ################################################################################################
    ## PUBLIC METHODS
    ################################################################################################

    def experiment_run(self, experiment: QECExperiment) -> UUID:
        """
        Submit a memory experiment run to the Loom API.
        """

        response = self.__post("/experiment_run/", experiment.model_dump())
        # Handle errors
        self.__raise_for_error_response(response)

        result = response.json()
        return UUID(result.get("run_id"))

    def get_experiment_run_status(self, run_id: UUID) -> dict[str, Any]:
        """
        Get the status of a specific experiment run by its ID.

        Args:
            run_id: UUID of the experiment run

        Returns:
            JSON object containing the run status
        """

        response = self.__get(f"/experiment_run/{run_id}")
        self.__raise_for_error_response(response)

        return response.json()

    def get_experiment_run_result(self, run_id: UUID) -> dict[str, Any]:
        """
        Get the result of a specific experiment run by its ID. Will return a 404 (not found) status
        error if no result is present for the given run ID.

        Use the `get_experiment_run_status` method first, to check the progress of the run.

        Args:
            run_id: UUID of the experiment run

        Returns:
            JSON object containing the run result or raises a 404 error if the result doesn't exist.
        """

        response = self.__get(f"/experiment_run/{run_id}/result")
        self.__raise_for_error_response(response)

        return response.json()

    def get_result_sync(
        self, run_id: UUID, timeout: int | None = None
    ) -> dict[str, Any]:
        """
        Synchronously wait for and retrieve the result of an experiment run.
        This method blocks until the run is completed or fails.

        Args:
            run_id: UUID of the experiment run
            timeout: Optional timeout in seconds. If None, will wait indefinitely.

        Returns:
            JSON object containing the run result
        Raises:
            RuntimeError: If the experiment run fails or crashes
            TimeoutError: If the timeout is reached before the run completes
        """

        start_time = time.time()

        while True:
            # Get the current status
            status: dict[str, Any] = self.get_experiment_run_status(run_id)
            state = status.get("state")
            assert isinstance(state, str)

            logger.debug(f"Experiment run '{run_id}' current status: {state}")

            # Raise for failure state
            self.__raise_for_failure_state(
                run_id=run_id,
                status_response=status,
            )

            # Raise for user provided timeout
            if timeout is not None:
                self.__raise_for_timeout(start_time, timeout)

            # Check if the run is completed
            if self.__is_completed_state(state):
                # Get and return the result
                return self.get_experiment_run_result(run_id)

            # Wait
            time.sleep(1)

    async def get_result_async(
        self, run_id: UUID, timeout: int | None = None
    ) -> dict[str, Any]:
        """
        Asynchronously wait for and retrieve the result of an experiment run.

        This is the non-blocking version of get_result_sync.

        Args:
            run_id: UUID of the experiment run
            timeout: Optional timeout in seconds

        Returns:
            JSON object containing the run result

        Raises:
            RuntimeError: If the experiment run fails or crashes
            TimeoutError: If the timeout is reached before the run completes
        """

        import asyncio
        import time

        import httpx

        start_time = time.time()

        # Create HTTP client for async requests
        async with httpx.AsyncClient() as client:
            while True:
                # Get the current status
                response = await self.__get_async(client, f"/experiment_run/{run_id}")
                self.__raise_for_error_response(response)

                status: dict[str, Any] = response.json()
                state = status.get("state")
                assert isinstance(state, str)

                logger.debug(f"Experiment run '{run_id}' current status: {state}")

                # Raise for experiment failure state
                self.__raise_for_failure_state(
                    run_id=run_id,
                    status_response=status,
                )

                # Raise for user provided timeout
                if timeout is not None:
                    self.__raise_for_timeout(start_time, timeout)

                # Check if the run is completed
                if self.__is_completed_state(state):
                    # Get and return the result
                    response = await self.__get_async(
                        client, f"/experiment_run/{run_id}/result"
                    )
                    self.__raise_for_error_response(response)

                    return response.json()

                # Non-blocking sleep
                await asyncio.sleep(1)
