# Risultati, decisioni e contesto della squadra

La gestione è comune a qualsiasi progetto. Ruoli e competenze restano compilati sul problema; le CLI sono capacità selezionabili, senza un elenco di professioni o una pipeline per settore.

## Risposte di controllo

`studio_plan` e `studio_delegate` restituiscono JSON entro 8.000 caratteri, sotto la soglia di esternalizzazione da 12.000 del DeerFlow fissato. Il risultato completo viene salvato immutabile in `.studio-project/control-results`, con percorso virtuale e SHA-256 nel messaggio. Richieste originali, handoff, file e verifiche non vengono eliminati. Il browser usa la API completa del progetto.

`ok=true` riguarda l'esecuzione dell'incarico. `decision` distingue execution_failed, needs_revision, review_required, review_passed e work_complete; work_complete non è approvazione del prodotto. Conteggi di controlli falliti e non eseguiti rimangono visibili anche se l'inventario deve essere abbreviato. Le anomalie hanno priorità rispetto alle lunghe istruzioni di apertura. Le decisioni non indeboliscono i controlli tecnici o la revisione necessari per `status=ready`.

Se `details_required=true`, il coordinatore deve leggere il riferimento completo prima di decidere. Gli altri dettagli vanno letti quando servono, evitando di rimettere tutto il progetto in ogni turno. Un requisito globale ancora incompleto non obbliga a rigenerare una parte valida: va interpretato nel contesto della fase e degli altri incarichi.

## Squadra attuale e altre attività

L'orientamento conta le attività dei ruoli attivi, quelle senza ruolo per compatibilità e ogni attività realmente in esecuzione. I ruoli non presenti nel contesto attuale rimangono nella cronologia espandibile. Nessuno stato viene trasformato in completato o cancellato per effetto di questa proiezione. Ricompilare il ruolo rende nuovamente visibili i relativi incarichi; file e tentativi restano conservati.

Il conteggio descrive la squadra attuale, non una percentuale dell'intero progetto. La storia può contenere attività mai avviate: non è una lista di risultati già ottenuti.

## Fattibilità e qualità

Prima di escludere una capacità, il coordinatore deve distinguere operazioni native, composizione/authoring/programmazione e qualità raggiungibile. Un catalogo senza generazione automatica non dimostra da solo che un metodo sia impossibile. Una prova piccola, autorizzata e rappresentativa deve precedere l'estensione di una produzione ancora incerta. Il metodo, i file osservati e i difetti vanno registrati nella memoria dinamica del progetto.

Un revisore deve avere gli strumenti necessari ai controlli richiesti e distinguere osservazione propria da evidenza del produttore. Aggiungere una CLI non garantisce un miglioramento; serve il confronto sullo stesso input e sugli stessi criteri. Queste correzioni non installano un generatore d'immagini e non certificano automaticamente la qualità artistica o professionale di un elaborato.

## Verifiche

Test di regressione su inventari lunghi, fallimenti all'inizio di molte verifiche, mancata osservazione, quota, integrità dei dettagli e memoria dei progetti. Il test Gateway usa i wrapper LangChain effettivi. Il browser verifica conteggio della squadra attuale, accesso alle attività degli altri contesti, sorgenti, ripresa e pannello mobile. La CI esegue anche tutte le 15 CLI e l'avvio del Compose candidato prima del merge.

## Dalla revisione alla correzione

`quality-review.json` può contenere `revision_actions`: requisito, azione, motivo, priorità e strategia (`revise`, `change_method`, `verify`, `missing_dependency`). Il runtime conserva queste azioni nel tentativo, nel messaggio al coordinatore e nella vista Progetto; legge anche il campo precedente `targeted_corrections`. Prima venivano conservati i verdetti ma perse le indicazioni operative. La prima correzione diventa la prossima azione proposta, senza avviare un ciclo rigido di produzione.

Una revisione successiva può indicare `baseline_path` e `comparison`, con requisito, stato `improved/unchanged/regressed/not_verified` ed evidenza. Entrambi i file devono esistere ed essere tra gli input letti. Il runtime lega il confronto agli hash, rifiuta un miglioramento dichiarato su byte identici e mantiene non verificati i metodi che il modello non può osservare. Il confronto è facoltativo per compatibilità e per le prime versioni; le istruzioni lo richiedono quando si valuta una correzione. Non misura automaticamente il gusto o la competenza artistica.

## Perfezionare le skills senza perdere l'esperienza

Il sistema ha tre livelli distinti:

1. **Memoria del progetto:** decisioni e lezioni sintetiche passate a `studio_plan(memory_json=...)`, con riferimenti alle prove. Si uniscono le chiavi di primo livello; gli oggetti annidati vengono sostituiti. Usare una chiave stabile per lezione evita di sovrascrivere le altre. Il runtime conserva snapshot immutabili in `.studio-project/memory` e ricompila le skills dei ruoli; le versioni precedenti rimangono leggibili.
2. **Skills dinamiche del progetto:** procedure e controlli pertinenti al brief, compilati in `.studio-project/roles`. Una correzione verificata deve aggiornare il metodo del ruolo e il controllo che evita di ripetere il difetto. Il coordinatore deve effettuare l'aggiornamento: la presenza di un rapporto non modifica da sola la procedura.
3. **Skills condivise del software:** `skills/custom/artcraft-*/SKILL.md` e riferimenti versionati in Git. Un metodo riutilizzabile va generalizzato, provato su più casi e integrato con una PR e test. Le istruzioni CLI appartengono allo strumento; il controllo comune alla skill workspace; le regole di collaborazione alla skill studio. Le professioni continuano a essere compilate dinamicamente.

Una lezione utile contiene: problema osservato, condizioni di applicazione, metodo tentato, correzione, esito, versioni degli strumenti, prove prima/dopo e limiti. Separare sempre ipotesi, successo osservato su un caso e procedura riprodotta. Conservare anche tentativi falliti e regressioni con il loro contesto. Non inserire manoscritti, asset o credenziali nelle skills condivise. Una lezione deve poter essere smentita, aggiornata o ritirata; non può prevalere sul nuovo brief.

Richiesta pratica nella chat: «Registra nella memoria del progetto cosa ha funzionato e cosa no, con le prove; aggiorna le procedure dei ruoli pertinenti. Prepara una nota riutilizzabile senza dati privati per i progetti successivi». Oggi il riuso tra conversazioni richiede trasferire esplicitamente questa nota oppure integrare il metodo nelle skills via PR. Non esiste ancora una biblioteca automatica di lezioni tra progetti. `memory.enabled`, `memory.injection_enabled` e `skill_evolution.enabled` di DeerFlow restano disabilitati: non basta attivarli per avere promozione basata su evidenze, test e propagazione ai worker isolati.

La scheda Impostazioni → Memory riguarda il profilo personale di DeerFlow, non la memoria dei progetti. Può quindi risultare vuota dopo molte conversazioni. L'interfaccia spiega che apprendimento e utilizzo automatico del profilo sono disattivati; le annotazioni manuali restano archiviabili ed esportabili. Non interpreta il profilo vuoto come perdita dei progetti.

La conservazione dipende anche dal deployment: il volume `deerflow-data` contiene i dati delle conversazioni, inclusi memoria, ruoli e prove. Mantenerlo tra aggiornamenti e includerlo nei backup del VPS; un volume persistente non è un backup. Git conserva le skills distribuite, ma non i dati privati delle conversazioni. Nessuno di questi meccanismi addestra i pesi del modello.
