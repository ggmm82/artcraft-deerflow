# Collaudo utente con DeepSeek

> Report del percorso precedente con configurazione manuale. Il nuovo flusso della [configurazione unica](CONFIGURAZIONE-SQUADRA.md) è in collaudo.

Esito finale: **superato** sul percorso `CSV → GridCraft → WordCraft → download XLSX/DOCX/PDF` da un browser Chromium reale con Playwright. Il modello del coordinatore e degli specialisti è `deepseek-flash`; le chiamate sono state autenticate con la chiave del proprietario, senza inserirla nel codice o nei report.

## Percorso verificato

| Passo | Risultato osservato |
|---|---|
| Primo accesso | Apertura della home, collegamento “Get Started”, creazione dell’amministratore dal form. |
| Credenziale errata | Il pannello mostra “Chiave DeepSeek rifiutata”; la connessione non viene configurata. |
| Credenziale reale | “Chiave configurata”, campo password svuotato, modello scelto tra quelli esposti dall’API. |
| Specialisti | GridCraft e WordCraft impostati su DeepSeek API; scelta conservata dopo ricaricamento e riavvio del Gateway. |
| Chat | “Studio · DeepSeek” selezionato dal menu; CSV con 10, 20, 30 caricato tramite il controllo allegati. |
| Delega | Il coordinatore legge il CSV, avvia realmente i due worker Docker in sequenza e passa il riepilogo verificato al secondo. |
| Consegna | Entrambi i worker concludono con `handoff.json` valido nella propria cartella. GridCraft: 13 chiamate API; WordCraft: 17 chiamate API. |
| Stato del prodotto | Il run DeerFlow risulta `success`; circa 2 minuti e 15 secondi per lo scenario finale. |
| Download | Da una nuova sessione browser: accesso con account, riapertura della conversazione, download dell’archivio con tre file e dell’XLSX individuale tramite i pulsanti della chat. |
| Contenuti | XLSX integro: 10/20/30 numerici, formula `SUM(B2:B4)`, valore salvato 60. DOCX e PDF leggibili con totale 60. PDF di una pagina, aperto anche come immagine: testo leggibile senza tagli o sovrapposizioni. |
| Protezione | Senza sessione DeerFlow, catalogo Studio e download del file restituiscono 401. Le risposte pubbliche di catalogo e modelli non contengono la chiave. |

Gli handoff sono stati rivalidati sul filesystem persistito, montato in sola lettura nello stesso spazio virtuale `/mnt/user-data`. I conteggi delle chiamate provengono dai file di utilizzo dei worker; la verifica dei contenuti scaricati usa parser ZIP/XML e pypdf, separatamente dalle dichiarazioni del modello.

## Problemi rilevati e corretti

1. Il prodotto iniziale supportava soltanto Codex/Gemini negli specialisti: il vecchio banco di prova DeepSeek non era un collaudo della chat. È stato aggiunto il collegamento API dal pannello, un provider per il coordinatore e il ciclo di strumenti nel worker reale.
2. Un incarico poteva proporre un percorso di output in conflitto con la cartella assegnata dal runtime. Il prompt e la descrizione del tool rendono esplicita la priorità della cartella; i nomi richiesti dal coordinatore non la sostituiscono.
3. Il modello poteva terminare senza aver scritto un manifest valido. Il ciclo DeepSeek ora restituisce l’errore di validazione al modello e richiede la correzione entro il limite di turni/timeout. La seconda prova aveva consegnato file con errori di handoff; la ripetizione finale ha superato entrambe le deleghe senza tali errori.

Sono presenti test di regressione su chiave rifiutata, assenza della chiave dalle risposte e dal job, permessi 0600, mount credenziali in sola lettura e recupero da una risposta finale prematura. La chiave API resta separata dalla configurazione dei modelli. Non vengono registrati HAR, trace o corpi delle richieste di collegamento.

## Ambiente e limiti

Il collaudo è stato svolto su un’istanza temporanea locale, non sulla VPS Hostinger. Gateway e frontend derivano dai runtime DeerFlow fissati dal repository; il codice Studio del branch è montato nel Gateway e nei worker. Il frontend compilato è eseguito come processo locale per ridurre lo spazio occupato da Docker.

Il driver Docker VFS e il limite disco di 32 GB hanno bloccato il primo tentativo di creare un worker completo. Il percorso finale usa un runner Python Bookworm ridotto, con le vere CLI GridCraft 0.7.0, WordCraft 0.7.0 e PdfCraft 0.8.0 estratte dall’immagine sandbox fissata e montate in sola lettura. Proxy e CA dell’ambiente sono stati forniti ai processi di prova mantenendo la verifica TLS. Queste differenze di infrastruttura non sono inserite nel Compose di produzione.

Il collaudo dimostra il funzionamento utente del percorso descritto, non copre tutti i formati dei 13 programmi, i login OAuth Codex/Gemini, le misure RAM sulla VPS o Traefik Hostinger. Il deploy esistente non è stato modificato e richiede immagini aggiornate per ottenere il nuovo motore.

## Ripetizione

Su un’istanza di prova già avviata:

```bash
python -m pip install -r requirements-uat.txt
python -m playwright install chromium --only-shell
# Imposta nell’ambiente: DEEPSEEK_API_KEY, UAT_EMAIL, UAT_PASSWORD.
# Se il proxy usa Basic Auth, imposta anche UAT_HTTP_USER e UAT_HTTP_PASSWORD.
python scripts/uat_deepseek.py --base-url http://127.0.0.1:2026 --initialize-admin
```

`--initialize-admin` serve solo al primo avvio dell’istanza isolata. `--thread-url` riapre una conversazione già completata e ripete accesso, download e controlli dei contenuti senza nuove chiamate LLM. I report, screenshot e file scaricati restano in `reports/`, esclusa da Git. I tentativi iniziali e le loro limitazioni restano distinti dal risultato finale.
