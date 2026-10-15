# Verifica Codex, Gemini CLI, Hostinger e specializzazione

Verifica del 15 ottobre 2026, sul ramo della PR #1. Le modifiche non sono ancora distribuite su Hostinger.

## Codex e Gemini CLI

Le versioni fissate sono Codex **0.162.1** e Gemini CLI **0.64.0**. `scripts/check_provider_clis.py` esegue i binari reali e verifica versione, comandi di login e flag del worker, senza credenziali o richieste di generazione. Il controllo passa anche nella build della sandbox.

Correzioni effettuate:

- **Gemini OAuth:** il vecchio login usava `--prompt`, che resta non interattivo anche dentro una PTY. La release 0.64.0 rifiuta lì l'autorizzazione manuale con `NO_BROWSER=true`. Ora il login usa `--prompt-interactive` dentro la PTY. Il codice ufficiale della release distingue esplicitamente queste modalità. Il login ora usa direttamente il modulo OAuth ufficiale di Gemini CLI in una PTY: termina dopo il collegamento, senza generare una risposta e senza richiedere `/quit`.
- **Gemini file condivisi:** il worker parte nella propria cartella di output; ora `--include-directories /mnt/user-data` abilita anche gli input caricati e i risultati dei colleghi. Il mount rimane limitato alla conversazione corrente.
- **Codex credenziali aggiornate:** il coordinatore rilegge bearer e account dal file OAuth prima di ogni richiesta, acquisendo il refresh fatto dai worker. Due prove con il vero provider DeerFlow verificano cambio delle credenziali senza ricreare il modello e oscuramento del bearer negli errori.
- Restano attivi allowlist dei file di autenticazione, permessi privati, refresh serializzato e verifica degli output tramite `handoff.json`.

La prova locale con il binario Gemini reale, HOME temporanea e PTY ha riprodotto il rifiuto con `--prompt`; con `--prompt-interactive` ha raggiunto l'URL OAuth e la richiesta del codice. Le sessioni sono state interrotte prima dell'autenticazione e le cartelle temporanee eliminate. Non è stato usato un account Google.

**Configurazione unica:** DeepSeek, Codex e Gemini sono disponibili nello stesso pannello per coordinatore e specialisti. Gemini restituisce chiamate strutturate tramite il nucleo ufficiale CLI, senza eseguire strumenti propri nel coordinatore. Sono mantenuti identificatori delle chiamate, risultati e firme opache richieste dal modello. Il salvataggio della squadra riporta tutte le precedenti eccezioni al provider condiviso.

Il controllo di flag e protocollo non equivale a un login OAuth completato. Non sono disponibili account Codex/Gemini forniti per questo collaudo: autenticazione completa, quote e generazione reale con questi account restano da verificare. Su HTTP 401 Codex richiede una volta il rinnovo tramite `app-server account/read` con `refreshToken: true`, senza generazione, e riprova con il file aggiornato. Se anche il rinnovo viene rifiutato viene richiesto di ricollegare l’account.

## Compose Hostinger e rilascio

Sono verificati interpolazione Compose, persistenza dei volumi, limiti di memoria, dipendenze/healthcheck, corrispondenza dell'immagine worker, routing Traefik e riscrittura `/api/langgraph/` → `/api/`. Solo il Gateway riceve il socket Docker. Non sono richieste porte host o reti esterne. Questo verifica la configurazione, non il Traefik o il consumo RAM dell'istanza Hostinger reale.

**Il Compose versionato punta ancora a immagini pubblicate prima di questa PR.** I tag `sha-…` non ricevono automaticamente le correzioni. Dopo il merge, attendere il workflow completo verde sul commit di `main`: vengono pubblicate le immagini e, dopo il collaudo di avvio, viene prodotto l'artefatto **`hostinger-compose-<SHA>`**. Contiene un Compose con Gateway, frontend e sandbox dello stesso commit.

Per prepararlo manualmente dopo una CI completamente superata:

```bash
python scripts/prepare_hostinger.py --commit <SHA_COMPLETO_CON_CI_VERDE> --output reports/release/compose.hostinger.yaml
STUDIO_PASSWORD=<PASSWORD_LOCALE> TRAEFIK_HOST=<DOMINIO_HOSTINGER> docker compose -f reports/release/compose.hostinger.yaml config --quiet
```

Lo script controlla prima su GHCR l'esistenza di tutte e tre le immagini e non modifica l'output se una manca. Non consulta autonomamente lo stato CI: questa verifica è obbligatoria per chi lo esegue manualmente. Il workflow invece genera l'artefatto solo dopo i controlli e l'avvio riusciti. Nessuna credenziale viene inserita nel Compose generato.

Caricare il Compose dell'artefatto nel progetto Hostinger esistente, conservando **lo stesso nome di progetto**, le variabili e i volumi. Per continuare a usare “Compose from URL”, aggiornare il file versionato con quel Compose in una successiva modifica revisionata. Non usare `down -v`. Prima dell'aggiornamento fare backup di `studio-state` e `deerflow-data` a servizi fermi. Dopo l'aggiornamento controllare login, modello condiviso, upload, delega e download sul dominio reale. Questo audit non ha eseguito un deploy sul VPS.

## Quanto sono specializzati gli specialisti

Tutte le 13 skills sono specifiche del programma: ambito e passaggi tra ruoli, ispezione iniziale, procedure, sintassi di riferimento, diagnosi degli errori e accettazione del formato. Sono state rafforzate le procedure di recupero di ciascuna CLI: per esempio formule e ricalcolo in GridCraft, dipendenze audio in SoundCraft, unità e contorni in CADCraft, alpha/keyframe in EffectCraft, OCR/redazione in PdfCraft.

Le skills **non addestrano nuovamente il modello** e non garantiscono competenza su ogni funzione. L'esperienza dimostrabile deriva da ricette ripetibili e risultati verificati. Questa è la copertura effettiva:

| Strumenti | Prove reali disponibili | Limite |
|---|---|---|
| Tutti i 13 | Versione, help, registro e discovery MCP nella CI | Non prova ogni modifica/import/export |
| GridCraft e WordCraft | Collaudo utente DeepSeek dal login a XLSX, DOCX e PDF; riapertura e controlli indipendenti | Non copre tutte le funzioni dei programmi |
| PdfCraft | Lettura e controllo del PDF prodotto, info e testo | Nessun collaudo completo di OCR/redazione/moduli |
| SoundCraft | Banco prova DeepSeek separato con WAV, misure e gestione media | Non è un collaudo completo dalla chat né ascolto percettivo |
| DeckCraft e CADCraft | Export dimostrativi PNG e DXF nella CI | Non prova una commessa completa o ogni formato |
| Photo, Vector, Film, Light, Effect, Design e Fig | Discovery reale e procedure specializzate | Collaudo semantico di una commessa completa ancora da aggiungere |

I test di pianificazione DeepSeek controllano struttura e discovery, non dimostrano qualità o padronanza esecutiva. Le dichiarazioni `not_run` restano tali: generare un'anteprima non equivale a visionarla o ascoltarla.

## Aggiungere uno strumento ArtCraft

Non serve un'altra configurazione di modelli. Il nuovo ruolo eredita automaticamente la squadra.

1. Aggiungere **una voce** in `versions.lock.json`: identificatore unico, nome, ruolo, descrizione, repository, versione, eseguibile, `registry_args`, `mcp_args`, asset Linux amd64/arm64 con URL, SHA-256 e dimensione, controlli ed esempi verificati. Scaricare le release ufficiali e calcolare realmente hash e dimensioni. Verificare i flag MCP di autorizzazione ai file: differiscono tra applicazioni.
2. Creare `skills/custom/artcraft-<id>/SKILL.md` con front matter, ambito, discovery, ricetta minima realmente eseguita, gestione degli errori, sorgente editabile, export, riapertura e criteri di accettazione. Aggiungere riferimenti locali alla skill solo se necessari. Non copiare soltanto il nome in un modello generico.
3. Eseguire `python scripts/sync_catalog.py`. Il catalogo propaga definizioni degli specialisti, routing del coordinatore e copie usate dal runtime. Le skills obbligatorie sono assegnate automaticamente. Il comando rifiuta una skill mancante ed è ripetibile senza ulteriori modifiche. Non modifica il profilo dei modelli.
4. Aggiungere a `scripts/smoke.py` una prova del nuovo programma con risultato atteso indipendente e, in `scripts/evaluate_skills.py`, un incarico rappresentativo (anche in `EXECUTION_CASES` se disponibile). Installer, menu del pannello, `craft list/help/commands/tools/batch` e discovery MCP percorrono già il catalogo dinamico.
5. Eseguire test Python, `scripts/validate.py` e build/CI completa. Il validatore confronta catalogo, specialisti e skills senza bloccare il numero a 13. Poi eseguire un vero incarico dalla chat: upload → scelta automatica del ruolo → creazione → riapertura → controlli indipendenti → download. Per audio/video aggiungere ascolto/visione quando richiesti.
6. Dopo CI verde, pubblicare le immagini e distribuire il Compose generato come sopra. All'avvio una vecchia installazione aggiunge il ruolo mancante sia al catalogo persistente sia alle definizioni del coordinatore, preservando preferenze e disabilitazioni esistenti. Il nuovo specialista eredita il provider/modello corrente.

È coperta da regressione l'aggiunta di uno strumento fittizio in una vecchia installazione: compare il ruolo, eredita il modello, vengono preservate le preferenze, e configurazioni/cataloghi restano coerenti. Questo dimostra il meccanismo di integrazione, non le capacità di una CLI futura.
