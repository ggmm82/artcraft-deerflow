# ArtCraft Studio · DeerFlow

[![Verify and build](https://github.com/ggmm82/artcraft-deerflow/actions/workflows/verify.yml/badge.svg)](https://github.com/ggmm82/artcraft-deerflow/actions/workflows/verify.yml)
[![Deploy on Hostinger](https://assets.hostinger.com/vps/deploy.svg)](https://www.hostinger.com/docker-hosting?compose_url=https://raw.githubusercontent.com/ggmm82/artcraft-deerflow/main/compose.hostinger.yaml)

DeerFlow con **13 specialisti ArtCraft**, motori **Codex, Gemini e DeepSeek API**, configurazione dal browser e **sandbox Docker temporanee**. Progetto indipendente; non è una distribuzione ufficiale dei prodotti integrati.

## Come funziona

- DeerFlow offre conversazioni, caricamento file, progetti, consegna degli artefatti, modelli e skills.
- Il pannello **ArtCraft Studio**, nella barra laterale di DeerFlow, collega Codex e Gemini tramite le procedure di autenticazione delle CLI originali.
- Ogni specialista ha motore, modello, skills aggiuntive, istruzioni e stato attivo configurabili dal browser. Le skills scelte entrano nel contesto del motore; per Codex e Gemini sono installate anche nel percorso nativo della CLI per quel solo incarico.
- Il coordinatore usa Codex oppure DeepSeek e invoca `studio_delegate`. Puoi aggiungere altri modelli API da Impostazioni → Modelli.
- Studio avvia un container per incarico, carica la procedura del programma pertinente e rimuove il container al termine, anche in caso di errore o timeout.
- I file della conversazione restano nel volume persistente. Il coordinatore passa al successivo specialista i percorsi dei risultati.
- Il profilo iniziale esegue **un solo specialista alla volta**, per la VPS da 4 GB. Non sono previsti modelli locali.

**Il coordinatore con abbonamento Gemini non è implementato:** Gemini CLI è disponibile come motore di tutti gli specialisti. Il coordinatore con abbonamento è Codex; un coordinatore Gemini via API può essere aggiunto dalle impostazioni standard. Non viene confuso un modello API con il login della CLI.

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
6. Apri **ArtCraft Studio** nella barra laterale, premi **Collega Codex**, apri il link ufficiale e completa il device login. Per **Collega Gemini**, apri il link Google e incolla il codice nel pannello. Non servono comandi SSH per autenticare le CLI.
7. Scegli il modello del coordinatore disponibile nel tuo account Codex. Per ogni specialista seleziona Codex o Gemini, eventuale modello e preferenze.
8. In DeerFlow seleziona **Studio · Codex**, carica un file e assegna il lavoro.

Il Compose Hostinger pubblica Gateway e frontend tramite etichette lette dal Traefik in modalità host e non richiede una rete esterna né occupa direttamente porte della VPS. Il proxy Caddy rimane soltanto nel Compose locale di sviluppo.

Hostinger documenta Compose da URL e la gestione delle variabili nella [guida ufficiale](https://www.hostinger.com/support/12040815-how-to-deploy-your-first-container-with-hostinger-docker-manager/). Le immagini del file Hostinger sono fissate al commit che le ha prodotte e sono scaricabili senza `docker login`.

## Uso con DeepSeek API

Non serve collegare account Codex/Gemini per usare DeepSeek:

1. Apri **ArtCraft Studio → DeepSeek API**, inserisci la chiave e premi **Collega DeepSeek**. Il modello vuoto viene scelto tra quelli effettivamente disponibili nell’account. Una chiave rifiutata non viene salvata.
2. Per gli specialisti desiderati scegli **DeepSeek API** nel campo Motore e salva. Il modello vuoto usa quello collegato; puoi indicare un altro ID DeepSeek disponibile.
3. Apri una nuova chat e seleziona **Studio · DeepSeek** nel selettore del modello.
4. Carica i file, richiedi il lavoro e scarica i risultati consegnati in chat. Il coordinatore usa `studio_delegate`; il worker esegue davvero le CLI ArtCraft con le procedure selezionate.

Il [collaudo utente documentato](docs/COLLAUDO-UTENTE-DEEPSEEK.md) verifica dal browser un CSV passato a GridCraft e WordCraft, con download e controllo indipendente di XLSX/DOCX/PDF.

La chiave resta nel volume privato `studio-state`, separata dalla configurazione dei modelli e dalle risposte pubbliche. Il worker DeepSeek riceve la cartella credenziali in sola lettura; come gli altri motori è destinato a un proprietario fidato. Le richieste del coordinatore e degli specialisti consumano la quota API DeepSeek. Un incarico ha timeout e limite di turni; errori, file mancanti o manifest non validi non vengono presentati come successo.

## Prova di collaborazione

Carica un XLSX e scrivi:

> Analizza questo foglio con gridcraft. Passa i dati verificati a deckcraft e crea una presentazione in italiano. Usa studio_delegate per ogni specialista. Consegna XLSX, PPTX e anteprime; indica i controlli eseguiti.

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

Esegui backup dei volumi `studio-state` e `deerflow-data` a servizi fermi. Non usare `down -v` salvo richiesta esplicita di cancellazione. Per aggiornare, modifica insieme `versions.lock.json`, versioni CLI nei Dockerfile, commit DeerFlow nei Compose/workflow e collaudi. I dati non si aggiornano automaticamente a un nuovo schema.

Il codice dell'integrazione è in `studio/`; il frontend upstream riceve soltanto un collegamento e la pagina del pannello. Dockerfile Gateway e frontend sono adattati dai corrispondenti file DeerFlow: la licenza originale è in `docs/DEERFLOW-LICENSE`.
