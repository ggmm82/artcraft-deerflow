import fs from 'node:fs';
const file='/app/frontend/src/components/workspace/workspace-sidebar.tsx';
let source=fs.readFileSync(file,'utf8');
const marker='          <WorkspaceNavChatList />';
if(!source.includes(marker))throw Error('DeerFlow sidebar changed; review integration before building');
source=source.replace(marker, marker+'\n          <a href="/workspace/studio" className="mx-3 rounded-md px-3 py-2 text-sm hover:bg-accent">ArtCraft Studio</a>');
fs.writeFileSync(file,source);
