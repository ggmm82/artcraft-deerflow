"""Run against the real pinned Gateway in CI; no model/account requests."""
import asyncio
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

try:
    from app.gateway.services import sse_consumer
    from deerflow.runtime import RunStatus
    from deerflow.runtime.runs.manager import DisconnectMode
except ImportError:
    if os.getenv('STUDIO_REQUIRE_GATEWAY_TESTS') == '1':
        raise
    sse_consumer = None

from studio.team_routing import shared_run


@unittest.skipIf(sse_consumer is None, 'Requires the pinned Gateway image')
class BackgroundRunTests(unittest.IsolatedAsyncioTestCase):
    async def check_disconnect(self, explicit_cancel=False):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'delivery.txt'

            async def worker():
                await asyncio.sleep(0.02)
                output.write_text('completed after browser disconnect')

            task = asyncio.create_task(worker())
            body = shared_run({'on_disconnect': 'cancel'} if explicit_cancel else {})
            record = SimpleNamespace(run_id='background-test', status=RunStatus.running,
                                     store_only=False, on_disconnect=DisconnectMode(body['on_disconnect']))

            async def disconnected():
                return True

            async def subscribe(*args, **kwargs):
                yield SimpleNamespace(event='messages', data={}, id='1')

            async def cancel(run_id):
                self.assertEqual(run_id, record.run_id)
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            # Isolate only stream-retention lookup; execute the genuine Gateway
            # SSE disconnect lifecycle and its actual cancellation decision.
            with patch('app.gateway.services._terminal_record_stream_missing', return_value=False):
                frames = [frame async for frame in sse_consumer(
                    SimpleNamespace(subscribe=subscribe), record,
                    SimpleNamespace(headers={}, is_disconnected=disconnected),
                    SimpleNamespace(cancel=cancel))]
            self.assertEqual(frames, [])
            if explicit_cancel:
                self.assertTrue(task.cancelled())
                self.assertFalse(output.exists())
            else:
                await asyncio.wait_for(task, timeout=2)
                self.assertEqual(output.read_text(), 'completed after browser disconnect')

    async def test_default_disconnect_keeps_worker_and_delivery_running(self):
        await self.check_disconnect()

    async def test_explicit_cancel_policy_still_cancels_worker(self):
        await self.check_disconnect(explicit_cancel=True)
