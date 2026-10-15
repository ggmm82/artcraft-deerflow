# wordcraft — ricetta CLI verificata

Questa ricetta è stata eseguita con la release fissata nel catalogo e viene inclusa automaticamente nel contesto dello specialista. Gli input di prova non sostituiscono quelli dell’utente. Adatta contenuti, dimensioni e percorsi al brief e alla cartella assegnata. Nei blocchi JSON sostituisci i percorsi di esempio; non lasciare il segnaposto RUN.

## Relazione strutturata, DOCX e PDF
```bash
wordcraft-cli convert "$ARTCRAFT_OUTPUT_DIR/work/relazione.md" "$ARTCRAFT_OUTPUT_DIR/relazione.docx"
wordcraft-cli inspect "$ARTCRAFT_OUTPUT_DIR/relazione.docx"
wordcraft-cli convert "$ARTCRAFT_OUTPUT_DIR/relazione.docx" "$ARTCRAFT_OUTPUT_DIR/relazione.pdf"
pdfcraft-cli text "$ARTCRAFT_OUTPUT_DIR/relazione.pdf"
```
Prova eseguita: Markdown con titolo e tabella → DOCX con testo e tabella XML veri → PDF con lo stesso marcatore e il totale 60. La ricetta serve per documenti nuovi semplici; per modificare documenti esistenti conserva stili e parti richiesti usando i tool pertinenti. La presenza del testo nel PDF non prova l’impaginazione: resta distinta l’ispezione visiva.

La prova ripetibile è in `/opt/artcraft/acceptance.py`, caso `wordcraft`. È un banco di collaudo con fixture, non una scorciatoia per produrre la consegna dell’utente. Non dichiarare visione o ascolto sulla base dei soli controlli tecnici.
