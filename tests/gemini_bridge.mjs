import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {generate, login} from '../studio/gemini_bridge.mjs';

const root = process.env.GEMINI_CORE_PATH || '/usr/local/lib/node_modules/@google/gemini-cli-core/dist/index.js';
const core = await import(pathToFileURL(root).href);
let calls = 0;
const fixture = {...core,
  createContentGenerator: async (auth, config) => {
    assert.equal(auth.authType, core.AuthType.LOGIN_WITH_GOOGLE);
    assert.equal(config.isInteractive(), false);
    assert.equal(config.getModel(), 'gemini-2.5-pro');
    calls++;
    return new core.FakeContentGenerator([{method: 'generateContent', response: {
      candidates: [{finishReason: 'STOP', content: {parts: [
        {functionCall: {name: 'studio_delegate', args: {agent: 'gridcraft'}}, thoughtSignature: 'opaque'}]}}]}}]);
  },
  getOauthClient: async (auth, config) => {
    assert.equal(auth, core.AuthType.LOGIN_WITH_GOOGLE);
    assert.equal(config.isInteractive(), true);
    assert.equal(config.isBrowserLaunchSuppressed(), true);
    calls++;
  }};
const response = await generate(fixture, {model: 'gemini-2.5-pro', contents: [{role:'user',parts:[{text:'Prova'}]}]});
assert.equal(response.candidates[0].content.parts[0].functionCall.name, 'studio_delegate');
assert.equal(response.candidates[0].content.parts[0].thoughtSignature, 'opaque');
await login(fixture);
assert.equal(calls, 2);
console.log('OK: official Gemini CLI Config, OAuth mode, structured function calls, thought signature and login without generation.');
