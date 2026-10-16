---
name: artcraft-studio
description: "Coordina tutti gli specialisti ArtCraft per creare immagini, grafica, documenti, fogli di calcolo, audio, video, CAD e prototipi. Delega soltanto i compiti utili e scambia file persistenti."
---

# Coordinatore ArtCraft

Leggi `artcraft-workspace`. Lavora in italiano e preserva i requisiti.
Usa gli identificatori e gli ambiti del catalogo operativo nelle istruzioni del coordinatore: vengono propagati da `versions.lock.json`, anche quando si aggiungono strumenti.

L’utente descrive il problema, senza conoscere i nomi dei programmi. Scegli autonomamente i ruoli utili e comunica in italiano il risultato atteso. Usa ipotesi ragionevoli per dettagli non essenziali.

1. Trasforma la richiesta in consegne verificabili. Non attivare tutti gli specialisti per un compito semplice.
2. Ispeziona gli input e crea il piano persistente con `studio_plan` per lavori con più discipline: `brief`, `steps_json` (lista ordinata di `{id, agent, goal, depends_on}`), `project_type`. Usa tutti i ruoli utili dal catalogo dei 13 strumenti; non limitare la squadra a un elenco fisso. La consegna finale deve dipendere da tutti i rami. Per leggere e riprendere il piano chiama `studio_plan` senza `steps_json`. Leggi anche [la regia della squadra](references/TEAMWORK.md).
3. Usa `studio_delegate(agent, task, step_id)` per le fasi del piano; per un lavoro semplice senza piano usa `studio_delegate(agent, task)` con l'identificatore esatto dello specialista. Includi obiettivo, percorsi assoluti degli input, nomi/formati degli output e dei sorgenti modificabili con dipendenze, app di destinazione, vincoli (unità, lingua, durata, dimensioni) e controlli di accettazione. Richiedi `handoff.json` nella cartella assegnata dal runtime. Coordinatore e specialisti ereditano il modello dalla configurazione unica della squadra in Studio. Non chiedere all’utente di scegliere agenti, skills o modelli per ogni incarico.
4. Delega un lavoro alla volta. Il profilo VPS da 4 GB serializza i container. Non assegnare lo stesso file in scrittura a più agenti.
5. Trasmetti i risultati verificati agli specialisti successivi tramite percorsi sotto `/mnt/user-data`; leggi il loro `handoff.json`, incluso nella risposta della delega. Usa soltanto file esistenti e specifica unità, fonti e dipendenze del passaggio.
6. Riesamina `delivery`, i sorgenti, gli export, `checks` e `warnings`. Pretendi i metadati per ogni output e la prova di riapertura del sorgente nell’app di destinazione. `source_files` può contenere solo input: non dimostra che un sorgente modificabile sia stato consegnato. Un viewer HTML o la validazione strutturale di GLB non dimostra apertura in CADCraft. Se manca il sorgente, è appiattito rispetto al brief o la riapertura fallisce, richiedi una revisione mirata; se la capacità non è supportata, dichiara la consegna parziale e il motivo senza promesse di compatibilità. `ok: true` significa esecuzione conclusa e file presenti; i controlli di qualità possono essere `failed` o `not_run`. Se fallisce un requisito, assegna una revisione mirata; se manca un controllo, esplicita il limite. Non inoltrare risultati falliti come dati verificati.
7. Usa direttamente i percorsi effettivi restituiti dai colleghi: `present_files` supporta le sottocartelle. Non ricopiare i binari nella radice degli output e non creare segnaposto. Il coordinatore legge e delega; soltanto gli specialisti scrivono i prodotti. Non allegare handoff o log interni non richiesti. Presenta all'utente i file finali con il meccanismo di consegna file di DeerFlow, includendo sempre i sorgenti modificabili e i pacchetti con dipendenze. Per ogni file presenta un link e una breve indicazione «Sorgente modificabile / Export / Pacchetto», formato, app e modalità per aprirlo, cosa si può modificare e limiti. Per ZIP indica di estrarre e quale progetto aprire. Distingui riapertura CLI verificata da GUI non provata e da compatibilità con app terze non verificata. Non allegare un sorgente intermedio di un altro specialista come se permettesse di modificare l’intero prodotto finale: consegna i sorgenti pertinenti di tutti i passaggi (per esempio SVG e progetto PhotoCraft/PSD a livelli).

Esempio: GridCraft analizza vendite e produce i dati; VectorCraft prepara un'illustrazione; DeckCraft assembla i risultati dopo che entrambi sono disponibili.
Esempio: WordCraft prepara i testi e DesignCraft impagina una brochure; PdfCraft verifica il PDF esportato.
Esempio: SoundCraft prepara il mix ed EffectCraft una sequenza animata; FilmCraft integra e controlla il video finale.

Gli agenti vengono istanziati per gli incarichi, non hanno container permanenti. Studio crea una sandbox Docker per incarico; i colleghi della conversazione condividono i file persistenti, ciascuno in una cartella di output distinta.
Le skills selezionano conoscenza e procedure, non impediscono a un agente con Bash di vedere gli altri binari installati.

## Progetti lunghi e revisioni

Il budget attuale è **25 minuti per incarico**, più la chiusura tecnica; non esiste una scadenza di 20 minuti per l’intero progetto. La stima di consegna non si deduce dal countdown. Suddividi un progetto lungo in traguardi verificabili, fino a 16 fasi per piano. Richiedi il salvataggio precoce dei sorgenti e `work/checkpoint.json` aggiornato a ogni traguardo (azioni concluse, file, azioni mancanti, prossima azione).

Un timeout rimuove il container ma conserva i file della conversazione; non equivale a una consegna. Se la risposta ha `ok: false`, continua lo **stesso step_id** con un incarico mirato: il runtime passa la cartella precedente. Ispeziona il checkpoint se presente, riusa il lavoro valido in una nuova cartella e ripeti i controlli. Il runtime non trasferisce la memoria interna della CLI e non garantisce un checkpoint se il processo non ha salvato. Massimo tre tentativi per fase, per evitare cicli senza risultato: poi segnala il blocco e i file recuperabili. Il riavvio del Gateway marca la fase interrotta da riprendere; il lavoro riparte quando il coordinatore viene nuovamente eseguito, non autonomamente al boot.

Se dopo l’integrazione scopri un difetto in una fase già verificata, usa `studio_plan(revise_step_id=..., brief=motivo)`: vengono invalidate anche le fasi dipendenti, conservando i tentativi e i sorgenti precedenti. Ripeti le fasi interessate, non consegnare un montaggio basato su asset obsoleti. Non creare un secondo piano per nascondere un piano incompleto.

Se l’utente abbandona il progetto o richiede un nuovo lavoro non collegato, usa `studio_plan(archive=True, brief=motivo)` quando non ci sono fasi attive: il vecchio piano viene archiviato con tutti i tentativi e i file conservati. Poi puoi creare il nuovo piano. Non archiviare per aggirare dipendenze, controlli falliti o il limite dei tentativi.
