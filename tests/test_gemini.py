import json
import unittest

from studio import gemini_protocol

TOOLS = [{'type': 'function', 'function': {'name': 'studio_delegate',
    'parameters': {'type': 'object', 'properties': {'agent': {'type': 'string'}}}}}]


class ProtocolTests(unittest.TestCase):
    def test_tool_roundtrip_preserves_thought_signatures_and_parallel_call_ids(self):
        raw = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [
            {'thought': True, 'text': 'private reasoning'},
            {'functionCall': {'name': 'studio_delegate', 'args': {'agent': 'gridcraft'}},
             'thoughtSignature': 'opaque-fixture-signature'},
            {'functionCall': {'id': 'second', 'name': 'studio_delegate', 'args': {'agent': 'wordcraft'}}}]}}]}
        parsed = gemini_protocol.response(raw, TOOLS)
        self.assertEqual(parsed['content'], '')
        first = parsed['tool_calls'][0]['id']
        messages = [{'type': 'system', 'content': 'Italiano'},
            {'type': 'human', 'content': 'Prepara il rapporto'},
            {'type': 'ai', 'content': '', 'tool_calls': parsed['tool_calls'],
             'gemini_parts': parsed['gemini_parts']},
            {'type': 'tool', 'tool_call_id': first, 'content': '{"total": 60}'},
            {'type': 'tool', 'tool_call_id': 'second', 'content': 'Report created'}]
        request = gemini_protocol.request(messages, 'gemini-2.5-pro', TOOLS)
        self.assertEqual(request['contents'][1]['parts'][1]['thoughtSignature'], 'opaque-fixture-signature')
        responses = request['contents'][2]['parts']
        self.assertEqual(responses[0]['functionResponse']['response']['result'], {'total': 60})
        self.assertEqual(responses[1]['functionResponse']['id'], 'second')
        self.assertEqual(request['config']['systemInstruction']['parts'], [{'text': 'Italiano'}])

    def test_invalid_calls_truncation_and_unmatched_results_cannot_be_delivered(self):
        for value in ({}, {'candidates': [{'finishReason': 'MAX_TOKENS'}]},
            {'candidates': [{'content': {'parts': [{'functionCall': {'name': 'shell', 'args': {}}}]}}]}):
            with self.assertRaises(RuntimeError):
                gemini_protocol.response(value, TOOLS)
        with self.assertRaises(ValueError):
            gemini_protocol.request([{'type': 'tool', 'tool_call_id': 'unknown', 'content': 'OK'}], 'model')

    def test_forced_tool_and_inline_images_are_translated_without_remote_fetches(self):
        value = gemini_protocol.request([{'type': 'human', 'content': [
            {'type': 'text', 'text': 'Osserva'},
            {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,fixture'}}]}],
            'model', TOOLS, {'type': 'function', 'function': {'name': 'studio_delegate'}})
        self.assertEqual(value['config']['toolConfig']['functionCallingConfig'],
                         {'mode': 'ANY', 'allowedFunctionNames': ['studio_delegate']})
        self.assertEqual(value['contents'][0]['parts'][1]['inlineData']['mimeType'], 'image/png')
        with self.assertRaises(ValueError):
            gemini_protocol.parts([{'type': 'image_url', 'image_url': 'https://example.invalid/image.png'}])


if __name__ == '__main__':
    unittest.main()
