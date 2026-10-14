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
