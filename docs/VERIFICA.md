# Registro di verifica

## Locale

I controlli eseguiti vengono riportati nel commit e nei log del workflow. La suite `tests/test_studio.py` verifica catalogo configurabile, protezione da percorsi esterni, mount dei singoli workspace, limiti dei container, pulizia dopo timeout, lista dei file credenziali copiabili e rifiuto delle scritture web da un'altra origine. Docker è sostituito da fixture soltanto nei test unitari.

## CI

`.github/workflows/verify.yml` esegue i test, valida entrambi i Compose, costruisce Gateway/frontend/sandbox/proxy, carica schema e tool con la versione reale DeerFlow e prova tutte le CLI e i server MCP. La build viene bloccata se il punto di inserimento frontend è cambiato.

## Da eseguire con gli account del proprietario

- Login Codex e Gemini dal pannello, verifica della risposta Gemini e successivo incarico per entrambi i motori.
- Un XLSX analizzato da GridCraft e passato a DeckCraft nella medesima conversazione.
- Controllo dei file dopo rimozione del container e dopo riavvio della piattaforma.
- Consumo RAM della piattaforma inattiva e durante un incarico rappresentativo sulla VPS Hostinger.
- Accesso HTTPS, registrazione DeerFlow e collegamento dalla barra laterale.

Non vengono dichiarati già eseguiti questi test senza i loro risultati reali. Nessuna API key o credenziale di un account è inclusa nel repository.

## Risultato effettivo della prima build sandbox

Il job `images (sandbox)` del run [38613178438](https://github.com/ggmm82/artcraft-deerflow/actions/runs/38613178438) ha completato con successo la build e i 52 controlli: versione, help, registro comandi e lista MCP per ciascuna delle 13 CLI. Non ha eseguito incarichi con credenziali reali. Il controllo Gateway di quel primo run aveva rilevato un errore nel test di serializzazione del runtime interno; il test è stato corretto per verificare lo schema effettivamente inviato al modello.

## Rilascio Hostinger verificato

Il run [38620200922](https://github.com/ggmm82/artcraft-deerflow/actions/runs/38620200922) ha superato i 9 test applicativi, la validazione dei Compose, le quattro build e l'avvio completo. La prova di avvio ha scaricato i riferimenti GHCR del Compose Hostinger, inizializzato un account DeerFlow temporaneo, verificato sessione e CSRF, aperto il pannello Studio e salvato la configurazione di uno specialista attraverso il proxy. I quattro tag fissati nel Compose rispondono inoltre al pull anonimo dal registry.

Restano da eseguire sulla VPS reale il login con gli abbonamenti Codex e Gemini e la misura del consumo RAM durante un incarico rappresentativo.

Il run [38623365738](https://github.com/ggmm82/artcraft-deerflow/actions/runs/38623365738) ha verificato la variante Hostinger con `TRAEFIK_HOST`: nessun servizio pubblica porte host, Caddy non fa parte dello stack Hostinger e il Compose risulta valido. Le build, i controlli delle 13 CLI e l'avvio applicativo completo sono terminati con successo. Dopo il collaudo sulla VPS, la dichiarazione della rete esterna è stata rimossa per supportare il Traefik Hostinger in modalità host, che scopre i container dalle etichette senza creare `traefik-proxy`.


## Revisione e prove del 14 ottobre 2026

Verifiche locali sul checkout di revisione:

- 24 test Python superati, inclusi subprocess MCP con stato e arresto al primo errore, riferimenti `$result` non validi, risposte oltre 24 KB, errori di inizializzazione login e contratto di consegna del worker.
- `python scripts/validate.py`, entrambi i `docker compose config --quiet` e `git diff --check` superati.
- 58 controlli reali sulle CLI: versione, help, registro e lista MCP per ciascuna delle 13 applicazioni, più somma numerica, TXT→DOCX→PDF, lettura PDF, rendering DeckCraft ed export DXF. La seconda esecuzione usa il wrapper `craft.py` modificato.
- Worker eseguito anche in Docker con una CLI fixture: cartella corrente e variabile di output corrette, caricamento skill nativo e consegna valida accettati; completamento della CLI senza `handoff.json` rifiutato. Questo verifica il contratto del worker, non un login Codex reale.

Le CLI provengono dall'immagine sandbox fissata nel Compose Hostinger, digest `sha256:35765781f2b83e25b09817d28921418500a4a379515adde3e22976878ae97d4d`. Il driver VFS dell'ambiente di prova duplicava vari GB per container e ha esaurito il disco. Per continuare è stato esportato lo stesso filesystem e reimportato in una sola layer locale (`artcraft-review-flat:local`), senza modificare driver o configurazione del deploy. Le prove incomplete per spazio disco restano nei report; il valutatore ora impedisce esecuzioni Docker contemporanee nello stesso checkout e interrompe i tentativi su errori di infrastruttura.

### DeepSeek

La chiave è rimasta fuori dal repository. Le chiamate usano il modello `deepseek-flash`, effettivamente esposto dall'endpoint `/models` della chiave fornita. DeepSeek è un banco di prova opzionale, non un terzo motore aggiunto al pannello Studio.

La serie di pianificazione ha verificato i 13 specialisti: 11 risposte inizialmente valide, una risposta LightCraft con JSON malformato e una GridCraft con oggetto annidato; entrambe sono risultate valide ripetendo i due casi con un contratto di risposta più esplicito e sintetico. Sono controllati ID, scoperta help/commands/tools, presenza di passi, controlli e handoff. Non è una valutazione automatica della qualità professionale del piano né una prova degli export di tutte le 13 applicazioni.

Le prime esecuzioni reali GridCraft e WordCraft hanno creato file validi ma raggiunto il limite di 16 turni prima della scrittura del manifest. Il valutatore supporta ora `--resume`, ricorda di riservare turni alla consegna e le procedure chiedono di preparare il manifest appena esiste un output valido. La prova WordCraft ha inoltre confermato che il PDF esportato non può essere riaperto da WordCraft: la skill usa PdfCraft per verificarne testo e pagine.

I report completi, i comandi e i file generati restano in `reports/` (esclusa da Git). Le attestazioni di qualità del modello non sono equiparate a verifiche indipendenti: il runtime controlla schema, percorsi e presenza dei file, mentre la revisione controlla separatamente formule OOXML, integrità ZIP e struttura degli artefatti. Il modello non dichiara ispezione visiva o ascolto. Nella revisione è stata aperta separatamente l’anteprima della pagina DOCX: titolo e due paragrafi leggibili, senza sovrapposizioni o testo tagliato; non è una verifica visiva di tutte le applicazioni.

Il collaudo completo con login Codex/Gemini, frontend/Gateway ricostruiti, Traefik e misure RAM sulla VPS resta quello indicato sopra. I riferimenti Hostinger continuano a identificare le immagini già pubblicate: per distribuire questa revisione occorre una nuova build e l'aggiornamento dei tag dopo CI.


Risultati finali degli incarichi DeepSeek, dopo ripresa dei file già prodotti:

| Specialista | Risultato | Controllo indipendente della revisione |
|---|---|---|
| GridCraft | XLSX, CSV, rapporto e manifest valido | Archivio ZIP integro; celle 10, 20, 30 numeriche; formula `SUM(B2:B4)` conservata e cache pari a 60. |
| WordCraft | DOCX, PDF, PNG e manifest valido | DOCX integro con titolo e due paragrafi; PDF presente. Il modello verifica con PdfCraft una pagina A4 e testo coincidente; anteprima aperta separatamente nella revisione. |
| SoundCraft | Progetto, media, WAV, rapporto e manifest valido | ffprobe: 10 secondi, PCM 24 bit, stereo, 48 kHz. ffmpeg volumedetect: picco campione −4,7 dBFS, media −20 dB; controllo separato ebur128: −19,3 LUFS integrati, LRA 1,1 LU, true peak −4,7 dBFS. Nessun ascolto dichiarato. |

Il caso audio ha rilevato media mancanti dopo lo spostamento del progetto; sono stati copiati insieme al progetto e la skill richiede ora esplicitamente di preservare i percorsi relativi e riaprire dalla cartella finale. Tutti e tre i manifest sono stati accettati dal validatore, con i controlli non eseguiti dichiarati. Il manifest GridCraft conserva avvisi degli errori OCI avvenuti durante la ripresa: le prove precedenti e le verifiche numeriche successive sono distinte, non considerate un'esecuzione senza errori.

Una ripetizione aggiuntiva del piano WordCraft ha restituito prima l'ID del tool invece dello specialista, poi un riferimento a `handoff.json` con testo esplicativo. Il prompt del valutatore rende letterale l'ID richiesto; il controllo del nome file accetta percorsi e annotazioni conservando l'output originale. Questo illustra i limiti della serializzazione del modello e non viene presentato come prova di routing infallibile.

Il modello aveva marcato loudness/true peak del master come non eseguiti, dichiarando un misuratore EBU non disponibile. La revisione ha invece misurato il master con il filtro FFmpeg `ebur128=peak=true`; la skill ora ne richiede la scoperta esplicita prima di dichiararne l’assenza e vieta di riutilizzare le misure di un bounce differente.
