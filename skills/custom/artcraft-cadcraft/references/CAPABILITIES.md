# Capacità operative: cadcraft

Versione esaminata: **v0.7.0**. Audit del catalogo nativo: 2026-10-21.

**Sceglilo per:** Disegno tecnico, quote, blocchi, geometrie CAD e tavole di progetto.
**Sorgenti:** DXF/DWG o formato nativo realmente supportato, con unità e quote.

## Dal risultato ai comandi

| Obiettivo | ID presenti nella versione fissata |
|---|---|
| Geometrie e modifica | `line`, `pline`, `circle`, `arc`, `spline` |
| Quote e annotazioni | `dimlinear`, `dimaligned`, `dimradius`, `mtext`, `dimstyle` |
| Layer, blocchi e riferimenti | `layer.new`, `layer.set`, `block`, `insert`, `xref` |
| Modelli 3D e viste | `3dpoly`, `3dorbit`, `union`, `subtract` |
| Layout, audit e pubblicazione | `units`, `audit`, `recover`, `layout.set`, `saveas` |

Gli ID sopra sono registrati dalla CLI, non una certificazione di ogni funzione. Scopri parametri, contesto e disponibilità prima di mutare il documento. Le prove minime ripetibili sono in `CLI-RECIPE.md`; la qualità di produzione è trattata in `QUALITY.md`.

## Limiti e scelta del metodo

GLB non è automaticamente un documento CAD apribile nell’app. Geometria valida non dimostra correttezza strutturale, normativa o dimensionale. Per un modello 3D parametrico valuta FreeCAD o altro modellatore pertinente: un disegno DXF 2D non sostituisce automaticamente un asset 3D animabile.

## Scoperta mirata

1. `craft capabilities cadcraft`: selezione per obiettivo e confini.
2. `craft commands cadcraft`: registro integrale; cerca soltanto gli ID pertinenti.
3. `craft tools cadcraft --out "$ARTCRAFT_OUTPUT_DIR/work/cadcraft-tools.json"`: schemi MCP della release.
4. Apri un input pertinente, salva presto il sorgente e verifica una prova a finitura prevista. Riduci il perimetro prima della qualità.
5. Verifica le proprietà salvate e un export effettivo; non trasformare il codice di uscita zero in una valutazione professionale.

Catalogo esaminato: 426 ID unici (le integrazioni con adattatore descrivono le operazioni esposte, non l’intera API upstream). SHA256 della rilevazione: `d0905fdd4ce7227d6f26d8627c5907ac4d6ce40fad52021b54e0e9be2dc7b4dc`.
Fonte: https://github.com/storytold/cadcraft/tree/v0.7.0. Il catalogo locale della versione fissata prevale sulla documentazione di versioni successive.
