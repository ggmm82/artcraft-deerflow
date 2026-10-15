# pdfcraft — ricetta CLI verificata

Questa ricetta è stata eseguita con la release fissata nel catalogo e viene inclusa automaticamente nel contesto dello specialista. Gli input di prova non sostituiscono quelli dell’utente. Adatta contenuti, dimensioni e percorsi al brief e alla cartella assegnata. Nei blocchi JSON sostituisci i percorsi di esempio; non lasciare il segnaposto RUN.

## Unione verificata con ordine preservato
```bash
pdfcraft-cli info "$INPUT"
pdfcraft-cli combine "$INPUT" "$APPENDIX" --out "$ARTCRAFT_OUTPUT_DIR/unito.pdf"
pdfcraft-cli info "$ARTCRAFT_OUTPUT_DIR/unito.pdf"
pdfcraft-cli text "$ARTCRAFT_OUTPUT_DIR/unito.pdf"
```
Prova eseguita: due PDF contenenti marcatori diversi → un PDF di due pagine. Il controllo confronta il conteggio `pages` e l’ordine dei marcatori nel testo estratto. Per redazione, firme, OCR o moduli serve una ricetta distinta con strumenti effettivamente presenti nel registro: questa unione non li convalida.

La prova ripetibile è in `/opt/artcraft/acceptance.py`, caso `pdfcraft`. È un banco di collaudo con fixture, non una scorciatoia per produrre la consegna dell’utente. Non dichiarare visione o ascolto sulla base dei soli controlli tecnici.
