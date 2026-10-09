import json
import re

from openai import OpenAI
from .Tools import Tools

tools = Tools()

class CallingHandler:
    """
    Handles LLM-Calls and the API-requests and exposes methods to interact with the LLM.
    """
    
    def __init__(self, api_base_url: str, api_key: str, model: str) -> None:
        self.client = OpenAI(
            api_key = api_key,
            base_url = api_base_url
        )
        self.API_BASE_URL = api_base_url
        self.API_KEY = api_key
        self.MODEL = model
        self.chats = [] # Holds a list for every chat and stores the history.
        self.current_chat = 0 # Holds the index of the current chat. Chats store the history of messages. 

    def _parse_text_tool_call(self, content: str | None) -> tuple[str, dict] | None:
        if not content:
            return None

        match = re.search(r"<tools>\s*(.*?)\s*</tools>", content, re.DOTALL)
        payload = match.group(1) if match else content.strip()
        if not match and not (payload.startswith("{") and payload.endswith("}")):
            return None

        try:
            request = json.loads(payload)
        except json.JSONDecodeError:
            return None

        if not isinstance(request, dict):
            return None
        name = request.get("name")
        arguments = request.get("arguments")
        if name not in tools.tool_functions or not isinstance(arguments, dict):
            return None
        return name, arguments
        
    def make_call(self, messages: list, chat_id=None):
        """
        Returns the answer from the LLM based on openai messages input.
        If chat_id is not None the call will be stored to that belonging chat.
        
        Example
        -------
        make_call([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ])
        """
        
        conversation = list(messages)
        while True:
            completion = self.client.chat.completions.create(
                model=self.MODEL,
                messages=conversation,
                tools=tools.tool_declarations
            )
            message = completion.choices[0].message
            tool_calls = message.tool_calls
            if not tool_calls:
                text_tool_call = self._parse_text_tool_call(message.content)
                if text_tool_call is None:
                    answer = message.content
                    break
                name, arguments = text_tool_call
                tool_call_id = f"text_call_{len(conversation)}"
                assistant_tool_calls = [{
                    "id": tool_call_id,
                    "type": "function",
                    "function": {"name": name, "arguments": json.dumps(arguments)},
                }]
                calls_to_execute = [{
                    "id": tool_call_id,
                    "type": "function",
                    "name": name,
                    "arguments": arguments,
                }]
                assistant_content = None
            else:
                assistant_tool_calls = [call.model_dump(exclude_none=True) for call in tool_calls]
                calls_to_execute = [
                    {
                        "id": call.id,
                        "type": call.type,
                        "name": call.function.name if call.type == "function" else None,
                        "arguments": call.function.arguments if call.type == "function" else None,
                    }
                    for call in tool_calls
                ]
                assistant_content = message.content

            conversation.append({
                "role": "assistant",
                "content": assistant_content,
                "tool_calls": assistant_tool_calls,
            })
            for tool_call in calls_to_execute:
                if tool_call["type"] != "function":
                    tool_result = json.dumps({"error": f"Unsupported tool type: {tool_call['type']}"})
                    conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": tool_result,
                    })
                    continue
                try:
                    arguments = tool_call["arguments"]
                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)
                    if not isinstance(arguments, dict):
                        raise ValueError("Tool arguments must be a JSON object")
                    function = tools.tool_functions[tool_call["name"]]
                    result = function(**arguments)
                    tool_result = json.dumps(result, default=str)
                except Exception as error:
                    tool_result = json.dumps({"error": str(error)})
                conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result,
                })

        if chat_id is not None:
            if chat_id == len(self.chats):
                self.chats.append(conversation)
            elif 0 <= chat_id < len(self.chats):
                self.chats[chat_id].extend(conversation)
            else:
                raise Exception("self.chats is a list and can only grow by 1 slot at a time. chat_id can only be 1 number higher than the previous chat_id.")

        return answer
        
