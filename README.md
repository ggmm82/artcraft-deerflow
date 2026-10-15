# ArtCraft Studio · DeerFlow

[![Verify and build](https://github.com/ggmm82/artcraft-deerflow/actions/workflows/verify.yml/badge.svg)](https://github.com/ggmm82/artcraft-deerflow/actions/workflows/verify.yml)
[![Deploy on Hostinger](https://assets.hostinger.com/vps/deploy.svg)](https://www.hostinger.com/docker-hosting?compose_url=https://raw.githubusercontent.com/ggmm82/artcraft-deerflow/main/compose.hostinger.yaml)

DeerFlow con **13 specialisti ArtCraft**, motori **Codex, Gemini e DeepSeek API**, configurazione dal browser e **sandbox Docker temporanee**. Progetto indipendente; non è una distribuzione ufficiale dei prodotti integrati.

## Come funziona

- DeerFlow offre conversazioni, caricamento file, progetti, consegna degli artefatti, modelli e skills.
- **La tua squadra**, nella barra laterale, è l’unico punto per collegare il servizio e scegliere il modello.
- Un salvataggio applica il modello al coordinatore e a tutti i 13 specialisti. Ogni ruolo mantiene le proprie skills, verifiche e preferenze; non devi configurare 13 motori.
- Descrivi il problema in chat: il coordinatore sceglie gli specialisti utili, assegna gli incarichi e controlla le consegne. Non occorre conoscere nomi di agenti o strumenti.
- Studio avvia un container per incarico, carica la procedura del programma pertinente e rimuove il container al termine, anche in caso di errore o timeout.
- I file della conversazione restano nel volume persistente. Il coordinatore passa al successivo specialista i percorsi dei risultati.
- Il profilo iniziale esegue **un solo specialista alla volta**, per la VPS da 4 GB. Non sono previsti modelli locali.

La configurazione condivisa supporta **DeepSeek API**, **account Codex** e **account Gemini**. La stessa scelta vale per coordinatore e specialisti. Gemini usa il nucleo ufficiale di Gemini CLI per autenticazione e chiamate strutturate; il coordinatore resta privo di strumenti CLI propri e affida i file agli specialisti.

## Stato della verifica

La suite locale verifica configurazione, API del pannello, isolamento dei percorsi, gestione delle credenziali, timeout e rimozione dei container tramite fixture. GitHub Actions costruisce i quattro runtime, carica lo schema reale DeerFlow e prova i registri e i server MCP delle 13 CLI. Consulta il risultato del workflow prima del deploy.

**Login con account reali e consumo RAM su Hostinger richiedono il collaudo sull'istanza con i tuoi account.** Non sono dichiarati già verificati. Le applicazioni Craft sono alpha; la presenza di un tool non garantisce ogni import/export.

## Deploy con Hostinger · Compose from URL

URL diretto:

```text
https://raw.githubusercontent.com/ggmm82/artcraft-deerflow/main/compose.hostinger.yaml
```

1. In Hostinger apri VPS → Docker Manager → Compose → Compose from URL e inserisci l'URL.
2. Imposta `STUDIO_PASSWORD` con almeno 16 caratteri casuali. Non mettere password o credenziali CLI nel repository pubblico.
3. Imposta `TRAEFIK_HOST` con il dominio base fornito da Hostinger, per esempio `srv0000000.hstgr.cloud`. Il progetto sarà disponibile su `https://<nome-progetto>.<TRAEFIK_HOST>`.
4. Avvia il progetto. Hostinger scarica le quattro immagini pubbliche e già collaudate da `ghcr.io/ggmm82`; il Compose non richiede BuildKit e non compila sulla VPS.
5. Apri il dominio e crea il primo account amministratore DeerFlow. La password `STUDIO_PASSWORD` protegge i segreti interni e non è la password dell'account DeerFlow.
6. Apri **La tua squadra**, scegli DeepSeek e incolla la chiave, oppure scegli Codex o Gemini e completa il collegamento ufficiale.
7. Lascia **Automatico** oppure scegli un modello e premi **Salva e attiva la squadra**. La scelta vale per tutti gli specialisti e le loro skills. Anche **Impostazioni → Modelli** rimanda a questo pannello.
8. Premi **Risolvi un problema**, carica eventuali file e descrivi cosa ti serve. La chat è già sul profilo **Squadra ArtCraft**: non occorre scegliere un altro coordinatore.

Il Compose Hostinger pubblica Gateway e frontend tramite etichette lette dal Traefik in modalità host e non richiede una rete esterna né occupa direttamente porte della VPS. Il proxy Caddy rimane soltanto nel Compose locale di sviluppo.

Hostinger documenta Compose da URL e la gestione delle variabili nella [guida ufficiale](https://www.hostinger.com/support/12040815-how-to-deploy-your-first-container-with-hostinger-docker-manager/). Le immagini del file Hostinger sono fissate al commit che le ha prodotte e sono scaricabili senza `docker login`.

## Uso con DeepSeek API

Non serve collegare account Codex/Gemini per usare DeepSeek:

1. Apri **La tua squadra**, incolla la chiave DeepSeek e premi **Salva e attiva la squadra**. **Automatico** sceglie tra i modelli effettivamente disponibili nell’account; una chiave o un modello rifiutati non cambiano la configurazione.
2. Premi **Risolvi un problema**, carica i file e descrivi il risultato. Il coordinatore e tutti i 13 specialisti usano già il modello condiviso.
3. Scarica i prodotti consegnati in chat. Per cambiare modello, torna allo stesso pannello: la chiave già collegata non va reinserita e le skills dei singoli ruoli restano attive.

Il salvataggio della squadra rimuove le vecchie scelte di motore/modello dei singoli specialisti, preservando skills aggiuntive, istruzioni e stato attivo. Le conversazioni esistenti mantengono l’identificatore del profilo; il nome visibile diventa **Squadra ArtCraft**.

Il [collaudo utente documentato](docs/COLLAUDO-UTENTE-DEEPSEEK.md) verifica con la chiave DeepSeek reale configurazione unica, scelta automatica di GridCraft e WordCraft, download e controllo indipendente di XLSX/DOCX/PDF, oltre alla riapertura dopo riavvio. La [guida della squadra](docs/CONFIGURAZIONE-SQUADRA.md) descrive il percorso dal problema ai file finali.

La chiave resta nel volume privato `studio-state`, separata dalla configurazione dei modelli e dalle risposte pubbliche. Il worker DeepSeek riceve la cartella credenziali in sola lettura; come gli altri motori è destinato a un proprietario fidato. Le richieste del coordinatore e degli specialisti consumano la quota API DeepSeek. Un incarico ha timeout e limite di turni; errori, file mancanti o manifest non validi non vengono presentati come successo.

## Prova di collaborazione

Carica un XLSX e scrivi:

> Devo presentare queste vendite al cliente. Prepara un foglio con i totali verificati e una presentazione chiara in italiano, con grafici e file modificabili.

Una conversazione è uno spazio di lavoro. I container sono separati tra incarichi, mentre i colleghi della stessa conversazione possono leggere i file condivisi. La collaborazione avviene tramite coordinatore e file, non tramite una chat autonoma tra processi sempre accesi.

## Catalogo

| Programma | Specialista | CLI | Ambito |
|---|---|---|---|
| PhotoCraft | photocraft | photocraft-cli | Immagini e ritocco |
| VectorCraft | vectorcraft | vectorcraft-cli | SVG e grafica vettoriale |
| FilmCraft | filmcraft | filmcraft-cli | Montaggio video |
| LightCraft | lightcraft | lightcraft-cli | Foto e RAW |
| PdfCraft | pdfcraft | pdfcraft-cli | PDF e moduli |
| EffectCraft | effectcraft | effectcraft-cli | Animazione ed effetti |
| DesignCraft | designcraft | designcraft-cli | Impaginazione |
| GridCraft | gridcraft | gridcraft-cli | XLSX, formule e grafici |
| WordCraft | wordcraft | wordcraft-cli | Documenti DOCX |
| DeckCraft | deckcraft | deckcraft-cli | Presentazioni PPTX |
| CADCraft | cadcraft | cadcraft-cli | CAD e DXF |
| SoundCraft | soundcraft | soundcraft-cli | Audio e mix |
| FigCraft | figcraft | figcraft-cli | Interfacce e prototipi |

Sono incluse 13 skills specifiche dei programmi, una procedura comune e una skill di coordinamento. I comandi e gli schemi completi vengono scoperti dalla release effettivamente installata, con `craft help`, `craft commands`, `craft tools` e `craft batch`. Il batch conserva lo stato MCP tra apertura, modifica e salvataggio.

Ogni skill distingue il proprio ambito dagli specialisti vicini e definisce ispezione iniziale, procedura, controlli specifici del formato e limiti di compatibilità. Il worker assegna una cartella distinta tramite `ARTCRAFT_OUTPUT_DIR`, avvia la CLI in quella cartella e verifica `handoff.json` prima di restituire successo: gli output devono esistere, essere non vuoti e restare nella cartella assegnata. I controlli di qualità riportano `passed`, `failed` o `not_run` con evidenze; la presenza dei file non dimostra la qualità visiva o audio.

## Avvio locale

```bash
cp .env.example .env
# Compila STUDIO_PASSWORD e le impostazioni del dominio in .env.
docker compose build
docker compose up -d
```

`compose.hostinger.yaml` usa immagini pubbliche GHCR già costruite; `docker-compose.yaml` usa il checkout locale per sviluppo. Entrambi usano volumi nominati: non richiedono una cartella del repository montata sul server.

## Risorse e confini

Limiti Hostinger configurati: Gateway 1.024 MiB, frontend 512 MiB, Redis 128 MiB e un worker 1.536 MiB. Sono limiti di progetto, **non misure di RAM reali** né una garanzia che ogni rendering rientri in 4 GB. L'immagine contiene tutta la suite e richiede diversi GB su disco. Per video, RAW e composizioni grandi sarà necessario ridurre i lavori o aumentare le risorse.

L'installazione è per **un proprietario fidato**. Il Gateway controlla Docker; gli specialisti non ricevono il socket Docker, hanno un solo spazio di conversazione montato, un limite RAM/CPU e nessuna capability Linux. Le CLI devono accedere alle proprie credenziali e alla rete per usare l'abbonamento: questa non è una sandbox per codice ostile con segreti inaccessibili. Non condividere l'accesso Studio con persone non fidate.

Le credenziali restano nel volume privato `studio-state`; la storia delle CLI non viene copiata nei worker. Il refresh delle credenziali degli specialisti è serializzato. Non esistono promesse di utilizzo illimitato: quote e accesso ai modelli dipendono dagli account e dai provider.

## Manutenzione e sviluppo

La [verifica delle integrazioni e guida ai nuovi strumenti](docs/INTEGRAZIONI-E-NUOVI-STRUMENTI.md) descrive Codex/Gemini CLI, la copertura reale delle skills e la procedura automatizzata per aggiungere uno specialista senza un altro modello da configurare.

```bash
docker compose logs -f gateway
docker compose down                 # conserva i volumi
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate.py
```

Per provare le skill con DeepSeek imposta `DEEPSEEK_API_KEY` nell'ambiente della shell (mai nel repository), poi:

```bash
python scripts/evaluate_skills.py                     # piani dei 13 specialisti
python scripts/evaluate_skills.py --execute           # lavori reali Grid/Word/Sound
# Per completare un incarico interrotto senza ricreare i file:
python scripts/evaluate_skills.py --execute --agents gridcraft --resume reports/skills-RUN
```

I report e le consegne restano in `reports/`, esclusa da Git. Il modello viene scelto tra quelli esposti dall'API; `--model` permette di selezionarlo. La prima prova controlla struttura e scoperta dei comandi, senza assegnare un voto alla qualità del piano. `--execute` richiede Docker e avvia container senza rete, senza socket Docker e senza credenziali Codex/Gemini; solo il processo sul computer chiamante usa la chiave DeepSeek. Le verifiche dei file sono automatiche, mentre le dichiarazioni di qualità del modello restano da valutare. Questo banco di prova è distinto dal percorso DeepSeek integrato nel pannello e non sostituisce il collaudo utente né i login delle CLI. Ogni prova consuma la quota del provider.

Per verificare modifiche in produzione ricostruisci le immagini dal checkout oppure, dopo CI e pubblicazione, aggiorna i riferimenti `sha-…` del Compose Hostinger. I tag già fissati non ricevono le modifiche dei sorgenti automaticamente.

Dopo un workflow completo verde su `main`, l'artefatto `hostinger-compose-<SHA>` contiene il Compose con tutte le immagini di quel commit. È generato solo dopo il collaudo di avvio; il file Hostinger attualmente versionato conserva le immagini precedenti finché non viene aggiornato esplicitamente. `scripts/prepare_hostinger.py` permette di preparare lo stesso file controllando prima che le immagini siano pubblicate.

Esegui backup dei volumi `studio-state` e `deerflow-data` a servizi fermi. Non usare `down -v` salvo richiesta esplicita di cancellazione. Per aggiornare, modifica insieme `versions.lock.json`, versioni CLI nei Dockerfile, commit DeerFlow nei Compose/workflow e collaudi. I dati non si aggiornano automaticamente a un nuovo schema.

Il codice dell'integrazione è in `studio/`; il frontend upstream riceve soltanto un collegamento e la pagina del pannello. Dockerfile Gateway e frontend sono adattati dai corrispondenti file DeerFlow: la licenza originale è in `docs/DEERFLOW-LICENSE`.
