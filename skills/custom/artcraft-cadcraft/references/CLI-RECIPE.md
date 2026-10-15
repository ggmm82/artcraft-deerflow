# cadcraft — ricetta CLI verificata

Questa ricetta è stata eseguita con la release fissata nel catalogo e viene inclusa automaticamente nel contesto dello specialista. Gli input di prova non sostituiscono quelli dell’utente. Adatta contenuti, dimensioni e percorsi al brief e alla cartella assegnata. Nei blocchi JSON sostituisci i percorsi di esempio; non lasciare il segnaposto RUN.

## Rettangolo metrico modificabile e verifica geometrica
```bash
cadcraft-cli run --metric --cmd 'units {"insunits":4}' --cmd 'pline {"vertices":[[0,0],[40,0],[40,20],[0,20]],"closed":true}' --save "$ARTCRAFT_OUTPUT_DIR/rettangolo.dxf"
cadcraft-cli info "$ARTCRAFT_OUTPUT_DIR/rettangolo.dxf"
cadcraft-cli convert "$ARTCRAFT_OUTPUT_DIR/rettangolo.dxf" "$ARTCRAFT_OUTPUT_DIR/previews/rettangolo.svg"
```
Prova eseguita: un rettangolo di 40×20 mm. Il test legge direttamente i gruppi DXF: quattro vertici `LWPOLYLINE`, flag di chiusura, coordinate e `$INSUNITS=4` (millimetri), poi riapre il file e valida l’SVG. Adatta dimensioni e tolleranze al brief; la scala di stampa è distinta dalle unità del modello.

La prova ripetibile è in `/opt/artcraft/acceptance.py`, caso `cadcraft`. È un banco di collaudo con fixture, non una scorciatoia per produrre la consegna dell’utente. Non dichiarare visione o ascolto sulla base dei soli controlli tecnici.
