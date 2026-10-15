# lightcraft — ricetta CLI verificata

Questa ricetta è stata eseguita con la release fissata nel catalogo e viene inclusa automaticamente nel contesto dello specialista. Gli input di prova non sostituiscono quelli dell’utente. Adatta contenuti, dimensioni e percorsi al brief e alla cartella assegnata. Nei blocchi JSON sostituisci i percorsi di esempio; non lasciare il segnaposto RUN.

## Sviluppo RAW senza modificare l’originale
```bash
lightcraft-cli render "$INPUT" -o "$ARTCRAFT_OUTPUT_DIR/sviluppata.png" --set light.exposure=0.5 --size 64
```
Prova eseguita sia su PNG sia su un vero DNG sintetico generato da `lightcraft-cli synth-merge hdr -o CARTELLA_TEST`. Il DNG è stato sviluppato dalla CLI e il suo checksum è rimasto invariato. `--size` indica il lato lungo; 64 è la dimensione della prova, da sostituire con quella di consegna. `--set` imposta uno specifico controllo reale; consulta `lightcraft-cli controls --json` per gli altri. Conserva la ricetta effettiva e verifica campioni e clipping prima di elaborare la serie; la prova non misura la qualità percettiva dei RAW dell’utente.

La prova ripetibile è in `/opt/artcraft/acceptance.py`, caso `lightcraft`. È un banco di collaudo con fixture, non una scorciatoia per produrre la consegna dell’utente. Non dichiarare visione o ascolto sulla base dei soli controlli tecnici.
