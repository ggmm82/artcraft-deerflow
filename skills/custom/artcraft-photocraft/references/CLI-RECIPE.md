# photocraft — ricetta CLI verificata

Questa ricetta è stata eseguita con la release fissata nel catalogo e viene inclusa automaticamente nel contesto dello specialista. Gli input di prova non sostituiscono quelli dell’utente. Adatta contenuti, dimensioni e percorsi al brief e alla cartella assegnata. Nei blocchi JSON sostituisci i percorsi di esempio; non lasciare il segnaposto RUN.

## Conversione conservativa con sorgente modificabile
```bash
photocraft-cli convert "$INPUT" "$ARTCRAFT_OUTPUT_DIR/progetto.pcraft"
photocraft-cli info "$ARTCRAFT_OUTPUT_DIR/progetto.pcraft"
photocraft-cli convert "$ARTCRAFT_OUTPUT_DIR/progetto.pcraft" "$ARTCRAFT_OUTPUT_DIR/finale.png"
```
Prova eseguita: PNG RGBA 64×48 → PCraft → PNG. Dopo riapertura, dimensioni e alpha risultano conservati; il checksum dell’originale resta uguale. Per il lavoro reale confronta anche livelli, modalità e dimensioni con il brief: questa ricetta non prova ogni filtro o tutte le funzioni PSD.

La prova ripetibile è in `/opt/artcraft/acceptance.py`, caso `photocraft`. È un banco di collaudo con fixture, non una scorciatoia per produrre la consegna dell’utente. Non dichiarare visione o ascolto sulla base dei soli controlli tecnici.
