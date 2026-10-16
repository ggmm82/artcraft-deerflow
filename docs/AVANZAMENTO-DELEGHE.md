# Avanzamento degli specialisti

La chat mostra **Lavoro della squadra** durante `studio_delegate`. Il pannello indica specialista, provider/modello condiviso, riepilogo operativo, fase corrente, tempo trascorso, ultima attività, file provvisori e cronologia. Restano visibili gli incarichi attivi e gli ultimi tre conclusi. Il polling ogni due secondi è indipendente dallo stream del coordinatore: riaprire la pagina recupera lo stesso stato persistito.

Il worker registra automaticamente l'attesa del modello, l'avvio e la conclusione dei comandi, i cambiamenti dei file e i controlli di consegna. Codex viene osservato tramite gli eventi JSON `item.started/completed`; Antigravity tramite `step_update`; DeepSeek pubblica gli eventi del suo ciclo di strumenti. Gli specialisti possono aggiungere un breve piano o una decisione operativa con `report_progress` (DeepSeek) o `/usr/bin/python3 /opt/studio/progress.py --phase creating --summary "Creo il sorgente modificabile e poi verifico l’export"` (CLI). Le istruzioni comuni del worker richiedono questi riepiloghi ai cambi di fase.

La cronologia contiene azioni e sintesi operative. Prompt, ragionamenti interni, trascrizioni CLI, argomenti dei comandi e contenuti dei risultati non vengono pubblicati automaticamente. I riepiloghi espliciti vengono limitati e ripuliti dai formati comuni di credenziali.

## Attività, attese e limiti

- **Ultima attività:** ultimo evento effettivo o cambiamento dei file. Un heartbeat non aggiorna questo orario.
- **Worker raggiungibile:** il supervisore nel worker continua a rispondere. Non dimostra che un comando o il modello stiano facendo progressi.
- Dopo 90 secondi senza attività il pannello segnala l'assenza di nuovi avanzamenti. Dopo 15 secondi senza heartbeat segnala che lo stato va verificato. Sono indizi operativi, non diagnosi automatiche di blocco.
- Il worker ha un budget massimo di 25 minuti; l'attesa iniziale della squadra ha un limite di due minuti. La scadenza mostrata deriva dal budget effettivo del job. Non viene trasformata in una percentuale o una promessa di consegna.
- I file elencati prima della conclusione sono provvisori. La consegna resta soggetta alla validazione esistente di `handoff.json`, sorgenti modificabili, riapertura e limiti. Un errore o timeout rimane tale anche se esistono file parziali.

Lo stato è salvato in `.studio-jobs/<job-id>/progress.json` nella cartella privata della conversazione, separato dagli output scaricabili. Si conservano al massimo 60 eventi e 100 nomi di file per incarico nel payload. L'endpoint `GET /api/threads/<thread-id>/studio-jobs` richiede autenticazione, permesso di lettura e proprietà di una conversazione esistente; non richiede di essere amministratore. La risposta è `no-store` e contiene solo i campi pubblici ammessi.

Le deleghe avviate prima dell'aggiornamento non possono ricevere retroattivamente la cronologia. Un riavvio dei container non garantisce la prosecuzione del lavoro: la perdita del segnale viene mostrata come stato non confermato. Il pannello non reinvia automaticamente un incarico.

## Verifiche

I test coprono stato persistito, heartbeat distinto dall'attività, file e link simbolici, riepiloghi privi di trascrizioni e credenziali, protocollo Codex/Antigravity, progressi DeepSeek e timeout. Un sottoprocesso reale resta in attesa che il suo evento sia stato osservato, verificando che la lettura avvenga prima dell'uscita. Nella vera immagine Gateway si verificano autenticazione e isolamento fra utenti.

`scripts/check_delegate_progress_ui.py` esegue il componente React effettivo in Chromium con risposte API di test dichiarate: incarico di 18 minuti, aggiornamento, attesa prolungata, perdita heartbeat, errore di rete/riprova, ricaricamento, conclusione e cambio conversazione. Non richiede account o generazioni LLM. La build Next.js e l'avvio delle immagini complete rimangono parte della CI della PR.

Il pannello include ora anche il piano persistente della squadra, con dipendenze e stato delle fasi. Per budget, continuazioni e limiti del recupero vedi [Squadre e progetti lunghi](SQUADRE-E-PROGETTI-LUNGHI.md).
