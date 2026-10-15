# filmcraft — ricetta CLI verificata

Questa ricetta è stata eseguita con la release fissata nel catalogo e viene inclusa automaticamente nel contesto dello specialista. Gli input di prova non sostituiscono quelli dell’utente. Adatta contenuti, dimensioni e percorsi al brief e alla cartella assegnata. Nei blocchi JSON sostituisci i percorsi di esempio; non lasciare il segnaposto RUN.

## Import, sequenza, salvataggio ed export CPU
Sequenza MCP verificata, da salvare come lista JSON per `craft batch filmcraft`. Sostituisci i percorsi con quelli reali:
```json
[
  {"name":"command_run","arguments":{"id":"file.newProject","params":{"name":"Montaggio"}}},
  {"name":"media_import","arguments":{"paths":["/mnt/user-data/uploads/prima.mp4","/mnt/user-data/uploads/seconda.mp4"]}},
  {"name":"command_run","arguments":{"id":"file.newSequence","params":{"name":"Main","fromItems":{"$result":"1.content.0.text.$json.items"},"width":160,"height":90,"fps":25}}},
  {"name":"command_run","arguments":{"id":"file.saveAs","params":{"path":"/mnt/user-data/outputs/filmcraft/RUN/montaggio.fcproj"}}}
]
```
```bash
filmcraft-cli --project "$ARTCRAFT_OUTPUT_DIR/montaggio.fcproj" inspect
filmcraft-cli --project "$ARTCRAFT_OUTPUT_DIR/montaggio.fcproj" export "$ARTCRAFT_OUTPUT_DIR/montaggio.mp4" --gpu-rendering off
```
Prova eseguita: due clip reali di test con audio, sequenza salvata e riaperta, export H.264 160×90 a 25 fps per 1,2 secondi con audio a 48 kHz; misure indipendenti con ffprobe. Adatta dimensioni, durata e fps agli input reali. `file.newSequenceFromClip` richiede una selezione nel Project panel: per automazione usa `file.newSequence` con `fromItems` ottenuti dall’import, evitando ID inventati e dipendenze dalla selezione GUI. Un export con media offline viene rifiutato; non usare `--allow-offline` per nasconderlo.

La prova ripetibile è in `/opt/artcraft/acceptance.py`, caso `filmcraft`. È un banco di collaudo con fixture, non una scorciatoia per produrre la consegna dell’utente. Non dichiarare visione o ascolto sulla base dei soli controlli tecnici.
