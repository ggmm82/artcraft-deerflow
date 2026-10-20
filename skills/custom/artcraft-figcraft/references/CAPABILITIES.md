# Capacità operative: figcraft

Versione esaminata: **v0.6.0**. Audit del catalogo nativo: 2026-10-20.

**Sceglilo per:** Design di interfacce, componenti, layout adattivi e prototipi.
**Sorgenti:** .figcraft e asset; esportazioni .fig/SVG/PDF verificate separatamente.

## Dal risultato ai comandi

| Obiettivo | ID presenti nella versione fissata |
|---|---|
| Frame e layout | `frame.create`, `frame.presets`, `node.create`, `node.set` |
| Componenti e proprietà | `component.create`, `component.combineVariants`, `component.addProperty`, `component.bindProperty`, `instance.create` |
| Testi e vettori | `text.create`, `vector.create`, `vector.outlineStroke` |
| Prototipi e interazioni | `proto.interaction.add`, `proto.interaction.set`, `proto.flow.add` |
| Asset, versioni ed export | `file.export`, `file.exportLayers`, `file.exportSvg`, `file.saveVersion`, `variable.export` |

Gli ID sopra sono registrati dalla CLI, non una certificazione di ogni funzione. Scopri parametri, contesto e disponibilità prima di mutare il documento. Le prove minime ripetibili sono in `CLI-RECIPE.md`; la qualità di produzione è trattata in `QUALITY.md`.

## Limiti e scelta del metodo

Un prototipo non è software applicativo funzionante. Collaborazione, plugin o servizi di rete richiedono componenti e accessi reali.

## Scoperta mirata

1. `craft capabilities figcraft`: selezione per obiettivo e confini.
2. `craft commands figcraft`: registro integrale; cerca soltanto gli ID pertinenti.
3. `craft tools figcraft --out "$ARTCRAFT_OUTPUT_DIR/work/figcraft-tools.json"`: schemi MCP della release.
4. Apri un input pertinente, salva presto il sorgente e verifica una prova a finitura prevista. Riduci il perimetro prima della qualità.
5. Verifica le proprietà salvate e un export effettivo; non trasformare il codice di uscita zero in una valutazione professionale.

Catalogo esaminato: 552 ID unici (per Blender/Calibre: adattatore, non l’intera API ufficiale). SHA256 della rilevazione: `7b4f193437e7c436aa810f283aac3df7f443ba8a6a23e76593e8e08a3702887d`.
Fonte: https://github.com/storytold/figcraft/tree/v0.6.0. Il catalogo locale della versione fissata prevale sulla documentazione di versioni successive.
