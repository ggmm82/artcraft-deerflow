# deckcraft — ricetta CLI verificata

Questa ricetta è stata eseguita con la release fissata nel catalogo e viene inclusa automaticamente nel contesto dello specialista. Gli input di prova non sostituiscono quelli dell’utente. Adatta contenuti, dimensioni e percorsi al brief e alla cartella assegnata. Nei blocchi JSON sostituisci i percorsi di esempio; non lasciare il segnaposto RUN.

## Presentazione modificabile con testo e anteprima
Lista MCP verificata per `craft batch deckcraft`:
```json
[
  {"name":"new_presentation","arguments":{"blank":true}},
  {"name":"add_slide","arguments":{"layout":"blank"}},
  {"name":"add_text_box","arguments":{"x":30,"y":30,"w":500,"h":80,"text":"Titolo verificato","size":28}},
  {"name":"save_presentation","arguments":{"path":"/mnt/user-data/outputs/deckcraft/RUN/slide.deckcraft"}},
  {"name":"export","arguments":{"path":"/mnt/user-data/outputs/deckcraft/RUN/slide.pptx","format":"pptx"}}
]
```
```bash
deckcraft-cli info "$ARTCRAFT_OUTPUT_DIR/slide.pptx"
deckcraft-cli render "$ARTCRAFT_OUTPUT_DIR/slide.pptx" --slide 0 "$ARTCRAFT_OUTPUT_DIR/previews/slide.png"
```
Prova eseguita: prima slide creata da zero, salvata in sorgente e PPTX, riaperta e renderizzata. Il controllo indipendente legge `ppt/slides/slide1.xml` e trova il testo come testo editabile, non bitmap. Gli indici `--slide` e MCP sono **zero-based**: la prima slide è 0. Per grafici e animazioni serve un controllo specifico ulteriore.

La prova ripetibile è in `/opt/artcraft/acceptance.py`, caso `deckcraft`. È un banco di collaudo con fixture, non una scorciatoia per produrre la consegna dell’utente. Non dichiarare visione o ascolto sulla base dei soli controlli tecnici.
