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
| [playwright](../../artcraft-playwright/references/CAPABILITIES.md) | Automazione browser, test di interazione, screenshot e trace su applicazioni web reali | Codice applicativo, test .test.cjs o automazione .cjs, configurazione, screenshot e trace pertinenti |
| [aubio](../../artcraft-aubio/references/CAPABILITIES.md) | Stima di attacchi, battiti, altezza e note dal segnale audio, con unità esplicite | Audio originale, parametri di analisi, report con unità, ricetta ripetibile; sorgenti musicali conservati dagli strumenti di authoring |
| [fluidsynth](../../artcraft-fluidsynth/references/CAPABILITIES.md) | Rendering offline MIDI con strumenti SF2, partitura e banca conservate per la riproduzione | MIDI, SoundFont SF2 effettivo, licenza della banca e render-settings.json; sessione SoundCraft e stem per il mix |
| [epubcheck](../../artcraft-epubcheck/references/CAPABILITIES.md) | Controllo indipendente EPUB di contenitori, manifest, risorse e markup; errori distinti dagli avvisi | EPUB e sorgenti XHTML/CSS/OPF, media e font prodotti dagli strumenti di authoring; report JSON come prova |
| [pandoc](../../artcraft-pandoc/references/CAPABILITIES.md) | Conversione Markdown, DOCX, EPUB, HTML e altri formati, con bibliografia e template espliciti | Documento strutturato originale, Markdown/AST quando usato, template, bibliografia CSL/BibTeX, font/media e ricetta di conversione |
| [typst](../../artcraft-typst/references/CAPABILITIES.md) | Composizione tipografica riproducibile in PDF, SVG o PNG da sorgenti .typ, font e risorse | Sorgenti .typ, template e moduli locali, dati, immagini, font e ricetta di compilazione |
| [freecad](../../artcraft-freecad/references/CAPABILITIES.md) | Authoring parametrico .FCStd, misure geometriche e scambio STEP tramite motore headless nativo | Documento nativo .FCStd con albero parametrico, script .py realmente usato, dati e riferimenti; STEP come export di scambio |
| [whisper](../../artcraft-whisper/references/CAPABILITIES.md) | Trascrizione parlato CPU multilingue in TXT, SRT e JSON con modello tiny fissato e disponibile offline | Audio originale o riferimento autorizzato, TXT/SRT/JSON modificabili, lingua e configurazione, identificativo e hash del modello |
| [ffmpeg](../../artcraft-ffmpeg/references/CAPABILITIES.md) | Probe dei flussi, conversione codec e formati, estrazione audio e mux con parametri espliciti | Input originali, progetti delle app di authoring, media collegati, ricetta/parametri di conversione e mux |

## Passaggi tra strumenti

Per ogni passaggio specifica risultato atteso, formato, unità/scala, risoluzione, colore, frame rate/sample rate e riferimenti temporali pertinenti. L’integrazione conserva anche i sorgenti delle componenti, non soltanto il progetto che li contiene.
Usa gli strumenti di authoring pertinenti prima di ridurre tutto a primitive o script usa-e-getta. Lo scripting rimane utile per costruzione e automazione, con ricetta e parametri conservati. La disponibilità di molte app non obbliga a usarle tutte.
Se la prova non raggiunge la finitura, cambia il metodo o la competenza sul difetto osservato. Un campione breve può essere fedele al livello finale; un render lungo dello stesso asset rudimentale non lo migliora.
