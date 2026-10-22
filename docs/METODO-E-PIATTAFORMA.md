# Metodo di produzione e scelta della piattaforma

## Diagnosi verificata — 21 ottobre 2026

La quantità di strumenti non misura la qualità del prodotto. Nei due casi analizzati le CLI hanno prodotto file e sorgenti: il problema principale osservato è il passaggio da capacità tecniche a un metodo di realizzazione coerente. Non abbiamo verificato ogni comando del catalogo, né escluso errori di configurazione in altri progetti.

- Un campione vettoriale già eseguito con il modello maggiore è rimasto visivamente elementare. Un ruolo compilato non conferisce da solo competenza artistica o asset di qualità.
- Nell’animazione, dopo due campioni EffectCraft insufficienti, è stato scritto un renderer alternativo. Il rapporto ammetteva ancora geometrie elementari, camera fissa e limiti di finitura. Cambiare strumento non aveva risolto il difetto di costruzione del contenuto.
- I rapporti contenevano controlli falliti, mentre la memoria restituiva zero osservazioni. Il raccoglitore acquisiva lezioni esplicite e revisioni formali, perdendo i difetti dichiarati nei normali handoff, anche quando erano disponibili immagini e sorgenti.
- La revisione prevista non era arrivata a conclusione: interrompere un job o avere un errore del provider non deve cancellare le evidenze già prodotte.
- Il worker riceveva subito protocolli completi, ricette CLI e istruzioni di qualità. In due combinazioni rappresentative, il contesto statico misurato passava rispettivamente da 63.812 a 21.571 caratteri e da 58.999 a 18.351 dopo questa revisione. È una misura di carico delle istruzioni, non una prova di miglioramento estetico.

Il vantaggio delle prime versioni con un solo strumento è compatibile con maggiore continuità di sorgenti e metodo e minore costo d’integrazione. Non abbiamo un confronto controllato che ne provi la causa. Più strumenti danno più possibilità, ma possono anche introdurre conversioni, perdita di informazioni e cambi di metodo inutili.

## Correzioni

1. **Un responsabile del prodotto, contributi pertinenti.** I ruoli restano dinamici; non si impone una squadra numerosa né una sequenza valida solo per un settore.
2. **Diagnosi prima della sostituzione.** Distinguere errori di esecuzione, impostazioni, asset e capacità; conservare i sorgenti validi e confrontare la modifica sullo stesso requisito. Un campione riduce durata o estensione, non il livello di finitura atteso.
3. **Riferimenti su richiesta.** Il brief conserva incarico, vincoli, continuità e controlli essenziali. I protocolli completi restano disponibili nelle skills, ma ricette e schemi non vengono espansi preventivamente nel prompt di ogni worker.
4. **Feedback oltre i cambi di ruolo.** Il prossimo incarico riceve un numero limitato di difetti dichiarati, con percorsi e impronte dei file. Sono evidenze da verificare, non nuove istruzioni o lezioni approvate.
5. **Esperienza anche dai tentativi incompleti.** Un handoff con controlli falliti e almeno un artefatto locale può diventare osservazione persistente. La raccolta considera al massimo tre piccoli file per rapporto, entro 16 MiB, privilegiando le anteprime. Non legge interi render o archivi a ogni raccolta. Il coordinatore deve valutare se esiste una lezione trasferibile, oppure motivare lo scarto. Il metodo generale richiede accettazione; la sola conoscenza tecnica può attivarsi automaticamente quando supera i controlli operativi già previsti.

La riacquisizione offline dei tre tentativi reali ha conservato quattro osservazioni negative, nessuna lezione automaticamente approvata e zero duplicati alla seconda raccolta. La copia locale include rapporti e anteprime, non ogni file dell’archivio originale. Nessuna modifica alla conversazione di produzione.

## Cosa manca davvero

I controlli tecnici verificano esistenza, formato, riapertura e alcuni requisiti misurabili. Non certificano gusto, fedeltà a un riferimento, qualità del disegno o qualità della scrittura. L’attuale registro delle capacità non offre ascolto percettivo: volume, durata e presenza di una traccia non equivalgono ad ascoltarla.

Per un lavoro specifico possono mancare asset, un modello capace di crearli o una capacità di osservazione. Va identificato quel limite e proposto all’utente; aggiungere un’altra CLI o riattivare uno strumento escluso non è una soluzione universale. Restano rispettate le disattivazioni in Agents/Skills. Questa PR non aggiunge strumenti e non promette qualità professionale automatica.

## DeerFlow, Multica e alternative

Valutazione della documentazione ufficiale, non un collaudo comparativo delle piattaforme installate.

| Piattaforma | Utilità concreta | Limite rispetto al problema osservato |
| --- | --- | --- |
| [DeerFlow](https://deerflow.tech/en/docs/harness/skills) | Skills caricate quando servono, contesti separati, agenti e delega dinamica | Il sovraccarico rilevato nasceva dal worker ArtCraft personalizzato; non è imposto dalla piattaforma. Correggerlo conserva runtime e integrazioni già collaudati. |
| [Multica](https://github.com/multica-ai/multica) | Gestione del lavoro con issue, agenti CLI, squadre, responsabilità e revisione umana; self-hosted, source-available | Le [squadre](https://multica.ai/docs/squads) instradano il lavoro verso i membri adatti, senza far lavorare tutti automaticamente. Le [skills](https://multica.ai/docs/skills) sono procedure riutilizzabili: non aggiungono asset o competenza artistica al modello. |
| [OpenHands](https://docs.openhands.dev/overview/introduction) | SDK e ambiente per agenti software, esecuzione e controllo delle attività | Interessante per sviluppo software e gestione dell’esecuzione; non risolve da solo la produzione professionale nei diversi domini ArtCraft. |

**Scelta:** correggere prima il metodo e la raccolta delle evidenze in DeerFlow. Una migrazione ora trasferirebbe buona parte dei problemi insieme a modelli, strumenti e procedure. Multica merita un prototipo separato se il limite dominante resta la gestione del lavoro e della squadra, con confronto su identici brief, modelli, strumenti e budget.

## Validazione e limiti

I test coprono raccolta dopo interruzione, isolamento dei file, percorsi virtuali, limiti di lettura, deduplicazione, nessuna approvazione implicita, trasferimento delle osservazioni al ruolo successivo e accessibilità dei protocolli. I test esistenti verificano anche policy, sorgenti e integrazioni.

La misura successiva è un confronto end-to-end su brief e riferimenti identici: qualità osservata del risultato, riapertura dei sorgenti, numero di revisioni, tempo e costo. Non basta contare agenti, file o comandi riusciti. Le modifiche del prompt sono un’ipotesi di miglioramento da misurare; i test deterministici non garantiscono il risultato creativo di ogni modello.

## Correzione dei contratti di completamento

Un successivo caso reale ha evidenziato tre difetti distinti dal metodo creativo:

- Il `read_file` nativo consente i percorsi della conversazione in `workspace`, `uploads` e `outputs`, ma rifiuta `.studio-project`. Le risposte di controllo indirizzavano il coordinatore proprio lì. `studio_read_context` legge soltanto i riferimenti immutabili di quel progetto, verificando hash, confine della conversazione, dimensione e paginazione. Non amplia l’accesso del lettore nativo al filesystem host; viene aggiunto anche alle configurazioni persistenti esistenti.
- I pacchetti portabili possono contenere copie degli export scaricabili. La copertura dei sorgenti non riconosceva l’equivalenza e chiedeva di documentare nuovamente gli stessi file dentro lo ZIP. Ora la copertura si trasferisce soltanto fra copie con stesso nome e SHA-256 identico; un file diverso resta da documentare. Gli errori indicano anche archivio e membro, per distinguere le copie.
- Una revisione salvata in `quality-review.json` veniva persa se il worker non scriveva anche `handoff.json`. Per i soli job di revisione, il runtime può compilare l’involucro mancante o recuperare un involucro non valido dopo aver validato il rapporto esistente e i suoi input. Conserva l’originale in work/ e mantiene i controlli dichiarati falliti. Mantiene i giudizi del revisore, non modifica il prodotto e rifiuta un hash dichiarato che non corrisponde al prodotto. Una revisione consegna un rapporto: non richiede un altro export audiovisivo per soddisfare i requisiti del prodotto esaminato.

Riproduzione offline sui file reali: l’associazione dei sorgenti passa senza rigenerare o modificare i file; la revisione viene acquisita e conserva `needs_review`, con ascolto e confronto rimasti non verificati. Il recupero del rapporto non approva automaticamente la qualità e non esegue la rigenerazione dei sorgenti dichiarata dal produttore.

## Lezioni imperfette e registro della conversazione

Altri due incarichi hanno salvato sei appunti CLI con strutture diverse dal protocollo (`finding`/`benefit` oppure una lista di `lesson` testuali). Il raccoglitore li scartava. Ora quei formati vengono conservati come `needs_generalization`, con origine e hash del file; il file prova solo l’esistenza dell’appunto, non la correttezza del contenuto. Nessuna attivazione automatica. Le note canoniche con prove non valide restano rifiutate: non aggiriamo i controlli operativi. La riproduzione sui sei appunti recupera sei fonti, zero duplicati e zero lezioni approvate. La generalizzazione richiede ancora il coordinatore disponibile, oppure il comando di valutazione delle osservazioni nel pannello Lezioni; una quota esaurita può fermare quel passaggio, ma non cancella gli appunti.

L’errore generico di Antigravity suggeriva di verificare anche la quota; il classificatore interpretava quel suggerimento come prova di credito esaurito. Il nuovo diagnostico conserva la causa effettivamente fornita dalla CLI e tratta i vecchi messaggi generici come errore non confermato. Un limite Codex esplicito rimane un vero blocco di quota.

La scheda **Registro** aggiunge timestamp, attore, operazione ed esito per l’intera conversazione: ricezione del turno, richieste al modello, strumenti nativi, avanzamenti di tutti i worker e azioni dell’utente nel pannello. Usa i middleware nativi di DeerFlow e un registro persistente per conversazione, paginato ed esportabile in CSV. Non dipende dalla pagina aperta e non si ferma agli ultimi 60 eventi della sandbox. Richieste/risposte complete, credenziali e ragionamenti interni non vengono copiati. Gli eventi precedenti all’installazione non sono inventati; il registro completo parte dall’aggiornamento. I giudizi artistici del modello restano fallibili anche quando l’esecuzione viene registrata correttamente.

Il collaudo ripetuto ha inoltre individuato un errore reale di configurazione Calibre: `ensure_app(headless=True)` imposta esplicitamente la piattaforma e prevale su `QT_QPA_PLATFORM`. L’adattatore configura anche `CALIBRE_HEADLESS_PLATFORM=xcb`, usando Xvfb e OpenGL software già previsti. Il controllo nativo viene ripetuto tre volte nel container senza GPU; non si nasconde il crash con un retry generico.

La verifica ripetuta ha anche evidenziato una differenza dal runtime: i container CI dei workflow nativi non usavano `--init`, già presente nei worker di produzione. Nelle prove locali sono rimasti numerosi processi figli terminati non raccolti dal PID 1; il collaudo CI impone 256 processi. I controlli nativi ora usano lo stesso init della produzione, senza alzare i limiti o eliminare le tre ripetizioni. Tre workflow Calibre completi e cinque riaperture semplici sono passati localmente; la conferma con i limiti Docker resta affidata alla CI.

Il caso successivo ha mostrato un problema di convergenza e comunicazione: una preview di 6 secondi ha richiesto circa 17 minuti; una correzione di altri 12 minuti ha prodotto 6,5 secondi, ma ha dichiarato ancora difetti di scala, silhouette e assestamento. Il coordinatore è passato a un terzo campione senza chiamare `present_files`. Questo non prova un guasto della sandbox: i comandi continuavano e i file esistevano. Non prova neppure che l’app sapesse raggiungere automaticamente la finitura richiesta.

La correzione distingue il contratto finale dalla domanda di una prova. Un rapporto può dichiarare `scope` checkpoint con gli ID selezionati e riceve un secondo verdetto; il verdetto completo resta invariato e continua a impedire un falso completamento. La continuazione distingue difetti osservati, verifiche ancora eseguibili e modalità indisponibili che richiedono l’utente. Un fallimento tecnico osservato non viene più cancellato soltanto perché il coordinatore ha accorpato quel controllo a un criterio percettivo. Le skills chiedono requisiti separati per proprietà osservabile.

Il sorgente della preview rimane obbligatorio; il confezionamento portabile può essere rinviato fino alla consegna. `finalization_pending` rimane visibile e impedisce anche l’accettazione manuale come consegna completa; gli ZIP effettivamente prodotti conservano tutti i controlli. Il pannello espone l’ultimo campione completato anche durante la correzione successiva, con sorgenti della stessa lavorazione, senza sostituire un prodotto finale selezionato. Le risposte al coordinatore indirizzano direttamente a `present_files` per ogni nuova preview utilizzabile. Le correzioni già dichiarate dal produttore non richiedono un’altra revisione equivalente prima di essere affrontate: va provata prima la causa prioritaria con il controllo pertinente meno costoso.

Questi controlli correggono errori di avanzamento, visibilità e verifica; non trasformano un ruolo compilato in una competenza artistica dimostrata. Il caso reale, al momento dell’analisi, non aveva prodotto un master approvato. Le prove automatiche verificano stati, conservazione dei file e rifiuto delle approvazioni improprie; il confronto creativo completo richiede un nuovo collaudo dopo il deploy.

La verifica della chiusura dello stesso caso ha poi confermato un errore ulteriore: il run è terminato con successo tecnico, sandbox liberate, ma nessun master completo. Il coordinatore ha descritto la bozza e le correzioni ancora necessarie e ha chiuso senza una dipendenza concreta dall’utente. Un middleware nativo rileva questa uscita dopo produzione avviata nel turno e richiama il coordinatore al prossimo obiettivo, al massimo due volte. Rispetta pause, quota/autenticazione, budget/stop nativi, richieste reali all’utente e verifiche sensoriali indisponibili; non trasforma una domanda informativa in produzione. Il feedback è limitato alla richiesta al modello e non viene salvato come messaggio dell’utente. Esauriti i richiami, il progetto mostra esplicitamente `incomplete_objective` e il Registro riporta l’obiettivo non completato, anziché suggerire che il prodotto sia concluso.

Sono emerse anche modifiche EffectCraft non persistite tra processi e tre fallimenti del protocollo di consegna. La skill spiega `--save`/`--save-as`, controllo delle tracce animate e riapertura in un processo nuovo; il workflow nativo verifica una modifica successiva alla creazione e il frame riaperto. Il comando `handoff.py validate` consente a tutte le CLI di correggere il manifest nella stessa sessione, con lo stesso schema di `submit_handoff`. Non ricostruisce inventari da file indovinati, non attenua le verifiche e non approva la qualità: il controllo può riuscire anche se conserva un `failed` dichiarato sul contenuto.

La selezione di una bozza e l’approvazione finale sono distinte anche per i file di consegne fallite. In `status=review` un file verificato da una revisione separata può essere selezionato come bozza se hash e contratto corrispondono; i requisiti media finali non impediscono di mostrarlo. Nessuna nuova approvazione viene dedotta da tale selezione: per `ready` restano necessari consegna tecnica valida, sorgenti e verifiche finali, e byte diversi invalidano il riferimento alla bozza revisionata.
