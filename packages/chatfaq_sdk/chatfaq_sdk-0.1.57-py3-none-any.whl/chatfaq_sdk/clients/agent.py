import inspect
import os
from logging import getLogger
from typing import List, Callable, Any

from chatfaq_sdk.clients import query_prompt
from chatfaq_sdk.layers import StreamingMessage


from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.clients import llm_request
from chatfaq_sdk.layers import Message, ToolUse, ToolResult

from enum import Enum


logger = getLogger(__name__)


class MessageSender(Enum):
    system = "system"
    assistant = "assistant"
    user = "user"


class Agent:
    intro_msg = ""

    def __init__(self):
        self.conversation = []
        self.prompt = None
        self.add_assistant_message(self.intro_msg)

    def add_message(self, sender: MessageSender, message: str):
        self.conversation.append((sender, message))

    def add_user_message(self, message: Any):
        self.add_message(MessageSender.user, message)

    def add_assistant_message(self, message: str):
        self.add_message(MessageSender.assistant, message)

    def _from_serialized(self, data):
        pass

    def _serialize(self):
        return {}

    async def _async_init(self, sdk: ChatFAQSDK, *args, **kwargs):
        pass

    @classmethod
    def from_serialized(cls, data):
        instance = cls()
        instance.conversation = []

        for s, m in data['conversation']:
            instance.add_message(MessageSender(s), m)

        instance._from_serialized(data)

        return instance

    def serialize(self):
        return {
            "conversation": [(s.value, m) for s, m in self.conversation],
            **self._serialize()
        }

    @classmethod
    async def async_init(cls, sdk: ChatFAQSDK, *args, **kwargs):
        instance = cls()
        await instance._async_init(sdk, *args, **kwargs)
        return instance

    def format_conversation(self):
        res = []
        for sender, message in self.conversation:
            res.append(
                {
                    "role": sender.value,
                    "content": message,
                }
            )
        return [
            {
                "role": MessageSender.system.value if self.conversation else MessageSender.user.value,
                "content": self.prompt,
            },
            *res,
        ]

    @staticmethod
    async def request_prompt(
        sdk: ChatFAQSDK, prompt_name: str, default_prompt: str
    ):
        if prompt := await query_prompt(sdk, prompt_name):
            logger.info(f"{prompt_name} found")
            return prompt
        else:
            logger.warning(f"{prompt_name} not found, using default")
            return default_prompt

    async def set_prompt(
        self, sdk: ChatFAQSDK, prompt_name: str, default_prompt: str
    ):
        self.prompt = await self.request_prompt(sdk, prompt_name, default_prompt)

    async def tool_use_loop(self, sdk: ChatFAQSDK, ctx: dict, tools: List[Callable]):
        print("\n" + "-" * 50 + "      TOOL USE LOOP \n")
        print("\033[42m" + "\033[30m tools \033[0m")
        print("\033[92m" + str(tools) + "\033[0m")

        while True:
            messages = self.format_conversation()
            print("\n" + "-" * 50 + "      PROMPT \n")
            print("\033[43m" + "\033[30m prompt \033[0m")
            print("\033[93m" + messages[0]["content"] + "\033[0m")

            response = await llm_request(
                sdk,
                os.getenv("LLM"),
                use_conversation_context=False,
                conversation_id=ctx["conversation_id"],
                bot_channel_name=ctx["bot_channel_name"],
                messages=messages,
                tools=tools,
                tool_choice="auto",
                stream=False,
            )
            print("\n" + "-" * 50 + "      RESPONSE \n")
            print("\033[45m" + "\033[30m response \033[0m")
            print("\033[95m" + str(response) + "\033[0m")

            tool_results = []
            for content in response["content"]:
                if content["type"] == "text":
                    self.add_assistant_message(content["text"])
                    yield Message(content["text"])
                elif content["type"] == "tool_use":
                    tool_use = content["tool_use"]
                    # Find the corresponding tool
                    tool = None
                    for t in tools:
                        if t.__name__ == tool_use["name"]:
                            tool = t
                    if not tool:
                        raise ValueError(f"Tool {tool_use['name']} not found")
                    # Execute the tool
                    try:
                        if inspect.iscoroutinefunction(tool):
                            result = await tool(**tool_use["args"], sdk=sdk, ctx=ctx, agent=self)
                        else:
                            result = tool(**tool_use["args"], sdk=sdk, ctx=ctx, agent=self)
                    except Exception as e:
                        result = f"Error executing tool {tool_use['name']}: {str(e)}"

                    if inspect.isasyncgen(result):
                        yield StreamingMessage(result)
                        result = str("submitted")

                    yield ToolUse(name=tool_use["name"], id=tool_use["id"], args=tool_use["args"])
                    yield ToolResult(
                        id=tool_use["id"], name=tool_use["name"], result=result
                    )
                    tool_results.append({
                        "id": tool_use["id"],
                        "name": tool_use["name"],
                        "result": result
                    })
            if not tool_results:
                break
            # Append assistant and user messages for the next iteration
            self.add_assistant_message(response["content"])
            self.add_user_message([
                {"type": "tool_result", "tool_result": tr} for tr in tool_results
            ])

    async def conversation_loop(self, sdk, ctx):
        raise NotImplementedError

    def solved(self):
        raise NotImplementedError
