import fs from 'node:fs';
const root=process.argv[2] ?? '/app/frontend';
const file=root+'/src/components/workspace/workspace-sidebar.tsx';
let source=fs.readFileSync(file,'utf8');
const marker='          <WorkspaceNavChatList />';
if(!source.includes(marker) || !source.includes('import { ThreadDeleteDialogProvider }'))throw Error('DeerFlow sidebar changed; review integration before building');
source=source.replace(marker, '          <TeamOnboarding />\n'+marker+'\n          <Link href="/workspace/studio" className="mx-3 rounded-md px-3 py-2 text-sm hover:bg-accent">La tua squadra</Link>');
source=source.replace('import { ThreadDeleteDialogProvider }', 'import { TeamOnboarding } from \"./team-onboarding\";\nimport { ThreadDeleteDialogProvider }');
source=source.replace('"use client";', '"use client";\n\nimport Link from "next/link";');
fs.writeFileSync(file,source);

// Pro/Ultra select the workflow, independently of provider thinking controls.
// Patch the shared resolver so selection, saved settings and model switches agree.
const reasoningFile=root+'/src/core/models/reasoning.ts';
let reasoning=fs.readFileSync(reasoningFile,'utf8');
const unsupportedMode='  if (thinking === "unsupported") {\n    return "flash";\n  }';
if(reasoning.split(unsupportedMode).length !== 2)throw Error('DeerFlow reasoning resolver changed; review mode integration before building');
reasoning=reasoning.replace(unsupportedMode, '  if (thinking === "unsupported") {\n    // Workflow modes do not require a provider-level thinking toggle.\n    return mode === "pro" || mode === "ultra" ? mode : "flash";\n  }');
fs.writeFileSync(reasoningFile,reasoning);
