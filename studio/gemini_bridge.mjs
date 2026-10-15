// Pinned official Gemini CLI authentication and content generation. No agent loop,
// built-in tools or workspace mount: DeerFlow alone executes the returned calls.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {randomUUID} from 'node:crypto';

export async function generate(core, request) {
  const config = new core.Config({sessionId: randomUUID(), model: request.model,
    targetDir: process.cwd(), cwd: process.cwd(), interactive: false, debugMode: false,
    usageStatisticsEnabled: false, telemetry: {enabled: false},
    proxy: process.env.HTTPS_PROXY || process.env.HTTP_PROXY,
    mcpEnabled: false, extensionsEnabled: false, enableAgents: false, skillsSupport: false});
  try {
    const auth = await core.createContentGeneratorConfig(config, core.AuthType.LOGIN_WITH_GOOGLE);
    const generator = await core.createContentGenerator(auth, config, config.getSessionId());
    return await generator.generateContent({...request,
      config: {...request.config, abortSignal: AbortSignal.timeout(1_740_000)}}, randomUUID());
  } finally {
    await config.dispose();
  }
}

export async function login(core) {
  const config = new core.Config({sessionId: randomUUID(), model: core.DEFAULT_GEMINI_MODEL,
    targetDir: process.cwd(), cwd: process.cwd(), interactive: true, noBrowser: true,
    debugMode: false, usageStatisticsEnabled: false, telemetry: {enabled: false},
    proxy: process.env.HTTPS_PROXY || process.env.HTTP_PROXY});
  try {
    await core.getOauthClient(core.AuthType.LOGIN_WITH_GOOGLE, config);
  } finally {
    await config.dispose();
  }
}

async function copyAuth(from, to) {
  await fs.mkdir(to, {recursive: true, mode: 0o700});
  for (const filename of ['oauth_creds.json', 'google_accounts.json', 'settings.json']) {
    const source = path.join(from, filename), target = path.join(to, filename);
    const stat = await fs.lstat(source).catch(e => {if (e.code !== 'ENOENT') throw e;});
    if (!stat) continue;
    if (!stat.isFile() || stat.isSymbolicLink()) throw Error('Credenziali Gemini non valide');
    const dest = await fs.lstat(target).catch(e => {if (e.code !== 'ENOENT') throw e;});
    if (dest?.isSymbolicLink()) throw Error('Destinazione credenziali non valida');
    const temporary = target + '.' + randomUUID() + '.tmp';
    await fs.copyFile(source, temporary);
    await fs.chmod(temporary, 0o600);
    await fs.rename(temporary, target);
  }
}

async function main() {
  const core = await import('/usr/local/lib/node_modules/@google/gemini-cli-core/dist/index.js');
  if (process.argv[2] === '--login') {
    await login(core);
    process.stdout.write('\nAccount Gemini collegato. Puoi salvare la squadra.\n');
    return;
  }
  console.log = console.debug = console.info = console.warn = console.error = () => {};
  const request = JSON.parse(await fs.readFile(process.argv[2], 'utf8'));
  await copyAuth('/credentials', '/root/.gemini');
  try {
    const response = await generate(core, request);
    process.stdout.write(JSON.stringify({ok: true, response}));
  } finally {
    await copyAuth('/root/.gemini', '/credentials');
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(() => {
    if (process.argv[2] === '--login') {
      process.stdout.write('\nAccesso Gemini non completato. Avvia nuovamente il collegamento.\n');
      process.exitCode = 1;
      return;
    }
    // Provider errors can contain credential material. Keep details private.
    process.stdout.write(JSON.stringify({ok: false,
      error: 'Gemini non disponibile: verifica account, quota e modello in La tua squadra.'}));
    process.exitCode = 1;
  });
}
