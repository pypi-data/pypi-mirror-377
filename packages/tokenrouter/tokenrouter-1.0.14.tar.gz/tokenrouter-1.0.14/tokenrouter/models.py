"""
Data models for TokenRouter SDK
OpenAI Responses API compatible
"""

from typing import Optional, List, Dict, Any, Union, Literal
from dataclasses import dataclass, field
from datetime import datetime


# Input Types
@dataclass
class ContentItem:
    """Content item for input messages"""
    type: Literal["input_text", "input_image", "input_audio"]
    text: Optional[str] = None
    image_url: Optional[Dict[str, Any]] = None
    audio: Optional[Dict[str, Any]] = None


@dataclass
class InputItem:
    """Input item for responses"""
    type: Literal["message", "function_result", "tool_result"]
    id: Optional[str] = None
    role: Optional[Literal["system", "user", "assistant"]] = None
    content: Optional[List[ContentItem]] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    output: Optional[str] = None


@dataclass
class Tool:
    """Tool definition"""
    type: Literal["function", "web_search", "file_search", "code_interpreter", "computer"]
    function: Optional[Dict[str, Any]] = None
    web_search: Optional[Dict[str, Any]] = None
    file_search: Optional[Dict[str, Any]] = None
    code_interpreter: Optional[Dict[str, Any]] = None
    computer: Optional[Dict[str, Any]] = None


@dataclass
class ResponseFormat:
    """Response format specification"""
    type: Literal["text", "json_object", "json_schema"]
    json_schema: Optional[Any] = None


@dataclass
class TextConfig:
    """Text configuration"""
    format: Optional[ResponseFormat] = None


# Response Types
@dataclass
class OutputContent:
    """Output content item"""
    type: Literal["output_text", "output_audio"]
    text: Optional[str] = None
    annotations: Optional[List[Any]] = None
    audio: Optional[Dict[str, Any]] = None


@dataclass
class ToolCall:
    """Tool call output"""
    id: str
    type: Literal["function", "web_search", "file_search", "code_interpreter", "computer"]
    function: Optional[Dict[str, Any]] = None
    web_search: Optional[Dict[str, Any]] = None
    file_search: Optional[Dict[str, Any]] = None
    code_interpreter: Optional[Dict[str, Any]] = None
    computer: Optional[Dict[str, Any]] = None


@dataclass
class OutputItem:
    """Output item from response"""
    type: Literal["message", "tool_call", "reasoning"]
    id: str
    status: Optional[Literal["completed", "failed", "incomplete"]] = None
    role: Optional[Literal["assistant", "system"]] = None
    content: Optional[List[OutputContent]] = None
    tool_calls: Optional[List[ToolCall]] = None
    encrypted_content: Optional[str] = None


@dataclass
class Usage:
    """Token usage information"""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_tokens_details: Optional[Dict[str, Any]] = None
    output_tokens_details: Optional[Dict[str, Any]] = None


@dataclass
class Response:
    """Response object from the API"""
    id: str
    object: str = "response"
    created_at: int = 0
    status: Literal["completed", "failed", "in_progress", "cancelled", "queued", "incomplete"] = "completed"
    error: Optional[Dict[str, Any]] = None
    incomplete_details: Optional[Dict[str, Any]] = None
    instructions: Optional[str] = None
    max_output_tokens: Optional[int] = None
    model: str = ""
    output: List[OutputItem] = field(default_factory=list)
    output_text: Optional[str] = None  # SDK convenience property
    parallel_tool_calls: bool = True
    previous_response_id: Optional[str] = None
    reasoning: Optional[Dict[str, Any]] = None
    store: bool = True
    temperature: float = 1.0
    text: Optional[TextConfig] = None
    tool_choice: Union[str, Dict[str, Any]] = "auto"
    tools: List[Tool] = field(default_factory=list)
    top_p: float = 1.0
    truncation: str = "disabled"
    usage: Optional[Usage] = None
    user: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    service_tier: Optional[str] = None
    conversation: Optional[Dict[str, Any]] = None
    max_tool_calls: Optional[int] = None
    safety_identifier: Optional[str] = None
    prompt_cache_key: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Response":
        """Create Response from dictionary"""
        # Convert output items
        output_items = []
        for item in data.get("output", []):
            content_list = None
            if item.get("content"):
                content_list = []
                for c in item["content"]:
                    if isinstance(c, dict):
                        content_list.append(OutputContent(
                            type=c.get("type", "output_text"),
                            text=c.get("text"),
                            annotations=c.get("annotations"),
                            audio=c.get("audio")
                        ))

            tool_calls_list = None
            if item.get("tool_calls"):
                tool_calls_list = []
                for t in item["tool_calls"]:
                    if isinstance(t, dict):
                        tool_calls_list.append(ToolCall(
                            id=t.get("id", ""),
                            type=t.get("type", "function"),
                            function=t.get("function"),
                            web_search=t.get("web_search"),
                            file_search=t.get("file_search"),
                            code_interpreter=t.get("code_interpreter"),
                            computer=t.get("computer")
                        ))

            output_item = OutputItem(
                type=item.get("type", "message"),
                id=item.get("id", ""),
                status=item.get("status"),
                role=item.get("role"),
                content=content_list,
                tool_calls=tool_calls_list,
                encrypted_content=item.get("encrypted_content")
            )
            output_items.append(output_item)

        # Convert usage if present
        usage_data = data.get("usage")
        usage = None
        if usage_data:
            usage = Usage(
                input_tokens=usage_data.get("input_tokens", 0),
                output_tokens=usage_data.get("output_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
                input_tokens_details=usage_data.get("input_tokens_details"),
                output_tokens_details=usage_data.get("output_tokens_details")
            )

        # Extract output_text from the response
        output_text = cls._extract_output_text(output_items)

        # Convert tools if present
        tools = []
        for t in data.get("tools", []):
            if isinstance(t, dict):
                tools.append(Tool(
                    type=t.get("type", "function"),
                    function=t.get("function"),
                    web_search=t.get("web_search"),
                    file_search=t.get("file_search"),
                    code_interpreter=t.get("code_interpreter"),
                    computer=t.get("computer")
                ))

        # Handle text config
        text_config = None
        if data.get("text") and isinstance(data["text"], dict):
            format_data = data["text"].get("format")
            if format_data:
                text_config = TextConfig(
                    format=ResponseFormat(
                        type=format_data.get("type", "text"),
                        json_schema=format_data.get("json_schema")
                    )
                )

        return cls(
            id=data.get("id", ""),
            object=data.get("object", "response"),
            created_at=data.get("created_at", 0),
            status=data.get("status", "completed"),
            error=data.get("error"),
            incomplete_details=data.get("incomplete_details"),
            instructions=data.get("instructions"),
            max_output_tokens=data.get("max_output_tokens"),
            model=data.get("model", ""),
            output=output_items,
            output_text=output_text,
            parallel_tool_calls=data.get("parallel_tool_calls", True),
            previous_response_id=data.get("previous_response_id"),
            reasoning=data.get("reasoning"),
            store=data.get("store", True),
            temperature=data.get("temperature", 1.0),
            text=text_config,
            tool_choice=data.get("tool_choice", "auto"),
            tools=tools,
            top_p=data.get("top_p", 1.0),
            truncation=data.get("truncation", "disabled"),
            usage=usage,
            user=data.get("user"),
            metadata=data.get("metadata"),
            service_tier=data.get("service_tier"),
            conversation=data.get("conversation"),
            max_tool_calls=data.get("max_tool_calls"),
            safety_identifier=data.get("safety_identifier"),
            prompt_cache_key=data.get("prompt_cache_key")
        )

    @staticmethod
    def _extract_output_text(output_items: List[OutputItem]) -> str:
        """Extract text from output items"""
        texts = []
        for item in output_items:
            if item.type == "message" and item.content:
                for content in item.content:
                    if content.type == "output_text" and content.text:
                        texts.append(content.text)
        return "".join(texts)


# Streaming Types
@dataclass
class ResponseDelta:
    """Delta for streaming responses"""
    id: Optional[str] = None
    status: Optional[str] = None
    output: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Usage] = None


@dataclass
class ResponseStreamEvent:
    """Stream event for responses"""
    type: Literal["response.created", "response.updated", "response.delta", "response.completed", "response.failed"]
    response: Optional[Response] = None
    delta: Optional[ResponseDelta] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResponseStreamEvent":
        """Create ResponseStreamEvent from dictionary"""
        response = None
        if data.get("response"):
            response = Response.from_dict(data["response"])

        delta = None
        if data.get("delta"):
            delta_data = data["delta"]
            # Parse usage if present in delta
            usage = None
            if delta_data.get("usage"):
                usage_data = delta_data["usage"]
                usage = Usage(
                    input_tokens=usage_data.get("input_tokens", 0),
                    output_tokens=usage_data.get("output_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0),
                    input_tokens_details=usage_data.get("input_tokens_details"),
                    output_tokens_details=usage_data.get("output_tokens_details")
                )
            delta = ResponseDelta(
                id=delta_data.get("id"),
                status=delta_data.get("status"),
                output=delta_data.get("output"),
                usage=usage
            )

        return cls(
            type=data.get("type", "response.delta"),
            response=response,
            delta=delta,
            error=data.get("error"),
            timestamp=data.get("timestamp")
        )


@dataclass
class InputItemsList:
    """List response for input items"""
    object: str = "list"
    data: List[InputItem] = field(default_factory=list)
    first_id: Optional[str] = None
    last_id: Optional[str] = None
    has_more: bool = False
