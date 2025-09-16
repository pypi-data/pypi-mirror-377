"""WaveSpeed API client base class."""

import time
import requests
import logging
from typing import Dict, Any

from wavespeed_mcp.exceptions import (
    WavespeedAuthError,
    WavespeedRequestError,
    WavespeedTimeoutError,
)
from wavespeed_mcp.const import API_PREDICTION_ENDPOINT

logger = logging.getLogger("wavespeed-client")


class WavespeedAPIClient:
    """Base client for making requests to WaveSpeed API."""

    def __init__(self, api_key: str, api_host: str):
        """Initialize the API client.

        Args:
            api_key: The API key for authentication
            api_host: The API host URL
        """
        self.api_key = api_key
        self.api_host = api_host
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the WaveSpeed API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            API response data as dictionary

        Raises:
            WavespeedAuthError: If authentication fails
            WavespeedRequestError: If the request fails
        """
        host = self.api_host.rstrip("/")
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        url = f"{host}{path}"

        logger.debug(f"Making {method} request to {url}")

        # Add timeout to prevent hanging
        if 'timeout' not in kwargs:
            from wavespeed_mcp.const import DEFAULT_REQUEST_TIMEOUT, ENV_WAVESPEED_REQUEST_TIMEOUT
            import os
            timeout = int(os.getenv(ENV_WAVESPEED_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT))
            kwargs['timeout'] = timeout

        response = None
        try:
            response = self.session.request(method, url, **kwargs)

            # Check for HTTP errors
            response.raise_for_status()

            data = response.json()

            # Check for API-specific errors
            if "error" in data:
                error_msg = data.get("error", "Unknown API error")
                raise WavespeedRequestError(f"API Error: {error_msg}")

            return data

        except requests.exceptions.Timeout:
            timeout = kwargs.get('timeout', 300)
            raise WavespeedTimeoutError(f"Request to {url} timed out after {timeout} seconds")
        except requests.exceptions.RequestException as e:
            if response is not None:
                if response.status_code == 401:
                    raise WavespeedAuthError(f"Authentication failed: {str(e)}")
                if hasattr(response, 'text') and response.text:
                    raise WavespeedRequestError(f"Request failed: {response.text}")
            raise WavespeedRequestError(f"Request failed: {str(e)}")

    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, **kwargs)

    def poll_result(
        self, wavespeed_request_id: str, max_retries: int = -1, poll_interval: float = 0.5, request_id: str = None
    ) -> Dict[str, Any]:
        """Poll for the result of an asynchronous API request.

        Args:
            wavespeed_request_id: The WaveSpeed API request ID to poll for
            max_retries: Maximum number of polling attempts. -1 for infinite retries.
            poll_interval: Time in seconds between polling attempts
            request_id: Optional MCP request ID for logging correlation

        Returns:
            The final result of the API request

        Raises:
            WavespeedTimeoutError: If polling exceeds max_retries
            WavespeedRequestError: If the request fails
        """
        result_url = f"{API_PREDICTION_ENDPOINT}/{wavespeed_request_id}/result"

        attempt = 0

        log_prefix = f"[{request_id}]" if request_id else ""
        logger.info(f"{log_prefix} Starting API polling for WaveSpeed ID: {wavespeed_request_id}")

        start_time = time.time()

        while True:
            if max_retries != -1 and attempt >= max_retries:
                elapsed = time.time() - start_time
                logger.error(
                    f"{log_prefix} API polling timed out after {max_retries} attempts ({elapsed:.1f}s)"
                )
                raise WavespeedTimeoutError(f"Polling timed out after {max_retries} attempts")
                break

            try:
                # Reduce log frequency - only log every 20 attempts (10 seconds)
                if attempt % 20 == 0 and attempt > 0:
                    logger.debug(
                        f"{log_prefix} Polling attempt {attempt+1}/{max_retries if max_retries != -1 else '∞'} ({time.time() - start_time:.1f}s elapsed)"
                    )

                response = self.get(result_url)
                result = response.get("data", {})
                status = result.get("status")

                # Only log status changes, not every poll
                if not hasattr(self, '_last_status') or self._last_status != status:
                    logger.debug(f"{log_prefix} Status changed to: {status}")
                    self._last_status = status

                if status == "completed":
                    elapsed = time.time() - start_time
                    logger.info(
                        f"{log_prefix} API polling completed after {attempt+1} attempts ({elapsed:.1f}s)"
                    )
                    return result
                elif status == "failed":
                    elapsed = time.time() - start_time
                    logger.error(
                        f"{log_prefix} API polling failed after {attempt+1} attempts ({elapsed:.1f}s)"
                    )
                    error = result.get("error", "unknown error")
                    raise WavespeedRequestError(f"API request failed: {error}")

                # If still processing, wait and try again
                time.sleep(poll_interval)
                attempt += 1

            except WavespeedRequestError as e:
                # If it's a request error, re-raise it
                elapsed = time.time() - start_time
                logger.error(f"{log_prefix} Request failed: {str(e)}")
                raise
            except Exception as e:
                # For other exceptions, log and continue polling
                logger.warning(f"{log_prefix} Error during polling: {str(e)}")

        # If we've exhausted all retries
        elapsed = time.time() - start_time
        logger.error(
            f"{log_prefix} API polling timed out after {max_retries} attempts ({elapsed:.1f}s)"
        )
        raise WavespeedTimeoutError(f"Polling timed out after {max_retries} attempts")
