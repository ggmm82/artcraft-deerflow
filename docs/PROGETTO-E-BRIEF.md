# Capire il risultato prima di produrlo

La squadra può esistere senza essere comprensibile all’utente. Per questo la chat mantiene una scheda del progetto vicina alla casella di scrittura: titolo, forma della consegna, incarichi conclusi e attività attuale. Non serve cercare queste informazioni nella cronologia delle chiamate agli strumenti.

## Domande iniziali pertinenti al brief

Il coordinatore distingue cosa creare da come dovrà essere consegnato e usato. Chiede soltanto le scelte mancanti che cambiano sensibilmente il prodotto, gli strumenti o l’impegno necessario. La quantità non risolve automaticamente la forma: la stessa richiesta di contenuto può richiedere testo modificabile oppure un prodotto impaginato. Lo stesso principio distingue una proposta da un progetto esecutivo, un prototipo da software distribuibile o una bozza da una produzione finita.

Le domande sono generate dal brief, senza questionari per settore o cataloghi professionali. Se la richiesta è completa, il coordinatore registra il risultato e procede. Se l’utente delega una scelta, la assume esplicitamente senza chiedere conferme ripetute. Non c’è un’approvazione obbligatoria di ogni piano.

`studio_plan(outcome_json=...)` registra un oggetto generico:

| Campo | Significato |
| --- | --- |
| `title` | Nome breve del progetto |
| `result` | Cosa riceverà l’utente nella fase richiesta |
| `format` | Forma della consegna, espressa liberamente; non è un elenco di estensioni |
| `use` | Uso previsto e destinatari, quando pertinenti |
| `quality` | Livello di finitura atteso |
| `constraints`, `assumptions` | Liste di vincoli e ipotesi esplicite |
| `questions` | Al massimo tre scelte decisive ancora aperte |

Il coordinatore usa `ask_clarification` per raccogliere le risposte, poi aggiorna l’oggetto completo con le scelte effettive e `questions: []`. Se mancano risultato o forma della consegna, oppure esistono domande aperte, `studio_delegate` restituisce `needs_briefing` e non avvia worker. Non è un errore del provider e non richiede tentativi automatici. Il controllo non analizza semanticamente le risposte: il modello resta responsabile di individuare le scelte davvero mancanti e di registrarle fedelmente, senza inventare una decisione dell’utente.

## Un progetto leggibile

**Progetto** mostra risultato, consegna, uso, qualità, vincoli, ipotesi e domande aperte. La sezione **Dove siamo** distingue traguardo in corso, lavoro attuale e attività ancora previste. Il conteggio rappresenta incarichi conclusi rispetto al piano corrente: non è una percentuale di completamento, una previsione dei tempi o una sequenza obbligatoria. Le attività rimangono modificabili.

**Squadra** mostra missione, competenze assegnate e strumenti di ogni ruolo. Distingue chi è al lavoro, chi ha già lavorato e chi è soltanto previsto. Metodo e controlli sono consultabili nei dettagli. Essere assegnato a un ruolo non dimostra che ogni competenza sia stata applicata o ogni tool invocato: attività registrate e verifiche con evidenze restano distinte.

**Attività** conserva aggiornamenti degli incarichi e operazioni effettive. **Vedi risultato** e **File e sorgenti** mantengono prodotti, versioni, rapporti e sorgenti della stessa consegna raggruppati.

## Passaggio a ruoli e strumenti

La definizione del risultato viene inclusa negli incarichi e nella memoria versionata come `project_outcome`. Un suo cambiamento ricompila le skill dinamiche; il coordinatore adatta anche ruoli e strumenti quando la nuova forma richiede capacità diverse. Questa definizione generata non sostituisce i messaggi originali dell’utente né diventa una loro nuova versione autorizzata.

Gli incarichi registrano il compito specifico separatamente dall’obiettivo generale. Avviarli non sovrascrive più il riepilogo del coordinatore con il titolo di una lunga attività. I progetti precedenti conservano file e storia: alla prima nuova delega il coordinatore completa la definizione mancante o chiede le scelte necessarie, senza rigenerare il lavoro già valido.

## Collaudo

I test coprono richieste complete senza domande aggiuntive, richieste incomplete bloccate prima di avviare worker, ripresa dopo risposte, memoria e skill aggiornate, conservazione dei file precedenti e distinzione tra task, obiettivo e conteggio. Gli esempi comprendono domini diversi e un dominio non previsto, senza usare quei nomi nella logica di produzione.

Le prove browser verificano visibilità su desktop/mobile, informazioni della scheda progetto, competenze, ruoli attivi/previsti, domande aperte e isolamento tra conversazioni. La CI prova anche i wrapper reali nel Gateway e l’avvio del Compose. Le risposte dei provider nei test automatici sono fixture; il collaudo del comportamento conversazionale con un provider reale resta una verifica distinta.
