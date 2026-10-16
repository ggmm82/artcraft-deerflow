# Regia di una squadra di specialisti

Il catalogo attuale comprende 13 strumenti. Non attivarli tutti senza motivo, e non trattare lo specialista del formato finale come una squadra universale. Il piano `custom` accetta qualunque specialista del catalogo dinamico, inclusi nuovi strumenti integrati tramite `versions.lock.json` e skill verificata.

## Robot che balla: esempio di prodotto audiovisivo

Usa `project_type: animated_video`. Concorda una specifica condivisa (per esempio 1080x1080, 30 fps, durata/BPM compatibili con la coreografia, alpha dove necessario), un aspetto riconoscibile e controlli sul movimento. Non promettere il brano Macarena originale senza un file disponibile: spiega l’eventuale base originale.

```json
[
  {"id":"visual","agent":"photocraft","goal":"Robot: asset separati, texture e sfondo coerenti; progetto a livelli riaperto ed export con alpha","depends_on":[]},
  {"id":"motion","agent":"effectcraft","goal":"Importa gli asset visual, costruisci e verifica il rig 3D supportato, anima le pose e renderizza; conserva .ecproj e risorse","depends_on":["visual"]},
  {"id":"audio","agent":"soundcraft","goal":"Base ritmica e accenti con BPM, cue e durata dell’animazione; mix WAV, sessione multitraccia e media verificati","depends_on":["motion"]},
  {"id":"final","agent":"filmcraft","goal":"Integra animazione e mix in timeline; verifica sincro, movimento, immagini, audio e media online; progetto autosufficiente e MP4 finale","depends_on":["motion","audio"]}
]
```

Non basta chiamare quattro specialisti: gli asset devono passare davvero nelle lavorazioni successive e l’audio deve essere presente nel filmato finale. Il runtime blocca le fasi con dipendenze incomplete, controlli falliti o passaggi senza input collegati. I controlli dichiarati non dimostrano da soli qualità artistica: esamina anteprime, pose e transizioni; effettua ascolto/visione se disponibili, altrimenti dichiara il limite.

L’utente può chiedere un video muto o fornire asset già pronti: registra il requisito esplicito in `omissions_json` e costruisci le dipendenze corrispondenti. Non inventare omissioni per risparmiare lavoro. CADCraft è utile se serve geometria tecnica supportata; LightCraft se ci sono RAW da sviluppare; non sono obbligatori in questa animazione.

## Comporre altre squadre

| Bisogno | Collaborazione tipica |
| --- | --- |
| Report con dati | GridCraft → WordCraft → PdfCraft per il controllo PDF richiesto |
| Brochure | WordCraft + PhotoCraft/VectorCraft → DesignCraft → PdfCraft |
| Presentazione | GridCraft + WordCraft + PhotoCraft/VectorCraft → DeckCraft |
| Foto RAW per catalogo | LightCraft → PhotoCraft → DesignCraft |
| Logo o identità | VectorCraft → PhotoCraft per mockup e varianti raster se utili |
| Interfaccia/prototipo | WordCraft/contenuti + VectorCraft/PhotoCraft → FigCraft |
| Tavola tecnica | CadCraft → DesignCraft/WordCraft per manuale, PdfCraft per PDF se richiesto |
| Video con effetti e musica | PhotoCraft/VectorCraft → EffectCraft + SoundCraft → FilmCraft |
| Semplice ritocco o taglio audio | Un solo specialista pertinente, senza piano complesso |

Adatta ruoli e controlli al brief; gli esempi non autorizzano sostituzioni silenziose, conteggi di tool decorativi o capacità inesistenti.
