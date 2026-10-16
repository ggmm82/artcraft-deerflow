# Antigravity CLI con account Google

La voce **Antigravity · abbonamento Google** in **La tua squadra** usa il binario ufficiale `agy` **1.4.0**, sia per il coordinatore sia per i 13 specialisti. Non occorre una chiave AI Studio. Le richieste usano l’account collegato e le quote che Google rende disponibili a quell’account; un abbonamento non garantisce accesso illimitato a ogni modello.

## Collegamento dal browser

1. Distribuisci il Compose di prova della PR in un progetto Hostinger separato, secondo [la guida di aggiornamento](AGGIORNAMENTO-HOSTINGER.md).
2. Apri **La tua squadra**, scegli **Antigravity** e premi **Collega account Antigravity**.
3. Il pannello apre il flusso remoto del vero `agy`: segui **Apri il login ufficiale** (oppure **Copia link**), completa l’accesso sul sito Google e incolla il codice restituito nel campo del pannello. Non inserire la password Google in ArtCraft.
4. Il collegamento termina dopo che `agy models` ha confermato l’accesso al catalogo. Non viene eseguita una generazione di prova durante il login.
5. Scegli **Automatico** oppure aggiorna l’elenco dei modelli del tuo account. **Salva e attiva la squadra** propaga la scelta al coordinatore e a tutti gli specialisti, senza configurazioni per singola skill.
6. Prova una richiesta concreta, ad esempio: «Crea un robottino CAD modificabile, consegna il sorgente riaperto in CadCraft e un’anteprima; dichiara formati e limiti». Verifica anche i file scaricati, non soltanto il messaggio della chat.

**Migrazione:** le precedenti credenziali consumer Gemini CLI non costituiscono un collegamento Antigravity. Occorre rifare il login. Restano conservate sul volume, ma non vengono usate. I vecchi identificatori di modello del profilo Google vengono inizialmente sostituiti da `auto`; il pannello permette poi di scegliere un identificatore realmente restituito da `agy models`. L’identificatore interno `gemini` e la classe `StudioGeminiChatModel` sono conservati per compatibilità con configurazioni e conversazioni salvate.

## Esecuzione e isolamento

Il menu **Mode** della chat resta utilizzabile anche con Antigravity e DeepSeek: **Flash** avvia il flusso diretto, **Pro** abilita la pianificazione e **Ultra** aggiunge la delega ai sottoagenti prevista da DeerFlow. Sono modalità del flusso di lavoro, non nomi di modelli. L'opzione **Reasoning** compare solo quando il profilo espone quel controllo. Provider e modello restano configurati una sola volta in **La tua squadra** e sono condivisi con gli specialisti. Il numero di worker simultanei resta limitato dalle risorse configurate.

I lavori inviati dalla chat continuano sul server quando si chiude la pagina, si cambia conversazione o cade la connessione. Vale anche per modifica e rigenerazione di un messaggio. Riaprendo la conversazione, la chat usa la riconnessione al run e la cronologia persistita già previste da DeerFlow. Per interrompere il lavoro usare **Stop**. Questa continuità riguarda la disconnessione del browser: non garantisce l'esecuzione attraverso un riavvio o un aggiornamento dei container.

- Installazione nativa Linux amd64/arm64 con URL di release, SHA-512 fissato e SHA-256 pubblicato dal repository ufficiale in `scripts/antigravity.lock.json`. Non viene eseguito uno script remoto durante la build. Gli aggiornamenti automatici sono disabilitati per preservare la versione collaudata.
- Login e rinnovo dei token sono gestiti esclusivamente da `agy`. Su Linux senza D-Bus, il binario usa il proprio archivio `~/.gemini/antigravity-cli/antigravity-oauth-token`. ArtCraft conserva soltanto i file di autenticazione ammessi sul volume privato, con permessi `0600`; cronologia, log, plugin e configurazione del worker non vengono copiati tra conversazioni.
- `useG1Credits` è disabilitato: non si abilita automaticamente il consumo di crediti personali oltre la quota. Chiavi API e impostazioni esterne di provider non possono sostituire il login scelto nel pannello.
- Coordinatore: processo CLI in container senza mount della conversazione o socket Docker, agente personalizzato con il solo `finish` per consegnare la decisione e regole che negano comandi, file, rete degli strumenti e MCP. Il canale LLM della CLI rimane disponibile. `--json-schema` produce una decisione strutturata (`content`, `tool_calls`); DeerFlow esegue gli strumenti richiesti e restituisce i risultati nel turno successivo.
- Specialista: CLI nel container temporaneo della conversazione, skill e ricetta effettive, accesso ai file condivisi tramite `--add-dir`. Le autorizzazioni automatiche si applicano nel worker isolato. Anche il worker usa uno schema di conclusione (`summary`) e deve chiamare `finish`: un testo finale ripetuto non equivale alla chiusura del job. Il controllo obbligatorio di `handoff.json`, sorgenti modificabili, riapertura e limiti resta attivo.
- Il trasporto usa il protocollo documentato stdin/stdout `stream-json`, evitando limiti di lunghezza degli argomenti e prompt completi nell’elenco processi. Un risultato diverso da `SUCCESS` non diventa una consegna riuscita.

## Copertura del collaudo

Aggiornamento alla **1.4.0**: archivi ufficiali Linux amd64/arm64 verificati tramite digest GitHub, installazione e comandi reali amd64, protocollo headless senza account e regressioni automatiche. La versione è fissata nel lock; la build non segue il canale `latest`. Il collaudo autenticato descritto sotto è stato eseguito sulla precedente **1.3.5** e non viene presentato come una nuova prova OAuth sulla 1.4.0.

Verificati localmente il binario autentico 1.3.5, i flag, il protocollo e il login Google remoto completato con l’account fornito per il collaudo. La prova reale ha rilevato e corretto il formato del catalogo (tabulazioni, non soltanto spazi), i link OSC spezzati tra chunk del terminale e la necessità del tool nativo `finish` per ottenere `structured_output`. Catalogo autenticato e delega del coordinatore sono stati eseguiti con la CLI reale; le ulteriori evidenze della consegna sono riportate nella [PR #5](https://github.com/ggmm82/artcraft-deerflow/pull/5). I test automatici coprono scelta condivisa, migrazione, inoltro dei risultati degli strumenti, schema della delega, isolamento del coordinatore, copia selettiva dei token e rifiuto degli errori. Le risposte del modello nei test unitari sono fixture dichiarate.

**Da completare sulla VPS dopo l’aggiornamento:** nuovo login dal pannello corretto, attivazione della squadra e consegna completa dalla chat. Il collaudo autenticato locale non dimostra da solo che la nuova revisione sia già distribuita su Hostinger. Le quote residue dell’abbonamento e tutte le combinazioni dei 13 strumenti non sono certificate da un singolo incarico. Il login richiede l’azione del proprietario nel browser ufficiale Google.

## Fonti ufficiali

- [Installazione e login remoto](https://antigravity.google/docs/cli/install/)
- [Modalità headless, stream JSON, schema e catalogo modelli](https://antigravity.google/docs/cli/headless/)
- [Agenti personalizzati e strumenti consentiti](https://antigravity.google/docs/subagents/)
- [Skill e percorsi della CLI](https://antigravity.google/docs/skills/)
- [Permessi della CLI](https://antigravity.google/docs/permissions/)
- [Archivio credenziali e aggiornamenti](https://antigravity.google/docs/cli/troubleshooting/)
- [Annuncio della transizione Gemini CLI](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)

Quando il codice viene inviato, il pannello mostra lo stato di verifica e impedisce un secondo invio. Un codice rifiutato chiude il tentativo con un messaggio comprensibile. Riaprire il collegamento mentre è ancora attivo riprende la stessa sessione; non crea un altro URL. Le credenziali ricevute da Google vengono conservate anche se la successiva verifica del catalogo fallisce, senza dichiarare la squadra pronta prima del controllo.
