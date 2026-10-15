"""Actual LangChain model contract, exercised in the pinned gateway image."""
import importlib.util
import unittest
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec('langchain_core'), 'Requires gateway dependencies')
class GeminiProviderTests(unittest.TestCase):
    def test_deerflow_tool_call_and_final_answer_use_one_shared_model(self):
        from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
        from studio.gemini_provider import StudioGeminiChatModel
        calls = []
        def generate(payload, **kwargs):
            calls.append(payload)
            if len(calls) == 1:
                parts = [{'functionCall': {'name': 'studio_delegate', 'args': {'agent': 'gridcraft'}},
                          'thoughtSignature': 'fixture-signature'}]
            else:
                self.assertEqual(payload['contents'][-1]['parts'][0]['functionResponse']['response'],
                                 {'result': {'output': 'verified.xlsx'}})
                self.assertEqual(payload['contents'][-2]['parts'][0]['thoughtSignature'], 'fixture-signature')
                parts = [{'text': 'Ecco il foglio verificato.'}]
            return {'candidates': [{'finishReason': 'STOP', 'content': {'parts': parts}}],
                    'usageMetadata': {'promptTokenCount': 10, 'candidatesTokenCount': 5, 'totalTokenCount': 15}}
        tools = [{'type': 'function', 'function': {'name': 'studio_delegate',
                  'parameters': {'type': 'object', 'properties': {'agent': {'type': 'string'}}}}}]
        model = StudioGeminiChatModel(model='gemini-2.5-pro').bind_tools(tools)
        history = [SystemMessage('Italiano'), HumanMessage('Prepara il foglio')]
        with patch('studio.docker_runtime.generate_gemini', side_effect=generate):
            first = model.invoke(history)
            history.extend([first, ToolMessage('{"output":"verified.xlsx"}', tool_call_id=first.tool_calls[0]['id'])])
            final = model.invoke(history)
        self.assertEqual(final.content, 'Ecco il foglio verificato.')
        self.assertEqual(final.usage_metadata['total_tokens'], 15)
        self.assertTrue(all(call['model'] == 'gemini-2.5-pro' for call in calls))


if __name__ == '__main__':
    unittest.main()
