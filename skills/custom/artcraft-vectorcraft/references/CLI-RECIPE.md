# vectorcraft — ricetta CLI verificata

Questa ricetta è stata eseguita con la release fissata nel catalogo e viene inclusa automaticamente nel contesto dello specialista. Gli input di prova non sostituiscono quelli dell’utente. Adatta contenuti, dimensioni e percorsi al brief e alla cartella assegnata. Nei blocchi JSON sostituisci i percorsi di esempio; non lasciare il segnaposto RUN.

## Creazione da zero e importazione SVG

Per un disegno originale senza input, scrivi prima un SVG XML valido in `$ARTCRAFT_OUTPUT_DIR/work/bozza.svg` con `width`, `height` e `viewBox` coerenti. Definisci davvero il soggetto richiesto con forme/tracciati/gruppi e gradienti standard. Poi imposta `INPUT` a quel file e usa la sequenza seguente: la CLI produce il sorgente editabile e gli export. Non limitarti a preparare un batch di costruzione: esegui la produzione prima di consegnare. Non copiare la fixture del test come prodotto dell’utente.

## SVG con testo modificabile e anteprima
```bash
vectorcraft-cli convert "$INPUT" "$ARTCRAFT_OUTPUT_DIR/logo.vectorcraft"
vectorcraft-cli info "$ARTCRAFT_OUTPUT_DIR/logo.vectorcraft"
vectorcraft-cli convert "$ARTCRAFT_OUTPUT_DIR/logo.vectorcraft" "$ARTCRAFT_OUTPUT_DIR/logo.svg"
vectorcraft-cli convert "$ARTCRAFT_OUTPUT_DIR/logo.vectorcraft" "$ARTCRAFT_OUTPUT_DIR/anteprima.png"
```
Prova eseguita: SVG 160×90 con rettangolo e testo → sorgente VectorCraft → SVG/PNG. Il test indipendente legge XML, verifica `viewBox` e testo SVG editabile e decodifica il PNG. Non usare `--outline-text` quando il testo deve restare modificabile.

La prova ripetibile è in `/opt/artcraft/acceptance.py`, caso `vectorcraft`. È un banco di collaudo con fixture, non una scorciatoia per produrre la consegna dell’utente. Non dichiarare visione o ascolto sulla base dei soli controlli tecnici.
