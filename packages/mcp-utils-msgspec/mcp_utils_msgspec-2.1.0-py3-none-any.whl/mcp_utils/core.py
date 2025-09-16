"""
Core MCP functionality independent of web framework
"""

import json
import logging
import uuid
from collections.abc import Callable
from typing import Any, TypeVar

import msgspec

from .queue import ResponseQueueProtocol
from .schema import (
    CallToolResult,
    ClientCapabilities,
    CompletionValues,
    ErrorResponse,
    InitializeResult,
    ListPromptsResult,
    ListResourcesResult,
    ListResourceTemplateResult,
    ListToolsResult,
    MCPRequest,
    MCPResponse,
    PromptInfo,
    ResourceInfo,
    ResourceTemplateInfo,
    ServerInfo,
    TextContent,
    ToolInfo,
)

T = TypeVar("T")
logger = logging.getLogger("mcp_utils")
PAGE_SIZE = 50


class MCPServer:
    """Base MCP Server implementation"""

    def __init__(
        self,
        name: str,
        version: str,
        response_queue: ResponseQueueProtocol,
        instructions: str = "",
        protocol_version: str = "2025-06-18",
    ) -> None:
        # Basic info
        self.name: str = name
        self.version: str = version
        self.instructions: str = instructions

        # The response queue is used to store responses
        # that are sent to the client via SSE.
        self.response_queue: ResponseQueueProtocol = response_queue

        # Protocol version negotiation (see MCP spec)
        self.protocol_version: str = protocol_version

        # Server capabilities registries
        self._prompts: dict[str, Callable] = {}
        self._prompts_list: dict[str, PromptInfo] = {}
        self._prompt_completions: dict[str, dict[str, Callable]] = {}

        self._resources: dict[str, Callable] = {}
        self._resources_list: dict[str, ResourceInfo] = {}

        self._resource_templates: dict[str, Callable] = {}
        self._resource_template_list: dict[str, ResourceInfo] = {}

        self._tools: dict[str, Callable] = {}
        self._tools_list: dict[str, ToolInfo] = {}
        self._tool_arg_models: dict[str, type] = {}

    def register_tool(self, name: str, callable: Callable, tool_info: ToolInfo) -> None:
        self._tools_list[name] = tool_info
        self._tools[name] = callable
        # Track arg model for validation separately from serializable ToolInfo
        try:
            from .utils import inspect_callable

            self._tool_arg_models[name] = inspect_callable(callable).arg_model
        except Exception:
            pass

    def tool(self, name: str | None = None) -> Callable:
        """Register a tool"""

        def decorator(fn: Callable) -> Callable:
            tool_name = name or fn.__name__
            self.register_tool(
                tool_name, fn, ToolInfo.from_callable(fn, name=tool_name)
            )
            return fn

        return decorator

    def register_resource(
        self, path: str, callable: Callable, resource_info: ResourceInfo
    ) -> None:
        self._resources_list[path] = resource_info
        self._resources[path] = callable

    def resource(self, path: str, name: str | None = None) -> Callable:
        """Register a resource"""

        def decorator(fn: Callable) -> Callable:
            resource_name = name or fn.__name__
            self.register_resource(
                path, fn, ResourceInfo.from_callable(fn, path=path, name=resource_name)
            )
            return fn

        return decorator

    def register_resource_template(
        self,
        path: str,
        callable: Callable,
        resource_template_info: ResourceTemplateInfo,
    ) -> None:
        self._resource_template_list[path] = resource_template_info
        self._resource_templates[path] = callable

    def resource_template(self, path: str, name: str | None = None) -> Callable:
        """Register a resource template"""

        def decorator(f: Callable) -> Callable:
            resource_name = name or f.__name__
            self.register_resource_template(
                path,
                f,
                ResourceTemplateInfo.from_callable(
                    path=path, callable=f, name=resource_name
                ),
            )
            return f

        return decorator

    def register_prompt(
        self, name: str, callable: Callable, prompt_info: PromptInfo
    ) -> None:
        self._prompts_list[name] = prompt_info
        self._prompts[name] = callable

    def prompt(self, name: str | None = None) -> Callable:
        """Register a prompt"""

        def decorator(f: Callable) -> Callable:
            prompt_name = name or f.__name__
            self.register_prompt(
                prompt_name, f, PromptInfo.from_callable(f, name=prompt_name)
            )

            # Initialize completions dictionary for this prompt
            self._prompt_completions[prompt_name] = {}

            # Add completion_getter method to the function
            def completion_getter(param_name: str) -> Callable:
                def completion_decorator(completion_fn: Callable) -> Callable:
                    self._prompt_completions[prompt_name][param_name] = completion_fn
                    return completion_fn

                return completion_decorator

            f.completion = completion_getter
            return f

        return decorator

    def queue_response(
        self,
        session_id: str,
        response: MCPResponse,
    ) -> None:
        """Queue a response to be sent via SSE"""
        logger.debug(f"Queueing response: {response}")
        self.response_queue.push_response(
            session_id=session_id,
            response=response,
        )

    def wait_for_queued_response(
        self, session_id: str, timeout: float | None = None
    ) -> str | None:
        """
        Wait for next queued response for a session

        Args:
            session_id: The session ID
            timeout: How long to wait in seconds. None for indefinite wait.

        Returns:
            Response dictionary or None if timeout occurs
        """
        logger.debug(f"Waiting for response for session: {session_id}")
        return self.response_queue.wait_for_response(session_id, timeout)

    def generate_session_id(self) -> str:
        """
        Create a new session ID.
        """
        return str(uuid.uuid4())

    def sse_stream(self, session_id: str, messages_endpoint: str):
        """
        Create a Server-Sent Events (SSE) stream for a session

        Args:
            session_id: The session ID
            messages_endpoint: The endpoint for sending messages

        Returns:
            Iterator yielding SSE formatted strings
        """
        # The first message is the endpoint itself
        endpoint_response = f"event: endpoint\ndata: {messages_endpoint}\n\n"
        logger.debug(f"Sending endpoint: {endpoint_response}")
        yield endpoint_response

        # Now loop and block forever and keep yielding responses
        try:
            while True:
                response_json = self.wait_for_queued_response(session_id)
                if response_json:
                    logger.debug(f"Sending response: {response_json}")
                    yield f"event: message\ndata: {response_json}\n\n"
        finally:
            # Clean up session when the client disconnects
            self.response_queue.clear_session(session_id)

    def get_capabilities(self) -> InitializeResult:
        """
        Get capabilities of the server

        See: https://spec.modelcontextprotocol.io/specification/2024-11-05/basic/lifecycle/#initialization
        """
        return InitializeResult(
            capabilities=ClientCapabilities(
                experimental={},
                prompts={"listChanged": False},
                resources={"subscribe": False, "listChanged": False},
                tools={"listChanged": False},
            ),
            instructions=self.instructions,
            protocolVersion=self.protocol_version,
            serverInfo=ServerInfo(name=self.name, version=self.version),
        )

    def get_list_tools(
        self, page: int = 1, page_size: int = PAGE_SIZE
    ) -> ListToolsResult:
        """
        List available tools

        See: https://spec.modelcontextprotocol.io/specification/2024-11-05/server/tools/#listing-tools
        """
        tools = list(self._tools_list.values())
        paginated_tools, next_page = get_page_of_items(tools, page, page_size)

        return ListToolsResult(
            tools=paginated_tools,
            nextCursor=next_page,
        )

    def get_list_prompts(
        self, page: int = 1, page_size: int = PAGE_SIZE
    ) -> ListPromptsResult:
        """
        List available prompts

        See: https://spec.modelcontextprotocol.io/specification/2024-11-05/server/prompts/#listing-prompts
        """
        prompts = list(self._prompts_list.values())
        paginated_prompts, next_page = get_page_of_items(prompts, page, page_size)

        return ListPromptsResult(
            prompts=paginated_prompts,
            nextCursor=next_page,
        )

    def get_list_resources(
        self, page: int = 1, page_size: int = PAGE_SIZE
    ) -> ListResourcesResult:
        """
        List available resources

        See: https://spec.modelcontextprotocol.io/specification/2024-11-05/server/resources/#listing-resources
        """
        resources = list(self._resources_list.values())
        paginated_resources, next_page = get_page_of_items(resources, page, page_size)

        return ListResourcesResult(
            resources=paginated_resources,
            nextCursor=next_page,
        )

    def get_list_resource_templates(
        self, page: int = 1, page_size: int = PAGE_SIZE
    ) -> ListResourceTemplateResult:
        """
        List available resource templates

        See: https://spec.modelcontextprotocol.io/specification/2024-11-05/server/resources/#resource-templates
        """
        resource_templates = list(self._resource_template_list.values())
        paginated_resource_templates, next_page = get_page_of_items(
            resource_templates, page, page_size
        )

        return ListResourceTemplateResult(
            resourceTemplates=paginated_resource_templates,
            nextCursor=next_page,
        )

    def get_completions(
        self, prompt_name: str, param_name: str, value: str
    ) -> CompletionValues:
        """
        Get completions for a prompt parameter

        Args:
            prompt_name: Name of the prompt
            param_name: Name of the parameter
            value: Current value of the parameter

        Returns:
            CompletionValues object with possible completions

        See https://spec.modelcontextprotocol.io/specification/2024-11-05/server/utilities/completion/#requesting-completions
        """
        if prompt_name not in self._prompt_completions:
            return CompletionValues(values=[], total=0)

        completions = self._prompt_completions[prompt_name]
        if param_name not in completions:
            return CompletionValues(values=[])

        rv = completions[param_name](value)
        if not isinstance(rv, CompletionValues):
            return CompletionValues(values=rv, total=len(rv))
        return rv

    def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle initialize method."""
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result=self.get_capabilities(),
        )

    def _handle_ping(self, request: MCPRequest) -> MCPResponse:
        """Handle ping method."""
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result={},
        )

    def _handle_completion_complete(self, request: MCPRequest) -> MCPResponse:
        """Handle completion/complete method."""
        prompt_name = request.params["ref"]["name"]
        arg_name = request.params["argument"]["name"]
        value = request.params["argument"]["value"]
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result={"completion": self.get_completions(prompt_name, arg_name, value)},
        )

    def _handle_prompts_list(self, request: MCPRequest) -> MCPResponse:
        """Handle prompts/list method."""
        page = int(request.params.get("cursor", "1"))
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result=self.get_list_prompts(page=page),
        )

    def _handle_prompts_get(self, request: MCPRequest) -> MCPResponse:
        """Handle prompts/get method."""
        name = request.params["name"]
        try:
            prompt = self._prompts[name]
        except KeyError:
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error=ErrorResponse(
                    code=400,
                    message="Prompt not found",
                ),
            )
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result=prompt(**request.params["arguments"]),
        )

    def _handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/list method."""
        page = int(request.params.get("cursor", "1"))
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result=self.get_list_tools(page=page),
        )

    def _handle_resources_list(self, request: MCPRequest) -> MCPResponse:
        """Handle resources/list method."""
        page = int(request.params.get("cursor", "1"))
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result=self.get_list_resources(page=page),
        )

    def _handle_resources_templates_list(self, request: MCPRequest) -> MCPResponse:
        """Handle resources/templates/list method."""
        page = int(request.params.get("cursor", "1"))
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result=self.get_list_resource_templates(page=page),
        )

    def _handle_tools_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call method."""
        tool_name = request.params["name"]
        kwargs = request.params.get("arguments", {})

        try:
            callable = self._tools[tool_name]
            arg_model = self._tool_arg_models[tool_name]
            args = msgspec.convert(kwargs, arg_model)
            result = callable(**msgspec.to_builtins(args))
            if isinstance(result, dict):
                result = CallToolResult(
                    content=[TextContent(text=json.dumps(result))],
                    is_error=False,
                )
            elif isinstance(result, str):
                result = CallToolResult(
                    content=[TextContent(text=result)],
                    is_error=False,
                )
            elif isinstance(result, CallToolResult):
                result = result
            else:
                logger.error("Invalid tool result type: %s", type(result))
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    error=ErrorResponse(
                        code=400,
                        message="Invalid tool result type",
                    ),
                )
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                result=result,
            )
        except KeyError:
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error=ErrorResponse(
                    code=-32601,
                    message="Tool not found",
                ),
            )
        except Exception as e:
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error=ErrorResponse(
                    code=-32602,
                    message=str(e),
                ),
            )
        except Exception as e:
            logger.error(f"Error in tool {tool_name}: {e}")
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error=ErrorResponse(
                    code=-32603,
                    message="Internal Server Error",
                ),
            )

    def handle_message(
        self, message: dict, session_id: str | None = None
    ) -> MCPResponse | None:
        """Handle incoming MCP messages."""
        logger.debug(f"Handling message: {message}")
        response = self._handle_message(message, session_id)
        logger.debug(f"Response: {response}")
        if response is not None and session_id is not None:
            self.response_queue.push_response(session_id, response)
        return response

    def _handle_message(
        self, message: dict, session_id: str | None = None
    ) -> MCPResponse | None:
        try:
            mcp_request = msgspec.convert({**message}, MCPRequest)
        except Exception as e:
            return MCPResponse(
                jsonrpc="2.0",
                id=0,
                error=ErrorResponse(
                    code=-32600,
                    message=str(e),
                ),
            )

        if mcp_request.params is None:
            mcp_request.params = {}

        logger.debug(f"Received message: {mcp_request}")
        logger.info(f"Handling method: {mcp_request.method}")

        # Method handler mapping
        handlers = {
            "initialize": self._handle_initialize,
            "ping": self._handle_ping,
            "completion/complete": self._handle_completion_complete,
            "prompts/list": self._handle_prompts_list,
            "prompts/get": self._handle_prompts_get,
            "tools/list": self._handle_tools_list,
            "resources/list": self._handle_resources_list,
            "resources/templates/list": self._handle_resources_templates_list,
            "tools/call": self._handle_tools_call,
            "notifications/initialized": lambda _: None,
            "notifications/cancelled": lambda _: None,
        }

        if handler := handlers.get(mcp_request.method):
            return handler(mcp_request)
        else:
            message_id = message["id"]
            return MCPResponse(
                jsonrpc="2.0",
                id=message_id,
                error=ErrorResponse(
                    code=-32601,
                    message="Method not found",
                ),
            )


def get_page_of_items(
    items: list[Any], page: int, page_size: int
) -> tuple[list[Any], int | None]:
    """
    Get a page of items from a list.

    Args:
        items: List of items to paginate
        page: Current page number (1-based)
        page_size: Number of items per page

    Returns:
        Tuple of (items in current page, next page number if exists else None)
    """
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_items = items[start_idx:end_idx]
    # Use None to indicate no next page (not UNSET) for consistency with tests
    next_page = str(page + 1) if len(items) > end_idx else msgspec.UNSET
    return page_items, next_page
