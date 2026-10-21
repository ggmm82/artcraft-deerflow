# Capacità operative: aubio

Versione esaminata: **0.4.9**. Audit del catalogo nativo: 2026-10-21.

**Sceglilo per:** Stima di attacchi, battiti, altezza e note dal segnale audio, con unità esplicite.
**Sorgenti:** Audio originale, parametri di analisi, report con unità, ricetta ripetibile; sorgenti musicali conservati dagli strumenti di authoring.

## Dal risultato ai comandi

| Obiettivo | ID presenti nella versione fissata |
|---|---|
| Estimate onset/beat times in seconds, pitch in Hz or notes. Estimates do not recognize a song or certify quality. | `aubio.analyze` |

Gli ID sopra sono registrati dalla CLI, non una certificazione di ogni funzione. Scopri parametri, contesto e disponibilità prima di mutare il documento. Le prove minime ripetibili sono in `CLI-RECIPE.md`; la qualità di produzione è trattata in `QUALITY.md`.

## Limiti e scelta del metodo

Stime del segnale, non riconoscimento della melodia, trascrizione affidabile di strumenti polifonici o giudizio musicale. Un battito stimato non prova da solo la sincronizzazione audiovisiva.

## Scoperta mirata

1. `craft capabilities aubio`: selezione per obiettivo e confini.
2. `craft commands aubio`: registro integrale; cerca soltanto gli ID pertinenti.
3. `craft tools aubio --out "$ARTCRAFT_OUTPUT_DIR/work/aubio-tools.json"`: schemi MCP della release.
4. Apri un input pertinente, salva presto il sorgente e verifica una prova a finitura prevista. Riduci il perimetro prima della qualità.
5. Verifica le proprietà salvate e un export effettivo; non trasformare il codice di uscita zero in una valutazione professionale.

Catalogo esaminato: 1 ID unici (le integrazioni con adattatore descrivono le operazioni esposte, non l’intera API upstream). SHA256 della rilevazione: `9a217080687a9c162e9758d5f16194d2e68b8678fefcf12156c09bd0094140f1`.
Fonte: https://aubio.org/manual/latest/cli.html. Il catalogo locale della versione fissata prevale sulla documentazione di versioni successive.
