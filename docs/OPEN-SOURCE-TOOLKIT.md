# Strumenti open source nella squadra dinamica

Il catalogo passa da 15 a 24 strumenti. I nuovi strumenti ereditano la configurazione condivisa della squadra e sono selezionabili dai ruoli compilati per il progetto. Non aggiungono provider, modelli separati, professioni obbligatorie o una sequenza fissa di esecuzione.

| Strumento | Versione fissata | Capacità | Sorgenti e prova minima |
|---|---|---|---|
| FFmpeg | 5.1.9 Debian | Probe, conversione, estrazione audio, mux | Originali, ricetta e progetti di authoring; stream e parametri reali verificati |
| Playwright | 1.62.0 | Chromium, interazioni, screenshot, trace | Test `.test.cjs`, codice del prodotto; click reale e asserzione, errore rilevato |
| aubio | 0.4.9 | Attacchi, battiti, pitch, note stimati | Audio, parametri e unità; tono noto e impulsi temporizzati |
| FluidSynth | 2.3.1 | Sintesi offline MIDI + SF2 | MIDI, banca e licenza, impostazioni; rebuild dopo trasferimento |
| EPUBCheck | 5.4.0 | Conformità EPUB indipendente | EPUB e sorgenti prodotti dalle app di authoring; capitolo mancante rifiutato |
| Pandoc | 3.12.1 | Conversione strutturata, template, bibliografie | Input, asset e ricetta; DOCX riaperto e contenuti EPUB controllati |
| Typst | 0.15.1 | Impaginazione PDF/SVG/PNG da codice | `.typ`, font, moduli e media; modifica e ricompilazione dopo trasferimento |
| FreeCAD | 0.20.2 Debian | CAD parametrico headless, geometria, STEP | `.FCStd`, script e dipendenze; quota e vincoli sketch modificati, Pad ricalcolato, STEP riaperto senza solidi duplicati |
| whisper.cpp | 1.9.5 | Parlato CPU multilingue, TXT/SRT/JSON | Originale, sottotitoli e parametri/modello; campione parlato riconosciuto offline |

FreeCAD usa il pacchetto compatibile con Debian Bookworm, **non** la release upstream 1.x. Chromium è legato al pacchetto Playwright; modello Whisper tiny multilingue e banca TimGM6mb sono disponibili nell’immagine. Versioni, hash, dimensioni, provenienza e licenze di software/risorse sono in `versions.lock.json`; dipendenze Node hanno anche il lock con integrità. Le dipendenze Debian provengono dai repository autenticati della distribuzione. L’installazione dei pacchetti principali e delle risorse verifica SHA-256. Nessun download di browser o modelli durante il collaudo offline.

## Selezione e uso

`craft capabilities` offre l’indice compatto; `craft capabilities ID`, `craft commands ID` e `craft tools ID` espongono capacità e schemi della sola app pertinente. Per queste integrazioni gli ID sono quelli dell’adattatore ArtCraft, **non** l’intero catalogo upstream. Le nove skill hanno metodo specifico, limiti, ricetta, criteri di qualità e contratto dei sorgenti; i ruoli professionali restano dinamici.

CLI uniforme: `ID-cli call OPERAZIONE '{"input":"/mnt/user-data/...", "output":"/mnt/user-data/..."}'`. Consultare gli schemi prima di chiamare: alcuni output sono cartelle, altri file nuovi. `whisper-cpp-cli` è l’adattatore ArtCraft per il tool `whisper`; `whisper-cli` resta il comando upstream per le opzioni native.

Le operazioni lunghe usano il supervisore comune: log, processo, durata e risorse restano nella console e in `work/`. Ricevute e report tecnici non diventano automaticamente prodotti da scaricare. Dopo un errore non si dichiarano riusciti gli output parziali.

## Confini che contano per la qualità

FluidSynth completa SoundCraft: note e timbri si modificano nel MIDI e nella banca, mix e automazioni nella sessione SoundCraft. Il renderer include una banca GM compatta, non una libreria orchestrale professionale. Conservare sorgenti e licenze pertinenti.

aubio misura e Whisper trascrive: non aggiungono automaticamente ascolto musicale al modello. Il giudizio percettivo resta `not_run` quando il trasporto del modello non riceve audio. Conformità EPUB, compilazione PDF e validità geometrica sono controlli tecnici, distinti da finitura, contenuto e conformità professionale.

I nuovi tool non rendono automaticamente professionale un risultato: servono brief, riferimenti, prova rappresentativa, criterio di accettazione e revisione del prodotto reale. Le lezioni sull’uso degli strumenti possono essere proposte con prove e beneficio osservato; i metodi di realizzazione richiedono accettazione; le conoscenze tecniche si attivano con test automatici verificati, restando consultabili e revocabili.

## Collaudo del rilascio

`scripts/acceptance_toolkit.py` integra il collaudo delle 24 app nella CI. Le prove native usano la stessa immagine destinata al Compose, rete disabilitata, 1536 MiB, 1,5 CPU e 256 processi. Non richiedono API key né nuovi lavori in produzione. Il controllo dei sorgenti verifica nativamente anche `.FCStd` isolati o negli ZIP; un export STEP non lo sostituisce. La prova non certifica GUI o tutti i moduli/add-on FreeCAD.

L’immagine aumenta di dimensione e richiede più spazio al primo aggiornamento; gli strumenti non restano in esecuzione quando non utilizzati. Whisper usa due thread e il modello tiny, FreeCAD resta headless, Playwright usa un solo worker. Il budget della sandbox rimane condiviso: nessun server GPU o rendering parallelo aggiunto implicitamente.
