# Verifica Codex, Gemini CLI, Hostinger e specializzazione

**Aggiornamento Google:** la nuova integrazione usa [Antigravity CLI in abbonamento](ANTIGRAVITY.md). Le sezioni Gemini CLI seguenti descrivono l’integrazione precedente, rimossa dal runtime.

Audit iniziale del 15 ottobre 2026 sul ramo della PR #1. Per i successivi deploy Hostinger e le generazioni reali Codex/DeepSeek vedere [il collaudo aggiornato](CORREZIONE-MODELLI-E-DELEGA.md); il login e i limiti di collaudo Google attuali sono descritti nella guida Antigravity.

## Codex e Gemini CLI

Le versioni fissate sono Codex **0.162.1** e Gemini CLI **0.64.0**. `scripts/check_provider_clis.py` esegue i binari reali e verifica versione, comandi di login e flag del worker, senza credenziali o richieste di generazione. Il controllo passa anche nella build della sandbox.

Correzioni effettuate:

- **Gemini OAuth:** il vecchio login usava `--prompt`, che resta non interattivo anche dentro una PTY. La release 0.64.0 rifiuta lì l'autorizzazione manuale con `NO_BROWSER=true`. Il codice ufficiale distingue esplicitamente queste modalità; il login definitivo usa direttamente il modulo OAuth ufficiale di Gemini CLI in una PTY: termina dopo il collegamento, senza generare una risposta e senza richiedere `/quit`.
- **Gemini file condivisi:** il worker parte nella propria cartella di output; ora `--include-directories /mnt/user-data` abilita anche gli input caricati e i risultati dei colleghi. Il mount rimane limitato alla conversazione corrente.
- **Codex credenziali aggiornate:** il coordinatore rilegge bearer e account dal file OAuth prima di ogni richiesta, acquisendo il refresh fatto dai worker. Due prove con il vero provider DeerFlow verificano cambio delle credenziali senza ricreare il modello e oscuramento del bearer negli errori.
- Restano attivi allowlist dei file di autenticazione, permessi privati, refresh serializzato e verifica degli output tramite `handoff.json`.

La prova locale con il binario Gemini reale, HOME temporanea e PTY ha riprodotto il rifiuto con `--prompt`; con `--prompt-interactive` ha raggiunto l'URL OAuth e la richiesta del codice. Le sessioni sono state interrotte prima dell'autenticazione e le cartelle temporanee eliminate. Non è stato usato un account Google. Anche il nuovo ingresso OAuth tramite il modulo ufficiale è stato eseguito in una PTY reale fino all’URL e alla richiesta codice. Nel browser sono stati verificati selezione Gemini, codice, chiusura automatica del login, salvataggio, ereditarietà di tutti i ruoli, riapertura e schermo mobile; per questa prova la sessione OAuth è una fixture dichiarata.

**Configurazione unica:** DeepSeek, Codex e Gemini sono disponibili nello stesso pannello per coordinatore e specialisti. Gemini restituisce chiamate strutturate tramite il nucleo ufficiale CLI, senza eseguire strumenti propri nel coordinatore. Sono mantenuti identificatori delle chiamate, risultati e firme opache richieste dal modello. Il salvataggio della squadra riporta tutte le precedenti eccezioni al provider condiviso.

Il controllo di flag e protocollo non equivale a un login OAuth completato. Non sono disponibili account Codex/Gemini forniti per questo collaudo: autenticazione completa, quote e generazione reale con questi account restano da verificare. Su HTTP 401 Codex richiede una volta il rinnovo tramite `app-server account/read` con `refreshToken: true`, senza generazione, e riprova con il file aggiornato. Se anche il rinnovo viene rifiutato viene richiesto di ricollegare l’account.

## Compose Hostinger e rilascio

Sono verificati interpolazione Compose, persistenza dei volumi, limiti di memoria, dipendenze/healthcheck, corrispondenza dell'immagine worker, routing Traefik e riscrittura `/api/langgraph/` → `/api/`. Solo il Gateway riceve il socket Docker. Non sono richieste porte host o reti esterne. Questo verifica la configurazione, non il Traefik o il consumo RAM dell'istanza Hostinger reale.

Il flusso corrente è documentato in [AGGIORNAMENTO-HOSTINGER.md](AGGIORNAMENTO-HOSTINGER.md): una build della PR, prove sugli stessi digest pubblicati, Compose di prova prima del merge e promozione al rilascio stabile quando il contenuto Git del merge è identico a quello provato.

Il riepilogo **Compose pronto** del controllo `release` contiene il file installabile della PR. Dopo il merge il collegamento stabile rimane:

```text
https://github.com/ggmm82/artcraft-deerflow/releases/latest/download/compose.hostinger.yaml
```

`config/compose.hostinger.template.yaml` è il template interno, non il file da installare. L’artefatto `verified-runtime` e il prerelease contengono `compose.hostinger.yaml` e `runtime-manifest.json`, con digest, provenienza e checksum. `scripts/prepare_hostinger.py --manifest runtime-manifest.json --output compose.hostinger.yaml` ricrea il file verificando prima l’esistenza dei digest pubblicati; la modalità `--commit` resta disponibile per i vecchi tag SHA.

Il workflow verifica la riuscita della CI di origine, lo stesso repository/workflow/PR e l’identità del contenuto Git. Un cambiamento del contenuto richiede nuove prove; le PR da fork non ricevono privilegi di pubblicazione. Il rilascio non aggiorna da solo un progetto Hostinger già attivo.


## Quanto sono specializzati gli specialisti

Tutte le 13 skills sono specifiche del programma: ambito e passaggi tra ruoli, ispezione iniziale, procedure, sintassi di riferimento, diagnosi degli errori e accettazione del formato. Sono state rafforzate le procedure di recupero di ciascuna CLI: per esempio formule e ricalcolo in GridCraft, dipendenze audio in SoundCraft, unità e contorni in CADCraft, alpha/keyframe in EffectCraft, OCR/redazione in PdfCraft.

Le skills **non addestrano nuovamente il modello** e non garantiscono competenza su ogni funzione. L'esperienza dimostrabile deriva da ricette ripetibili e risultati verificati. Questa è la copertura operativa aggiunta, oltre a versione/help/registro/MCP per tutti i programmi. Ogni caso è eseguito da `scripts/acceptance.py` e dalla CI con rete disabilitata e gli stessi limiti RAM/CPU del worker (1.536 MiB, 1,5 CPU).

| Programma | Lavorazione reale e controlli |
|---|---|
| PhotoCraft | PNG RGBA → sorgente PCraft → PNG; dimensioni, alpha e originale intatto |
| VectorCraft | SVG con testo → sorgente → SVG/PNG; viewBox e testo editabile conservati |
| FilmCraft | Due clip con audio → timeline salvata → MP4; risoluzione, fps, durata, audio e immagini dei due segmenti |
| LightCraft | Sviluppo PNG e vero DNG sintetico; dimensioni di export e originali invariati |
| PdfCraft | Unione di due PDF; pagine, marcatori e ordine verificati |
| EffectCraft | Sorgente con keyframe → PNG/GIF; movimento, alpha e sei frame |
| DesignCraft | Cornice di testo → sorgente/PDF/PNG; riapertura, testo, formato e preflight senza errori |
| GridCraft | Numeri e formula SUM → XLSX; formula e cache 60 letti indipendentemente nell’XML |
| WordCraft | Markdown con titolo/tabella → DOCX/PDF; tabella XML, testo e totale |
| DeckCraft | Slide creata da zero → sorgente/PPTX/PNG; testo editabile nell’XML e render della prima slide |
| CADCraft | Polilinea chiusa 40×20 mm → DXF/SVG; vertici, chiusura e unità letti nei gruppi DXF |
| SoundCraft | WAV mono → sessione → mix stereo; dipendenze presenti, durata, 48 kHz, PCM16 e picco |
| FigCraft | Frame con testo figlio → sorgente/PNG; ID reali, riapertura, testo persistente e viewport |

Ogni skill contiene `references/CLI-RECIPE.md`, incluso automaticamente dal runtime nel contesto di Codex, Gemini e DeepSeek. Le ricette sono procedure eseguite, non esempi di sintassi ipotetici. Sono stati corretti anche `--slide 0`, i tempi numerici SoundCraft in campioni, gli ID testuali MCP attraverso `$json`, le opzioni `--project` di EffectCraft e l’inesistente `validate-pdf` di DesignCraft. Per DesignCraft si usa `preflight.run`; la conformità PDF/X richiede un validatore indipendente e non viene dedotta dal solo export.

Il collaudo utente DeepSeek dalla login ai prodotti GridCraft/WordCraft rimane documentato separatamente. Le nuove prove coprono una lavorazione rappresentativa per tutti gli strumenti: non certificano ogni funzione, tutti i formati o la qualità percettiva di qualsiasi commessa.
I test di pianificazione DeepSeek controllano struttura e discovery, non dimostrano qualità o padronanza esecutiva. Le dichiarazioni `not_run` restano tali: generare un'anteprima non equivale a visionarla o ascoltarla.

## Aggiungere uno strumento ArtCraft

Non serve un'altra configurazione di modelli. Il nuovo ruolo eredita automaticamente la squadra.

1. Aggiungere **una voce** in `versions.lock.json`: identificatore unico, nome, ruolo, descrizione, repository, versione, eseguibile, `registry_args`, `mcp_args`, asset Linux amd64/arm64 con URL, SHA-256 e dimensione, controlli ed esempi verificati. Scaricare le release ufficiali e calcolare realmente hash e dimensioni. Verificare i flag MCP di autorizzazione ai file: differiscono tra applicazioni.
2. Creare `skills/custom/artcraft-<id>/SKILL.md` con front matter, ambito, discovery, ricetta minima realmente eseguita, gestione degli errori, sorgente editabile, export, riapertura e criteri di accettazione. Includere la sezione `Consegna: sorgenti modificabili e compatibilità` e il contratto `delivery` (formato, app di apertura, modificabilità e riapertura) secondo [SORGENTI-E-COMPATIBILITA.md](SORGENTI-E-COMPATIBILITA.md). Creare `references/CLI-RECIPE.md` con la procedura verificata e le informazioni `delivery`: il runtime la include automaticamente nel contesto di tutti i provider. Non copiare soltanto il nome in un modello generico.
3. Eseguire `python scripts/sync_catalog.py`. Il catalogo propaga definizioni degli specialisti, routing del coordinatore e copie usate dal runtime. Le skills obbligatorie sono assegnate automaticamente. Il comando rifiuta una skill mancante ed è ripetibile senza ulteriori modifiche. Non modifica il profilo dei modelli.
4. Aggiungere obbligatoriamente un caso in `scripts/acceptance.py` con file reali, riapertura e controlli indipendenti; il validatore confronta i casi con il catalogo e impedisce che un nuovo programma resti senza prova operativa. Aggiungere anche a `scripts/evaluate_skills.py` un incarico rappresentativo per le valutazioni del modello (in `EXECUTION_CASES` se disponibile). Installer, menu del pannello, `craft list/help/commands/tools/batch` e discovery MCP percorrono già il catalogo dinamico.
5. Eseguire test Python, `scripts/validate.py` e build/CI completa. Il validatore confronta catalogo, specialisti e skills senza bloccare il numero a 13. Poi eseguire un vero incarico dalla chat: upload → scelta automatica del ruolo → creazione → riapertura → controlli indipendenti → download. Per audio/video aggiungere ascolto/visione quando richiesti.
6. Dopo CI verde, pubblicare le immagini e distribuire il Compose generato come sopra. All'avvio una vecchia installazione aggiunge il ruolo mancante sia al catalogo persistente sia alle definizioni del coordinatore, preservando preferenze e disabilitazioni esistenti. Il nuovo specialista eredita il provider/modello corrente.

È coperta da regressione l'aggiunta di uno strumento fittizio in una vecchia installazione: compare il ruolo, eredita il modello, vengono preservate le preferenze, e configurazioni/cataloghi restano coerenti. Questo dimostra il meccanismo di integrazione, non le capacità di una CLI futura.
