# Capacità operative: photocraft

Versione esaminata: **v0.8.2**. Audit del catalogo nativo: 2026-10-20.

**Sceglilo per:** Ritocco, compositing raster e texture con livelli e maschere.
**Sorgenti:** PSD o .pcraft con livelli; originali e ricetta delle texture.

## Dal risultato ai comandi

| Obiettivo | ID presenti nella versione fissata |
|---|---|
| Livelli, gruppi e maschere | `layer.new.layer`, `layer.new.group`, `layer.layerMask.revealSelection`, `layer.newAdjustmentLayer.curves`, `layer.createClippingMask` |
| Colore e correzioni | `image.adjustments.levels`, `image.adjustments.curves`, `image.adjustments.colorBalance`, `image.adjustments.hueSaturation`, `image.adjustments.exposure` |
| Filtri e ritocco | `paint.stroke`, `filter.blur.gaussianBlur`, `filter.sharpen.unsharpMask` |
| Selezioni e canali | `select.rect`, `select.inverse`, `channel.target.layerMask` |
| Testi e tracciati | `type.create`, `type.edit`, `type.setStyle`, `layer.vectorMask.fromPath` |

Gli ID sopra sono registrati dalla CLI, non una certificazione di ogni funzione. Scopri parametri, contesto e disponibilità prima di mutare il documento. Le prove minime ripetibili sono in `CLI-RECIPE.md`; la qualità di produzione è trattata in `QUALITY.md`.

## Limiti e scelta del metodo

Editor raster, non generatore di immagini per definizione. La generazione nativa del modello è una capacità distinta. Importare un PNG non ricostruisce i livelli.

## Scoperta mirata

1. `craft capabilities photocraft`: selezione per obiettivo e confini.
2. `craft commands photocraft`: registro integrale; cerca soltanto gli ID pertinenti.
3. `craft tools photocraft --out "$ARTCRAFT_OUTPUT_DIR/work/photocraft-tools.json"`: schemi MCP della release.
4. Apri un input pertinente, salva presto il sorgente e verifica una prova a finitura prevista. Riduci il perimetro prima della qualità.
5. Verifica le proprietà salvate e un export effettivo; non trasformare il codice di uscita zero in una valutazione professionale.

Catalogo esaminato: 892 ID unici (per Blender/Calibre: adattatore, non l’intera API ufficiale). SHA256 della rilevazione: `01668d7a38cf33bb75f28fe6e4985d471e1075022bee14f4812b60c73cbcd69f`.
Fonte: https://github.com/storytold/photocraft/tree/v0.8.2. Il catalogo locale della versione fissata prevale sulla documentazione di versioni successive.
