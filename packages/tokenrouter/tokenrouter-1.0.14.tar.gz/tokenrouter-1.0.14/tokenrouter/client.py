"""
TokenRouter SDK Client
OpenAI Responses API Compatible
"""

import os
import json
import time
import asyncio
from typing import Optional, Dict, Any, List, Union, AsyncIterator, Iterator
import httpx
from httpx import Response as HTTPResponse, HTTPStatusError

from .models import (
    Response,
    ResponseStreamEvent,
    InputItemsList,
    Usage,
    OutputItem,
    OutputContent,
    ContentItem,
    InputItem,
)
from .exceptions import (
    TokenRouterError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    APIConnectionError,
    APIStatusError,
    TimeoutError,
    QuotaExceededError,
)


class ResponsesNamespace:
    """Namespace for responses API endpoints"""

    def __init__(self, client: "BaseClient"):
        self.client = client

    def create(
        self,
        *,
        input: Optional[Union[str, List[Dict[str, Any]]]] = None,
        instructions: Optional[str] = None,
        model: Optional[str] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_logprobs: Optional[int] = None,
        stream: Optional[bool] = None,
        stream_options: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        parallel_tool_calls: Optional[bool] = None,
        max_tool_calls: Optional[int] = None,
        text: Optional[Dict[str, Any]] = None,
        previous_response_id: Optional[str] = None,
        conversation: Optional[Union[str, Dict[str, Any]]] = None,
        background: Optional[bool] = None,
        store: Optional[bool] = None,
        include: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        service_tier: Optional[str] = None,
        truncation: Optional[str] = None,
        reasoning: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        safety_identifier: Optional[str] = None,
        prompt_cache_key: Optional[str] = None,
        prompt: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[Response, Iterator[ResponseStreamEvent]]:
        """Create a model response"""
        payload = {}

        # Add parameters if provided
        if input is not None:
            payload["input"] = input
        if instructions is not None:
            payload["instructions"] = instructions
        if model is not None:
            payload["model"] = model
        if max_output_tokens is not None:
            payload["max_output_tokens"] = max_output_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if top_logprobs is not None:
            payload["top_logprobs"] = top_logprobs
        if stream is not None:
            payload["stream"] = stream
        if stream_options is not None:
            payload["stream_options"] = stream_options
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if parallel_tool_calls is not None:
            payload["parallel_tool_calls"] = parallel_tool_calls
        if max_tool_calls is not None:
            payload["max_tool_calls"] = max_tool_calls
        if text is not None:
            payload["text"] = text
        if previous_response_id is not None:
            payload["previous_response_id"] = previous_response_id
        if conversation is not None:
            payload["conversation"] = conversation
        if background is not None:
            payload["background"] = background
        if store is not None:
            payload["store"] = store
        if include is not None:
            payload["include"] = include
        if metadata is not None:
            payload["metadata"] = metadata
        if service_tier is not None:
            payload["service_tier"] = service_tier
        if truncation is not None:
            payload["truncation"] = truncation
        if reasoning is not None:
            payload["reasoning"] = reasoning
        if user is not None:
            payload["user"] = user
        if safety_identifier is not None:
            payload["safety_identifier"] = safety_identifier
        if prompt_cache_key is not None:
            payload["prompt_cache_key"] = prompt_cache_key
        if prompt is not None:
            payload["prompt"] = prompt

        # Handle streaming
        if stream:
            return self.client._stream_request("/v1/responses", payload)

        # Regular request
        response_data = self.client._request("POST", "/v1/responses", json=payload)
        return Response.from_dict(response_data)

    def get(
        self,
        response_id: str,
        *,
        include: Optional[List[str]] = None,
        include_obfuscation: Optional[bool] = None,
        starting_after: Optional[int] = None,
        stream: Optional[bool] = None,
    ) -> Union[Response, Iterator[ResponseStreamEvent]]:
        """Get a model response by ID"""
        params = {}
        if include is not None:
            params["include"] = include
        if include_obfuscation is not None:
            params["include_obfuscation"] = include_obfuscation
        if starting_after is not None:
            params["starting_after"] = starting_after
        if stream:
            params["stream"] = "true"
            return self.client._stream_request(f"/v1/responses/{response_id}", None, params=params, method="GET")

        response_data = self.client._request("GET", f"/v1/responses/{response_id}", params=params)
        return Response.from_dict(response_data)

    def delete(self, response_id: str) -> Dict[str, Any]:
        """Delete a model response"""
        return self.client._request("DELETE", f"/v1/responses/{response_id}")

    def cancel(self, response_id: str) -> Response:
        """Cancel a background response"""
        response_data = self.client._request("POST", f"/v1/responses/{response_id}/cancel")
        return Response.from_dict(response_data)

    def list_input_items(
        self,
        response_id: str,
        *,
        after: Optional[str] = None,
        include: Optional[List[str]] = None,
        limit: Optional[int] = None,
        order: Optional[str] = None,
    ) -> InputItemsList:
        """List input items for a response"""
        params = {}
        if after is not None:
            params["after"] = after
        if include is not None:
            params["include"] = include
        if limit is not None:
            params["limit"] = limit
        if order is not None:
            params["order"] = order

        response_data = self.client._request("GET", f"/v1/responses/{response_id}/input_items", params=params)
        return InputItemsList(**response_data)


class AsyncResponsesNamespace:
    """Async namespace for responses API endpoints"""

    def __init__(self, client: "AsyncBaseClient"):
        self.client = client

    async def create(
        self,
        *,
        input: Optional[Union[str, List[Dict[str, Any]]]] = None,
        instructions: Optional[str] = None,
        model: Optional[str] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_logprobs: Optional[int] = None,
        stream: Optional[bool] = None,
        stream_options: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        parallel_tool_calls: Optional[bool] = None,
        max_tool_calls: Optional[int] = None,
        text: Optional[Dict[str, Any]] = None,
        previous_response_id: Optional[str] = None,
        conversation: Optional[Union[str, Dict[str, Any]]] = None,
        background: Optional[bool] = None,
        store: Optional[bool] = None,
        include: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        service_tier: Optional[str] = None,
        truncation: Optional[str] = None,
        reasoning: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        safety_identifier: Optional[str] = None,
        prompt_cache_key: Optional[str] = None,
        prompt: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[Response, AsyncIterator[ResponseStreamEvent]]:
        """Create a model response"""
        payload = {}

        # Add parameters if provided
        if input is not None:
            payload["input"] = input
        if instructions is not None:
            payload["instructions"] = instructions
        if model is not None:
            payload["model"] = model
        if max_output_tokens is not None:
            payload["max_output_tokens"] = max_output_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if top_logprobs is not None:
            payload["top_logprobs"] = top_logprobs
        if stream is not None:
            payload["stream"] = stream
        if stream_options is not None:
            payload["stream_options"] = stream_options
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if parallel_tool_calls is not None:
            payload["parallel_tool_calls"] = parallel_tool_calls
        if max_tool_calls is not None:
            payload["max_tool_calls"] = max_tool_calls
        if text is not None:
            payload["text"] = text
        if previous_response_id is not None:
            payload["previous_response_id"] = previous_response_id
        if conversation is not None:
            payload["conversation"] = conversation
        if background is not None:
            payload["background"] = background
        if store is not None:
            payload["store"] = store
        if include is not None:
            payload["include"] = include
        if metadata is not None:
            payload["metadata"] = metadata
        if service_tier is not None:
            payload["service_tier"] = service_tier
        if truncation is not None:
            payload["truncation"] = truncation
        if reasoning is not None:
            payload["reasoning"] = reasoning
        if user is not None:
            payload["user"] = user
        if safety_identifier is not None:
            payload["safety_identifier"] = safety_identifier
        if prompt_cache_key is not None:
            payload["prompt_cache_key"] = prompt_cache_key
        if prompt is not None:
            payload["prompt"] = prompt

        # Handle streaming
        if stream:
            return self.client._stream_request("/v1/responses", payload)

        # Regular request
        response_data = await self.client._request("POST", "/v1/responses", json=payload)
        return Response.from_dict(response_data)

    async def get(
        self,
        response_id: str,
        *,
        include: Optional[List[str]] = None,
        include_obfuscation: Optional[bool] = None,
        starting_after: Optional[int] = None,
        stream: Optional[bool] = None,
    ) -> Union[Response, AsyncIterator[ResponseStreamEvent]]:
        """Get a model response by ID"""
        params = {}
        if include is not None:
            params["include"] = include
        if include_obfuscation is not None:
            params["include_obfuscation"] = include_obfuscation
        if starting_after is not None:
            params["starting_after"] = starting_after
        if stream:
            params["stream"] = "true"
            return self.client._stream_request(f"/v1/responses/{response_id}", None, params=params, method="GET")

        response_data = await self.client._request("GET", f"/v1/responses/{response_id}", params=params)
        return Response.from_dict(response_data)

    async def delete(self, response_id: str) -> Dict[str, Any]:
        """Delete a model response"""
        return await self.client._request("DELETE", f"/v1/responses/{response_id}")

    async def cancel(self, response_id: str) -> Response:
        """Cancel a background response"""
        response_data = await self.client._request("POST", f"/v1/responses/{response_id}/cancel")
        return Response.from_dict(response_data)

    async def list_input_items(
        self,
        response_id: str,
        *,
        after: Optional[str] = None,
        include: Optional[List[str]] = None,
        limit: Optional[int] = None,
        order: Optional[str] = None,
    ) -> InputItemsList:
        """List input items for a response"""
        params = {}
        if after is not None:
            params["after"] = after
        if include is not None:
            params["include"] = include
        if limit is not None:
            params["limit"] = limit
        if order is not None:
            params["order"] = order

        response_data = await self.client._request("GET", f"/v1/responses/{response_id}/input_items", params=params)
        return InputItemsList(**response_data)


class BaseClient:
    """Base client with common functionality"""

    DEFAULT_BASE_URL = "https://api.tokenrouter.io/api"
    DEFAULT_TIMEOUT = 60.0
    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: Optional[bool] = None,
    ):
        self.api_key = api_key or os.environ.get("TOKENROUTER_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Set TOKENROUTER_API_KEY environment variable or pass api_key parameter."
            )

        self.base_url = (base_url or os.environ.get("TOKENROUTER_BASE_URL", self.DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries or self.DEFAULT_MAX_RETRIES
        self.verify_ssl = verify_ssl if verify_ssl is not None else True

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "tokenrouter-python/1.0.12",
        }
        if headers:
            self.headers.update(headers)

    def _handle_response_error(self, response: HTTPResponse):
        """Handle HTTP response errors"""
        try:
            error_data = response.json()
            message = error_data.get("detail") or error_data.get("error") or response.text
        except Exception:
            message = response.text or response.reason_phrase

        status_code = response.status_code
        headers = dict(response.headers)

        if status_code == 401:
            raise AuthenticationError(message, status_code, response.text, headers)
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message, status_code, response.text, headers,
                retry_after=int(retry_after) if retry_after else None
            )
        elif status_code == 400:
            raise InvalidRequestError(message, status_code, response.text, headers)
        elif status_code == 403:
            if "quota" in message.lower():
                raise QuotaExceededError(message, status_code, response.text, headers)
            raise AuthenticationError(message, status_code, response.text, headers)
        elif status_code >= 500:
            raise APIStatusError(message, status_code, response.text, headers)
        else:
            raise TokenRouterError(message, status_code, response.text, headers)


class TokenRouter(BaseClient):
    """Synchronous TokenRouter client"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = httpx.Client(
            timeout=self.timeout,
            headers=self.headers,
            verify=self.verify_ssl
        )
        self.responses = ResponsesNamespace(self)

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a synchronous HTTP request"""
        # Properly join base URL with endpoint
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        url = f"{self.base_url}/{endpoint}"

        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        for attempt in range(self.max_retries):
            try:
                response = self.client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=request_headers,
                )
                response.raise_for_status()
                return response.json()
            except HTTPStatusError as e:
                if attempt == self.max_retries - 1 or e.response.status_code < 500:
                    self._handle_response_error(e.response)
                # Exponential backoff for retries
                time.sleep(2 ** attempt)
            except httpx.TimeoutException:
                if attempt == self.max_retries - 1:
                    raise TimeoutError("Request timed out")
                time.sleep(2 ** attempt)
            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise APIConnectionError(f"Connection error: {str(e)}")
                time.sleep(2 ** attempt)

    def _stream_request(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
    ) -> Iterator[ResponseStreamEvent]:
        """Make a streaming request"""
        # Properly join base URL with endpoint
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        url = f"{self.base_url}/{endpoint}"

        request_headers = self.headers.copy()
        request_headers["Accept"] = "text/event-stream"
        if headers:
            request_headers.update(headers)

        with self.client.stream(
            method=method,
            url=url,
            json=json_data,
            params=params,
            headers=request_headers,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        event_data = json.loads(data)
                        event = ResponseStreamEvent.from_dict(event_data)
                        # Add output_text convenience property for completed events
                        if event.type == "response.completed" and event.response:
                            event.response.output_text = Response._extract_output_text(event.response.output)
                        yield event
                    except json.JSONDecodeError:
                        continue

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close()


class AsyncTokenRouter(BaseClient):
    """Asynchronous TokenRouter client"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self.headers,
            verify=self.verify_ssl
        )
        self.responses = AsyncResponsesNamespace(self)

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make an asynchronous HTTP request"""
        # Properly join base URL with endpoint
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        url = f"{self.base_url}/{endpoint}"

        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=request_headers,
                )
                response.raise_for_status()
                return response.json()
            except HTTPStatusError as e:
                if attempt == self.max_retries - 1 or e.response.status_code < 500:
                    self._handle_response_error(e.response)
                # Exponential backoff for retries
                await asyncio.sleep(2 ** attempt)
            except httpx.TimeoutException:
                if attempt == self.max_retries - 1:
                    raise TimeoutError("Request timed out")
                await asyncio.sleep(2 ** attempt)
            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise APIConnectionError(f"Connection error: {str(e)}")
                await asyncio.sleep(2 ** attempt)

    async def _stream_request(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
    ) -> AsyncIterator[ResponseStreamEvent]:
        """Make a streaming request"""
        # Properly join base URL with endpoint
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        url = f"{self.base_url}/{endpoint}"

        request_headers = self.headers.copy()
        request_headers["Accept"] = "text/event-stream"
        if headers:
            request_headers.update(headers)

        async with self.client.stream(
            method=method,
            url=url,
            json=json,
            params=params,
            headers=request_headers,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        event_data = json.loads(data)
                        event = ResponseStreamEvent.from_dict(event_data)
                        # Add output_text convenience property for completed events
                        if event.type == "response.completed" and event.response:
                            event.response.output_text = Response._extract_output_text(event.response.output)
                        yield event
                    except json.JSONDecodeError:
                        continue

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()


# Default export for OpenAI compatibility
def create_client(*args, **kwargs) -> TokenRouter:
    """Create a TokenRouter client"""
    return TokenRouter(*args, **kwargs)