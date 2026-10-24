# Blender nella squadra ArtCraft

Blender è il quattordicesimo specialista (`blender`), accanto ai 13 strumenti Craft. Compare automaticamente nel catalogo e nelle installazioni esistenti dopo l'aggiornamento. Eredita provider e modello condivisi; nessuna chiave o configurazione aggiuntiva. Il coordinatore lo può scegliere per modellazione 3D, materiali, rigging, animazione e render, collaborando con immagini, audio e montaggio secondo il problema.

## Runtime e compatibilità

- Distribuzione ufficiale **Blender 5.2.3**, checksum SHA-256 e dimensione fissati in `versions.lock.json`. Nessun aggiornamento automatico.
- Release Linux **amd64**. La serie fissata non offre un binario ufficiale Linux ARM64: la build ARM si ferma con un errore esplicito prima di scaricare gli strumenti, senza saltare Blender in silenzio. Su Mac ARM per il container occorre emulazione `linux/amd64`; il `.blend` può essere aperto nella corrispondente app Blender per macOS.
- Il container include librerie grafiche/CPU e l'adattatore ArtCraft; non servono GPU, server grafico o licenze in abbonamento. Il render verificato usa Cycles CPU. EEVEE/GPU richiedono collaudo specifico sull'host e non sono promessi.
- Blender aggiunge circa 1,2 GB non compressi all'immagine sandbox. Render complessi richiedono RAM, tempo e spazio per i frame: salvare checkpoint e misurare un frame prima di promettere durata o prestazioni sul VPS. I limiti del worker continuano ad applicarsi.
- Binario e licenza della distribuzione ufficiale restano nel container. Blender è GPL; l'integrazione non modifica il binario. Fonti e informazioni licenza: https://www.blender.org/about/license/ e archivio ufficiale fissato nel catalogo.

## CLI e MCP

`blender` resta la CLI ufficiale. `blender-cli` è un piccolo adattatore locale incluso nel progetto; non è una distribuzione ufficiale Blender. Offre:

| Operazione | Comando |
| --- | --- |
| Scoperta | `craft help blender`, `craft commands blender`, `craft tools blender` |
| Script esplicito `bpy` | `blender-cli execute /mnt/user-data/.../create.py` |
| Riapertura e ispezione | `blender-cli inspect /mnt/user-data/.../scene.blend` |
| Render PNG CPU | `blender-cli render SCENA.blend PREVIEW.png --frame 1` |
| Export GLB | `blender-cli export_glb SCENA.blend MODELLO.glb` |
| Raccolta risorse supportate | `blender-cli pack INPUT.blend CONSEGNA.blend` |

Tutti i percorsi dell'adattatore devono appartenere al workspace. `render`, `pack` ed export non sovrascrivono file esistenti. Ogni tool MCP apre un processo Blender separato, anche dentro `craft batch`: il documento va salvato e riaperto esplicitamente. Non sono richiesti server esterni. Gli script espliciti lavorano nella sandbox temporanea; i `.blend` vengono aperti con auto-esecuzione Python disabilitata. Non si modificano autorizzazioni, credenziali o modelli dei provider.

## Consegne verificabili

La skill include competenze specifiche su `bpy`, PBR/UV, rig e gerarchie, keyframe, gestione colore, render a checkpoint e scambi con gli altri ruoli. Il sorgente richiesto è il **`.blend` modificabile**: GLB, script, anteprime o video da soli non lo sostituiscono.

Per una consegna Blender il runtime riapre il sorgente in un altro processo, controlla geometria e dipendenze e rifiuta l'approvazione tecnica se manca un `.blend` verificato. Le texture possono essere incorporate con `pack`; per risorse esterne usare ZIP completo con percorsi relativi `//`. Anche i `.blend` dentro ZIP vengono estratti e riaperti in una cartella diversa. Il file `.blend` isolato viene verificato rispetto alla sua cartella di consegna.

Le simulazioni e dipendenze procedurali di Fluid, Cloth, Soft Body, Dynamic Paint, cache di simulazione/bake o import di file nei Geometry Nodes, particelle, sequenze/video e UDIM non hanno ancora un collaudo completo: vengono segnalate e impediscono l'approvazione automatica. Non si disabilitano questi controlli per fingere una consegna completa. Restano applicati i criteri comuni della richiesta e la revisione separata del prodotto. La riapertura tecnica non certifica qualità artistica, coreografia o corrispondenza percettiva.

## Collaudo

Il caso `blender` di `scripts/acceptance.py` usa il binario ufficiale: mesh 3D con materiale e texture incorporata, animazione a keyframe, nuova apertura, valori diversi fra due pose, render PNG CPU non uniforme, export/reimport GLB con animazione, scambio MCP e sorgenti ZIP riaperti dopo trasferimento. È una fixture tecnica dichiarata, non una produzione artistica valutata da un utente.

La CI esegue questo caso insieme agli altri 13, scopre il server MCP, costruisce i runtime e avvia il Compose completo prima di pubblicare il candidato. Il Compose viene distribuito come asset della PR, pronto per il collaudo prima del merge; il template interno non è il file installabile.

## Lavori pesanti

Il render ora misura un campione preventivo e usa il [supervisore comune](LAVORI-PESANTI.md), con un budget condiviso dal pannello, avanzamento effettivo dei campioni e controllo dei processi duplicati. Non cambia automaticamente la qualità richiesta.
