# Verifica del completamento delle integrazioni

Sono stati aggiunti il coordinatore Gemini tramite il core ufficiale della CLI, il login OAuth guidato senza generazioni di prova e il rinnovo delle credenziali Codex tramite app-server. Codex, Gemini e DeepSeek si selezionano dallo stesso pannello e la scelta si propaga ai 13 specialisti.

Le 13 skills includono ricette specifiche caricate automaticamente nel contesto dei worker. La suite `scripts/acceptance.py` ha completato 13 casi nativi con 30 controlli su file: sorgenti riaperti, esportazioni, formule, testo, geometrie, immagini, video e audio. Sono passati anche i 59 controlli CLI/MCP. Si tratta di operazioni rappresentative, non di una certificazione di ogni funzione né di una valutazione percettiva.

La suite Python comprende 52 test: 48 eseguibili localmente e quattro che richiedono il Gateway DeerFlow. La CI esegue questi ultimi nell'immagine effettiva, verifica il bridge Node ufficiale, esegue le operazioni native nel sandbox limitato e avvia il Compose completo. Il rilascio Hostinger viene prodotto soltanto dopo tali verifiche.

La verifica browser locale del pannello Gemini ha superato otto controlli, inclusi propagazione, persistenza, conclusione automatica del login e viewport mobile. Il completamento OAuth è simulato nel test del pannello. Separatamente, il modulo ufficiale Gemini è stato avviato fino alla richiesta del codice Google; non è stato autenticato un account reale. Non è stata effettuata una nuova generazione DeepSeek durante questo completamento; il collaudo precedente è documentato in `COLLAUDO-UTENTE-DEEPSEEK.md`.

L'istanza https://artcraft-deerflow.srv1757745.hstgr.cloud/ risponde in HTTPS: pagina iniziale e login disponibili, readiness positiva con database/checkpointer/stream bridge operativi. Il catalogo Studio è protetto e risponde 401 senza sessione. Questi controlli non dimostrano che il VPS abbia già installato il nuovo rilascio: occorrono accesso applicativo e accesso al deployment per verificare o aggiornare quell'istanza.

Per un nuovo strumento seguire `INTEGRAZIONI-E-NUOVI-STRUMENTI.md`: catalogo versionato, checksum, adattatore CLI/MCP, skill con ricetta concreta e caso operativo obbligatorio. Il validatore impedisce di lasciare un'app senza ricetta o senza caso di collaudo.
