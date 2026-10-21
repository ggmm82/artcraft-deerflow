# Scegliere gli strumenti dal risultato

I ruoli professionali si compilano dal progetto. Questa mappa descrive strumenti e confini, non una squadra obbligatoria.
Consulta `craft capabilities` per la mappa compatta e `craft capabilities ID` per una sola app. Il catalogo completo è in `craft commands ID`; gli schemi esatti in `craft tools ID`.

Un comando registrato non è un workflow collaudato: verifica prerequisiti, dati, unità, modelli/add-on e reale esecuzione. `enabled=false` può dipendere dalla selezione o dal documento aperto; non significa automaticamente funzione assente.

| Strumento | Quando sceglierlo | Sorgenti da conservare |
|---|---|---|
| [photocraft](../../artcraft-photocraft/references/CAPABILITIES.md) | Ritocco, compositing raster e texture con livelli e maschere | PSD o .pcraft con livelli; originali e ricetta delle texture |
| [vectorcraft](../../artcraft-vectorcraft/references/CAPABILITIES.md) | Illustrazione vettoriale, loghi, icone, lettering e diagrammi modificabili | .vectorcraft/SVG con tracciati e testo; PDF come export |
| [filmcraft](../../artcraft-filmcraft/references/CAPABILITIES.md) | Montaggio, sequenze, composizione di contributi, colore e master audiovisivo | .fcproj, media e pacchetto portabile; master separato |
| [lightcraft](../../artcraft-lightcraft/references/CAPABILITIES.md) | Sviluppo fotografico/RAW, catalogazione, correzioni locali e serie coerenti | Originali, parametri e ricetta riproducibile; sidecar solo se realmente supportato |
| [pdfcraft](../../artcraft-pdfcraft/references/CAPABILITIES.md) | Ispezione e modifica PDF, pagine, testo, moduli, OCR e prestampa | PDF modificato e originali/ricetta; progetto editoriale da conservare separatamente |
| [effectcraft](../../artcraft-effectcraft/references/CAPABILITIES.md) | Animazione 2D/3D, motion graphics, compositing, camera/luci ed effetti | .ecproj e asset; parti, proprietà e keyframe conservati |
| [designcraft](../../artcraft-designcraft/references/CAPABILITIES.md) | Impaginazione multipagina, libri, riviste, fumetti e prestampa | .designcraft, font/immagini pertinenti e PDF di lettura/stampa |
| [gridcraft](../../artcraft-gridcraft/references/CAPABILITIES.md) | Fogli di calcolo, formule, tabelle, grafici, analisi e reporting | XLSX con formule/dati/grafici; export PDF/CSV separati |
| [wordcraft](../../artcraft-wordcraft/references/CAPABILITIES.md) | Scrittura strutturata, documenti lunghi, revisioni e apparati editoriali | DOCX/progetto supportato con struttura, stili e revisioni |
| [deckcraft](../../artcraft-deckcraft/references/CAPABILITIES.md) | Presentazioni editabili, sistemi di slide, diagrammi, media e animazioni | .deckcraft e PPTX, con media e limiti di interoperabilità |
| [cadcraft](../../artcraft-cadcraft/references/CAPABILITIES.md) | Disegno tecnico, quote, blocchi, geometrie CAD e tavole di progetto | DXF/DWG o formato nativo realmente supportato, con unità e quote |
| [soundcraft](../../artcraft-soundcraft/references/CAPABILITIES.md) | Composizione MIDI, sintesi, sound design, montaggio e mix modificabile | .scraft con strumenti/note, clip, automazioni, media, stem e mix |
| [figcraft](../../artcraft-figcraft/references/CAPABILITIES.md) | Design di interfacce, componenti, layout adattivi e prototipi | .figcraft e asset; esportazioni .fig/SVG/PDF verificate separatamente |
| [blender](../../artcraft-blender/references/CAPABILITIES.md) | Modellazione 3D, rig, materiali, simulazioni, animazione e rendering | .blend con risorse incorporate; GLB/FBX/video come export |
| [calibre](../../artcraft-calibre/references/CAPABILITIES.md) | Produzione e conversione editoriale, EPUB/AZW3, metadati, risorse e librerie | XHTML/CSS/OPF e risorse, ebook ricostruibile e input editoriali |

## Passaggi tra strumenti

Per ogni passaggio specifica risultato atteso, formato, unità/scala, risoluzione, colore, frame rate/sample rate e riferimenti temporali pertinenti. L’integrazione conserva anche i sorgenti delle componenti, non soltanto il progetto che li contiene.
Usa gli strumenti di authoring pertinenti prima di ridurre tutto a primitive o script usa-e-getta. Lo scripting rimane utile per costruzione e automazione, con ricetta e parametri conservati. La disponibilità di molte app non obbliga a usarle tutte.
Se la prova non raggiunge la finitura, cambia il metodo o la competenza sul difetto osservato. Un campione breve può essere fedele al livello finale; un render lungo dello stesso asset rudimentale non lo migliora.
