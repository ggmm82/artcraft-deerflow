"""Gemini coordinator, using CLI OAuth and its official content generator in Docker."""
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool

from . import gemini_protocol


class StudioGeminiChatModel(BaseChatModel):
    model: str = 'gemini-2.5-pro'
    request_timeout: int = 1800

    @property
    def _llm_type(self):
        return 'studio-gemini-cli'

    @property
    def _identifying_params(self):
        return {'model': self.model}

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        return self.bind(tools=[convert_to_openai_tool(t) for t in tools],
                         tool_choice=tool_choice, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs: Any):
        from .docker_runtime import generate_gemini
        records = []
        for message in messages:
            value = {'type': message.type, 'content': message.content}
            if message.type == 'ai':
                value.update(tool_calls=message.tool_calls,
                             gemini_parts=message.additional_kwargs.get('gemini_parts'))
            if message.type == 'tool':
                value['tool_call_id'] = message.tool_call_id
            records.append(value)
        tools = kwargs.get('tools', [])
        payload = gemini_protocol.request(records, self.model, tools, kwargs.get('tool_choice'))
        if stop:
            payload['config']['stopSequences'] = stop
        result = generate_gemini(payload, timeout=min(self.request_timeout, 1800))
        parsed = gemini_protocol.response(result, tools)
        usage = result.get('usageMetadata', {})
        input_tokens = usage.get('promptTokenCount', 0)
        output_tokens = usage.get('candidatesTokenCount', 0) + usage.get('thoughtsTokenCount', 0)
        message = AIMessage(content=parsed['content'], tool_calls=parsed['tool_calls'],
            additional_kwargs={'gemini_parts': parsed['gemini_parts']},
            usage_metadata={'input_tokens': input_tokens, 'output_tokens': output_tokens,
                            'total_tokens': max(usage.get('totalTokenCount', 0), input_tokens + output_tokens)})
        return ChatResult(generations=[ChatGeneration(message=message)])
