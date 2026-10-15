# Verifica del completamento delle integrazioni

Sono stati aggiunti il coordinatore Gemini tramite il core ufficiale della CLI, il login OAuth guidato senza generazioni di prova e il rinnovo delle credenziali Codex tramite app-server. Codex, Gemini e DeepSeek si selezionano dallo stesso pannello e la scelta si propaga ai 13 specialisti.

Le 13 skills includono ricette specifiche caricate automaticamente nel contesto dei worker. La suite `scripts/acceptance.py` ha completato 13 casi nativi con 30 controlli su file: sorgenti riaperti, esportazioni, formule, testo, geometrie, immagini, video e audio. Sono passati anche i 59 controlli CLI/MCP. Si tratta di operazioni rappresentative, non di una certificazione di ogni funzione né di una valutazione percettiva.

La suite Python comprende 52 test: 48 eseguibili localmente e quattro che richiedono il Gateway DeerFlow. La CI esegue questi ultimi nell'immagine effettiva, verifica il bridge Node ufficiale, esegue le operazioni native nel sandbox limitato e avvia il Compose completo. Il rilascio Hostinger viene prodotto soltanto dopo tali verifiche.

La verifica browser locale del pannello Gemini ha superato otto controlli, inclusi propagazione, persistenza, conclusione automatica del login e viewport mobile. Il completamento OAuth è simulato nel test del pannello. Separatamente, il modulo ufficiale Gemini è stato avviato fino alla richiesta del codice Google; non è stato autenticato un account reale. Non è stata effettuata una nuova generazione DeepSeek durante questo completamento; il collaudo precedente è documentato in `COLLAUDO-UTENTE-DEEPSEEK.md`.

L'istanza https://artcraft-deerflow.srv1757745.hstgr.cloud/ risponde in HTTPS: pagina iniziale e login disponibili, readiness positiva con database/checkpointer/stream bridge operativi. Il catalogo Studio risponde 401 senza sessione. La registrazione e l’accesso di un account di collaudo ordinario sono riusciti; la versione installata espone ancora il vecchio catalogo senza squadra unica e risponde 404 al nuovo endpoint dei modelli. Il controllo ha evidenziato che un utente ordinario poteva accedere alla configurazione globale. Il nuovo Gateway richiede quindi il ruolo amministratore per tutte le rotte Studio, e la CI verifica il rifiuto 403 per catalogo, login provider e modifica della squadra. La chat resta disponibile agli utenti ordinari. Nessuna impostazione globale del VPS è stata modificata; l’account di collaudo resta presente per le verifiche successive. Questi controlli non dimostrano che il VPS abbia già installato il nuovo rilascio: occorrono accesso applicativo e accesso al deployment per verificare o aggiornare quell'istanza.

Per un nuovo strumento seguire `INTEGRAZIONI-E-NUOVI-STRUMENTI.md`: catalogo versionato, checksum, adattatore CLI/MCP, skill con ricetta concreta e caso operativo obbligatorio. Il validatore impedisce di lasciare un'app senza ricetta o senza caso di collaudo.

## Rilascio verificato

Runtime del commit `c91e8032d7eed716b4dd19c81526abe778f35158`, pubblicati dopo tutti e sei i job CI verdi: https://github.com/ggmm82/artcraft-deerflow/actions/runs/38702377698. Anche la CI della PR sullo stesso commit è verde: https://github.com/ggmm82/artcraft-deerflow/actions/runs/38702347332.

Compose scaricabile: https://github.com/ggmm82/artcraft-deerflow/releases/latest/download/compose.hostinger.yaml. Il download anonimo è stato confrontato con il file generato e il Compose nel repository è stato aggiornato agli stessi tag. Per l’installazione sul progetto esistente seguire `AGGIORNAMENTO-HOSTINGER.md`.
