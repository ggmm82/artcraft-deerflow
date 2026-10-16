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
