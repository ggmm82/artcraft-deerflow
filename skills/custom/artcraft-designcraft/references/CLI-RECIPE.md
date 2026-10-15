# designcraft — ricetta CLI verificata

Questa ricetta è stata eseguita con la release fissata nel catalogo e viene inclusa automaticamente nel contesto dello specialista. Gli input di prova non sostituiscono quelli dell’utente. Adatta contenuti, dimensioni e percorsi al brief e alla cartella assegnata. Nei blocchi JSON sostituisci i percorsi di esempio; non lasciare il segnaposto RUN.

## Documento editoriale, PDF e riapertura
```bash
designcraft-cli run --cmd 'file.new={"width":360,"height":240,"pages":1,"facingPages":false}' --cmd 'frame.create={"rect":[20,20,330,120],"content":"text","text":"Titolo del documento"}' --cmd "file.saveAs={\"path\":\"$ARTCRAFT_OUTPUT_DIR/brochure.designcraft\"}" --export "$ARTCRAFT_OUTPUT_DIR/brochure.pdf"
designcraft-cli run --in "$ARTCRAFT_OUTPUT_DIR/brochure.designcraft" --export "$ARTCRAFT_OUTPUT_DIR/previews/pagina.png"
pdfcraft-cli info "$ARTCRAFT_OUTPUT_DIR/brochure.pdf"
pdfcraft-cli text "$ARTCRAFT_OUTPUT_DIR/brochure.pdf"
```
Prova eseguita: documento 360×240 punti con cornice di testo → sorgente e PDF; testo, dimensioni pagina e conteggio verificati; sorgente riaperto e PNG decodificato. Le unità delle dimensioni sono punti. Il registro contiene `preflight.run` per i controlli editoriali e `file.exportPdf` con opzione `standard` per le richieste di PDF/X. Non esiste il sottocomando CLI `validate-pdf`: non inventarlo. La scelta del profilo in export non costituisce certificazione PDF/X; occorre un validatore specifico indipendente per attestarlo.

La prova ripetibile è in `/opt/artcraft/acceptance.py`, caso `designcraft`. È un banco di collaudo con fixture, non una scorciatoia per produrre la consegna dell’utente. Non dichiarare visione o ascolto sulla base dei soli controlli tecnici.
