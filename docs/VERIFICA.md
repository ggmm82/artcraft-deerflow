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
