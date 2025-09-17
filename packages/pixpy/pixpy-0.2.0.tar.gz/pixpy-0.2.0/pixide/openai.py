from concurrent.futures import Future, ThreadPoolExecutor
import json
import inspect
from pathlib import Path
from typing import Callable, TypeGuard
from openai.types.responses import (
    FunctionToolParam,
    Response,
    ResponseFunctionToolCall,
    ResponseFunctionToolCallParam,
    ResponseInputItemParam,
)
from openai.types.responses.easy_input_message_param import (
    EasyInputMessageParam,
)
from openai.types.responses.response_input_item_param import FunctionCallOutput
from openai import OpenAI


def is_function_call(
    msg: ResponseInputItemParam,
) -> TypeGuard[ResponseFunctionToolCallParam]:
    return msg.get("type") == "function_call"


def is_function_call_output(
    msg: ResponseInputItemParam,
) -> TypeGuard[FunctionCallOutput]:
    return msg.get("type") == "function_call_output"


def create_function(
    fn: Callable[..., object],
    desc: str | None = None,
    arg_desc: dict[str, str] | None = None,
) -> FunctionToolParam:
    """Create an OpenAI function schema from a Python function using inspect.signature"""
    sig = inspect.signature(fn)
    properties = {}
    required: list[str] = []

    for param_name, param in sig.parameters.items():
        param_type = "string"
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is int:
                param_type = "integer"
            elif param.annotation is float:
                param_type = "number"
            elif param.annotation is bool:
                param_type = "boolean"
            elif param.annotation is list:
                param_type = "array"
            elif param.annotation is dict:
                param_type = "object"

        properties[param_name] = {"type": param_type}
        if arg_desc:
            if param_name in arg_desc:
                properties[param_name]["description"] = arg_desc[param_name]

        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    description = desc or fn.__doc__ or f"Calls the {fn.__name__} function"

    return {
        "type": "function",
        "strict": False,
        "name": fn.__name__,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


class OpenAIClient:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.executor = ThreadPoolExecutor(max_workers=2)

        # Initialize OpenAI client
        key_file = Path.home() / ".openai.key"
        if not key_file.exists():
            raise FileNotFoundError("Can not find .openai.key in $HOME!")
        key = key_file.read_text().rstrip()
        self.client = OpenAI(api_key=key)

        # Response queue and message handling
        self.responses: list[Future[Response]] = []
        self.messages: list[ResponseInputItemParam] = []
        self.tools: list[FunctionToolParam] = []
        self.functions: dict[str, Callable[..., object]] = {}

    def add_function(
        self,
        fn: Callable[..., object],
        desc: str | None = None,
        arg_desc: dict[str, str] | None = None,
    ):
        """Add a function to the OpenAI tool set"""
        fd = create_function(fn, desc, arg_desc)
        self.tools.append(fd)
        self.functions[fd["name"]] = fn

    def handle_function_call(self, fcall: ResponseFunctionToolCall) -> FunctionCallOutput | None:
        """Handle a function call from OpenAI and return the result"""
        if fcall.name in self.functions:
            msg: ResponseFunctionToolCallParam = {
                "name": fcall.name,
                "arguments": fcall.arguments,
                "call_id": fcall.call_id,
                "type": "function_call",
            }
            self.messages.append(msg)
            fn = self.functions[fcall.name]
            args = json.loads(fcall.arguments)
            print(args)
            ret = fn(**args)
            fr: FunctionCallOutput = {
                "call_id": fcall.call_id,
                "output": str(ret),
                "type": "function_call_output",
            }
            return fr
        return None

    def add_message(self, message: ResponseInputItemParam):
        """Add a message to the conversation"""
        self.messages.append(message)

    def update_function_output(self, function_name: str, new_output: str):
        """Update the output of a specific function call in the message history"""
        read_id = ""
        for msg in self.messages:
            if "type" in msg:
                if is_function_call(msg):
                    if msg["name"] == function_name:
                        read_id = msg["call_id"]
                if is_function_call_output(msg):
                    if msg["call_id"] == read_id:
                        msg["output"] = new_output

    def send_request(self, additional_message: ResponseInputItemParam | None = None) -> Future[Response]:
        """Send a request to OpenAI and return a Future for the response"""
        if additional_message:
            self.messages.append(additional_message)

        messages = self.messages.copy()

        def _get_ai_response(messages: list[ResponseInputItemParam]) -> Response:
            instructions = (self.data_path / "instructions.md").read_text()
            response = self.client.responses.create(
                model="gpt-5-mini",
                instructions=instructions,
                input=messages,
                tools=self.tools,
            )
            return response

        future = self.executor.submit(_get_ai_response, messages)
        self.responses.append(future)
        return future

    def get_pending_response(self) -> Response | None:
        """Check for and return the first completed response, if any"""
        if len(self.responses) > 0:
            r = self.responses[0]
            if r.done():
                self.responses.pop(0)
                return r.result()
        return None

    def handle_response(self, response: Response) -> list[FunctionCallOutput]:
        """Process a response and return any function call outputs"""
        print(response.output)
        function_outputs = []

        for output in response.output:
            if output.type == "function_call":
                result = self.handle_function_call(output)
                if result:
                    function_outputs.append(result)

        if not function_outputs:
            # Add assistant message to conversation if no function calls
            self.messages.append(
                EasyInputMessageParam(role="assistant", content=response.output_text)
            )

        return function_outputs
