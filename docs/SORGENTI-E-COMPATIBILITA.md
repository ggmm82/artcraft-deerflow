# Consegna di sorgenti modificabili e compatibilità

Un file creato dallo specialista CADCraft non è automaticamente un documento apribile nell’app CADCraft. Un GLB valido e un viewer HTML provano aspetti del modello/visualizzatore, non l’importazione nell’app. La CLI CADCraft fissata nel progetto documenta `info FILE.dxf`, conversioni da DXF e sessioni `run`: la ricetta operativa verifica DXF, non un flusso GLB o modellazione parametrica 3D. Il solo cambio di estensione non è una conversione.

Le 15 skill (13 specialisti, spazio di lavoro e coordinatore) e le 13 ricette richiedono ora, per impostazione predefinita, i sorgenti modificabili del risultato oltre agli export. La richiesta dell’utente rimane semplice: «crea questo prodotto». La squadra sceglie formati e specialisti e consegna i file con le informazioni necessarie per riaprirli, senza chiedere all’utente di conoscere le CLI.

## File attesi per specialista

| Specialista | Sorgente da consegnare | Distinzione da rendere esplicita |
| --- | --- | --- |
| CADCraft | DXF con entità/layer e unità verificati | GLB e viewer non dimostrano apertura CADCraft; DXF 2D non equivale al modello 3D richiesto |
| PhotoCraft | Progetto `.pcraft`; PSD se richiesto e verificato | Livelli/maschere reali, non una bitmap appiattita rinominata |
| VectorCraft | `.vectorcraft`, SVG di scambio se richiesto | Testi e oggetti conservati; un PNG non è un sorgente vettoriale |
| FilmCraft | `.fcproj` e pacchetto dei media | MP4 non conserva timeline; provare il pacchetto dopo estrazione |
| LightCraft | Originali e ricetta riproducibile; sidecar/catalogo se supportati | Ricetta da rieseguire distinta da progetto nativo; PNG non è RAW |
| PdfCraft | PDF riaperto, con modificabilità dichiarata | PDF non equivale al sorgente Word/editoriale; includerlo se creato dalla squadra |
| EffectCraft | `.ecproj` e risorse collegate | GIF/video non conservano composizioni e keyframe |
| DesignCraft | `.designcraft` e risorse necessarie | PDF di stampa distinto dal progetto con cornici/stili |
| GridCraft | XLSX con formule, fogli e dati | CSV/PDF e cache numeriche non sostituiscono il workbook |
| WordCraft | DOCX con stili, testo e tabelle | PDF o pagine raster non sostituiscono il documento modificabile |
| DeckCraft | `.deckcraft` e PPTX se richiesto | Provare separatamente il PPTX; immagini di slide non sono oggetti modificabili |
| SoundCraft | `.scraft` e audio collegati | WAV/MP3 non conservano montaggio multitraccia; provare il pacchetto estratto |
| FigCraft | `.figcraft` con gerarchie/nodi | `.fig` è un export sperimentale; non promettere compatibilità Figma non provata |

Questi sono i percorsi verificati della release fissata, non un elenco di tutte le capacità future. Per funzioni aggiuntive consultare help, registri e schemi reali, eseguire il flusso e riaprire il risultato nell’app richiesta. Non promettere compatibilità con un’app terza o con la GUI sulla sola base della CLI.

## Contratto di consegna

`source_files` conserva il significato storico di input letti e sorgenti prodotti: da solo non dimostra che l’utente abbia ricevuto un sorgente. I nuovi sorgenti e i pacchetti da scaricare devono essere in `output_files`, fuori da `work/`. I file tecnici e i cataloghi non sono prodotti.

I nuovi job Codex, Gemini e DeepSeek richiedono `delivery` in `handoff.json`; il tool DeepSeek `submit_handoff` espone lo stesso schema. Ogni file in `output_files` deve avere un unico record con:

- `path` e `role`: `editable_source`, `source_archive`, `export`, `dependency`, `preview` o `report`;
- `format`, `open_with` e `editability`: formato reale, app e procedura di apertura, parti effettivamente modificabili;
- `reopen`: `status` (`passed`, `failed`, `not_run`) ed `evidence` con comando/tool ed esito effettivi;
- `limitations`: perdite, dipendenze o verifiche mancanti.

`delivery.source_status` è `included` quando il sorgente/pacchetto è effettivamente scaricabile. Non equivale a riapertura riuscita: una prova fallita/non svolta deve restare tale, con limiti e `warnings`. Il coordinatore richiede una revisione o presenta una consegna parziale, senza chiamarla compatibile.

Se il sorgente equivalente non è producibile, usare `unavailable`, spiegando il motivo in `source_note` e `warnings`. Non inventare un documento nativo per superare il controllo. `not_applicable` è riservato a rapporti/analisi senza prodotto, non consente di nascondere un export privo di sorgente.

Il runtime verifica esistenza, confini dei percorsi, copertura dei metadati, coerenza fra stato e sorgenti scaricabili e dichiarazione delle verifiche mancanti. Non apre automaticamente tutti i formati e non certifica la veridicità delle prove dichiarate dal modello: la prova di riapertura resta un’operazione dello specialista. I manifest storici rimangono leggibili senza i nuovi metadati; la validazione dei nuovi worker li richiede.

## Presentazione all’utente

Per ciascun prodotto il coordinatore allega sorgenti ed export con link, formato, app/modalità di apertura, parti modificabili e limiti. Per un pacchetto indica di estrarre lo ZIP e quale progetto aprire. Per lavori a più fasi consegna i sorgenti pertinenti di tutti i passaggi, distinguendo il disegno vettoriale dal compositing finale o il mix dal montaggio video.

I pacchetti con media devono essere provati dopo estrazione in una nuova cartella, senza dipendere dai percorsi della sandbox. Font e risorse non redistribuibili vanno segnalati senza allegarli impropriamente. Le nuove skill aggiunte al catalogo devono rispettare lo stesso contratto; non richiedono altre configurazioni di modelli.

## Verifiche della modifica

I test coprono, fra gli altri, il caso GLB classificato come export senza sorgente scaricabile, input scambiati per sorgenti consegnati, metadati mancanti/duplicati, istruzioni di apertura mancanti e riapertura fallita senza limiti dichiarati. I worker e il tool DeepSeek usano il nuovo contratto; la lettura legacy resta compatibile.

Il caso nativo CADCraft crea un DXF con una polilinea chiusa 40×20 mm, lo riapre in un nuovo processo, aggiunge una seconda polilinea e salva un nuovo DXF: il controllo indipendente verifica entrambe le entità. È una prova di modificabilità del DXF, non dell’importazione GLB né di un modello 3D.

La PR aggiorna skill e runtime; non cambia il provider configurato, non converte retroattivamente i file delle vecchie conversazioni e non esegue un deploy sul VPS. Le nuove consegne richiedono un rilascio con queste modifiche.
