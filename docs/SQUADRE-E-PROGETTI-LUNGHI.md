# Squadre e progetti lunghi

Il coordinatore sceglie fra tutti i **13 specialisti** del catalogo. Un lavoro semplice può richiedere un solo ruolo; un prodotto multidisciplinare usa un piano persistente con obiettivi, responsabili, dipendenze e una fase finale che integra tutti i rami. Il pannello «Lavoro della squadra» mostra piano e stati anche dopo aver riaperto la chat. La configurazione del modello rimane unica.

## Esempio: robot che balla

La chat del 16 ottobre 2026 aveva delegato soltanto a EffectCraft: il robot e l’animazione erano prodotti dallo stesso specialista; mancavano passaggi dedicati per asset, musica e montaggio. La nuova regia prevede PhotoCraft per asset/texture separati, EffectCraft per animazione e rig supportato, SoundCraft per audio e FilmCraft per integrazione audiovisiva. CADCraft interviene se serve geometria tecnica supportata, LightCraft se ci sono RAW: non si attivano 13 strumenti senza necessità. Un video muto o asset già forniti possono giustificare omissioni, che devono corrispondere a requisiti espliciti dell’utente.

La presenza della CLI non implica generazione fotografica, composizione musicale generativa o rigging 3D arbitrari. Il coordinatore deve rispettare le capacità della release, dichiarare i limiti e mantenere il brief, senza sostituire silenziosamente il 3D con una vista isometrica. Il nome Macarena non rende disponibile il brano originale: si usa audio fornito/autorizzato o una base originale dichiarata, verificando sincro e ritmo.

## Collaborazione verificabile

`studio_plan` crea o legge il piano della conversazione. Accetta qualsiasi specialista di `versions.lock.json`; un nuovo strumento integrato nel catalogo e dotato di skill verificata non richiede una nuova configurazione del modello. Il profilo `animated_video` verifica la presenza delle quattro discipline pertinenti e la fase di integrazione; `custom` gestisce le altre squadre. Ogni fase ha `id`, `agent`, `goal`, `depends_on`. La lista è ordinata e priva di cicli; la fase finale deve integrare tutti i rami.

`studio_delegate(..., step_id=...)` controlla assegnazione e dipendenze. Inserisce nell’incarico i percorsi prodotti dai colleghi e richiede almeno un input effettivo di ciascuna dipendenza in `handoff.source_files`. Tutti i checks devono essere passed, i sorgenti disponibili e le riaperture dichiarate verificate, prima che la fase risulti completata. Se la fase ha un problema, resta da correggere e blocca le fasi dipendenti. `studio_plan(revise_step_id=..., brief=motivo)` riapre una fase già completata e invalida i controlli dei passaggi successivi, conservando i sorgenti.

Questi vincoli controllano struttura, percorsi e verifiche dichiarate. Non dimostrano da soli che un import sia stato usato artisticamente bene, che ogni requisito del brief sia soddisfatto o che vi sia stato ascolto/visione: sono necessari anche i controlli del coordinatore sul prodotto reale, con limiti espliciti per quelli non disponibili.

## Durata e recupero

Il limite attuale è **25 minuti per singolo incarico**, con fino a 60 secondi per chiusura/raccolta e un’attesa iniziale della squadra massima di due minuti. Non è una stima di consegna e non è il budget totale del progetto. Un progetto può superare 20 o 25 minuti distribuendo il lavoro fra fasi successive (fino a 16 nel piano). Sul VPS da 4 GB si esegue un solo worker alla volta.

Ogni worker deve salvare presto il sorgente e aggiornare `work/checkpoint.json` a ogni traguardo: azioni concluse, percorsi salvati, attività mancanti e prossima azione. Al timeout il container viene rimosso; i file già salvati restano nel volume della conversazione. La risposta riporta `ok: false`, la cartella precedente e le indicazioni di ripresa. Una continuazione sullo stesso `step_id` riceve automaticamente i riferimenti precedenti, ispeziona il lavoro recuperabile e lo riusa in una nuova cartella, poi ripete le verifiche. Non vengono trasferite la memoria interna della CLI o le modifiche mai salvate. Il checkpoint è disponibile soltanto se il worker lo ha scritto.

Il coordinatore deve continuare le fasi incomplete senza chiedere di nuovo il brief; il runtime consente fino a **tre tentativi per fase**, poi richiede di dichiarare il blocco anziché continuare senza limiti. Un riavvio del Gateway marca le fasi interrotte da riprendere: non avvia da solo un nuovo run LLM al boot. Dopo il riavvio il coordinatore può leggere il piano e proseguire quando la conversazione viene nuovamente eseguita. La chiusura della pagina continua a usare la modalità background già prevista.

Con DeepSeek un comando usa normalmente 90 secondi; render/export più lunghi possono richiedere `run_command.timeout_seconds` fino a 1200 secondi, sempre entro il residuo della fase. Questo valore riguarda un comando, non il progetto. Restano i limiti di turni, quota del provider e risorse del VPS.

## Collaudo

- Test di piano, tutti i 13 ruoli e aggiunta dinamica di un quattordicesimo; blocchi per assegnazione, dipendenze, controlli falliti, mancanza di sorgenti e input scollegati.
- Prova della ripresa, dei tre tentativi massimi, invalidazione dopo revisione e recupero della fase dopo riavvio, senza esporre metadati di un’altra conversazione.
- Chromium sul componente React effettivo con API di fixture dichiarate: piano, dipendenze, avanzamento, revisione, ricaricamento e cambio chat.
- `scripts/check_team_pipeline.py` usa CLI reali: asset PhotoCraft → animazione EffectCraft → mix SoundCraft → timeline video/audio FilmCraft. Verifica riapertura dei sorgenti, movimento, durata e audio finale non silenzioso. È una fixture tecnica piccola, non una valutazione artistica del robot e non un collaudo LLM autenticato. È eseguita anche in CI nell’immagine sandbox, con limiti di RAM/CPU del VPS.
- La CI conserva i workflow nativi per tutti e 13 gli strumenti, schema reale Gateway, autorizzazione della conversazione, build frontend e avvio delle immagini del Compose candidato.

Se l’utente abbandona il progetto o richiede un nuovo lavoro non collegato, usa `studio_plan(archive=True, brief=motivo)` quando non ci sono fasi attive: il vecchio piano viene archiviato con tutti i tentativi e i file conservati. Poi puoi creare il nuovo piano. Non archiviare per aggirare dipendenze, controlli falliti o il limite dei tentativi.
