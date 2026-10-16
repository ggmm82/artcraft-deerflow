import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

// Execute the actual integrated upstream helper, not a duplicate implementation.
const root = process.argv[2] ?? '/app/frontend';
const { getResolvedMode, reasoningEffortForMode, supportsThinking } = await import(
  pathToFileURL(path.resolve(root, 'src/core/models/reasoning.ts')).href
);
const unsupported = { supports_thinking: false, supports_reasoning_effort: false };
const optional = { supports_thinking: true, supports_reasoning_effort: true };
const required = { reasoning: { thinking: 'required', effort: null, source: 'declared' } };
const declaredUnsupported = { reasoning: { thinking: 'unsupported', effort: null, source: 'declared' } };

for (const model of [unsupported, declaredUnsupported, null]) {
  for (const mode of ['flash', 'pro', 'ultra']) {
    assert.equal(getResolvedMode(mode, model), mode, `select ${mode}`);
    const saved = JSON.parse(JSON.stringify({ mode }));
    assert.equal(getResolvedMode(saved.mode, model), mode, `restore ${mode}`);
    assert.equal(getResolvedMode(getResolvedMode(mode, optional), model), mode, `switch provider in ${mode}`);
    assert.equal(reasoningEffortForMode(mode, model), undefined, 'no unsupported effort sent');
  }
  assert.equal(getResolvedMode('thinking', model), 'flash');
  assert.equal(getResolvedMode(undefined, model), 'flash');
  assert.equal(supportsThinking(model), false);
}
for (const mode of ['flash', 'thinking', 'pro', 'ultra']) {
  assert.equal(getResolvedMode(mode, optional), mode);
  assert.equal(getResolvedMode(mode, required), mode === 'flash' ? 'thinking' : mode);
}
assert.equal(reasoningEffortForMode('pro', optional), 'medium');
assert.equal(reasoningEffortForMode('ultra', optional), 'high');
assert.equal(getResolvedMode(undefined, optional), 'pro');
assert.equal(getResolvedMode(undefined, required), 'pro');
console.log('Chat modes: selection, restore, model switches and reasoning capabilities verified');

const { getRunStartTime } = await import(
  pathToFileURL(path.resolve(root, 'src/core/messages/run-start-time.ts')).href
);
const start = Date.parse('2026-10-16T06:00:00Z');
const now = start + 12 * 60 * 1000;
const run = { run_id: 'one', thread_id: 'chat', status: 'running', created_at: new Date(start).toISOString() };
// Reopened tabs have no submitted run ID; the same persisted start survives reload.
assert.equal(getRunStartTime([run], null, 'chat', now), start);
assert.equal(getRunStartTime(JSON.parse(JSON.stringify([run])), null, 'chat', now + 60000), start);
assert.equal((now - getRunStartTime([run], null, 'chat', now)) / 1000, 720);
assert.equal(getRunStartTime([run], 'two', 'chat', now), null, 'new submit must not reuse old clock');
assert.equal(getRunStartTime([run], null, 'other-chat', now), null);
assert.equal(getRunStartTime([{ ...run, status: 'success' }], null, 'chat', now), null);
assert.equal(getRunStartTime([{ ...run, status: 'success' }], 'one', 'chat', now), null);
assert.equal(getRunStartTime([{ ...run, created_at: 'invalid' }], null, 'chat', now), null);
assert.equal(getRunStartTime([{ ...run, created_at: new Date(now + 10000).toISOString() }], null, 'chat', now), null);
assert.equal(getRunStartTime(undefined, null, 'chat', now), null);
console.log('Run clock: reopen, reload, new submissions, thread ownership and invalid dates verified');
