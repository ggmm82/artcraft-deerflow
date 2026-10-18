# Competenze compilate dal progetto

Gli strumenti installati e i ruoli professionali rispondono a domande diverse: con cosa eseguire il lavoro e quale metodo applicare. Il coordinatore definisce i ruoli dal brief, dalla fase richiesta e dalle incertezze effettive. Non c’è un catalogo di professioni né una lista di squadre per settore. Libri, edifici, film, software, eventi e domini futuri usano lo stesso percorso.

Prima della produzione il coordinatore registra il [risultato atteso e le scelte decisive](PROGETTO-E-BRIEF.md) con `outcome_json`. La definizione viene conservata nella memoria versionata e aggiorna le procedure quando cambia. Le domande aperte fermano le nuove deleghe fino alle risposte.

Per un progetto articolato il coordinatore registra un piano visibile e compila i ruoli con `studio_plan(roles_json=..., memory_json=...)`. Per una domanda semplice può rispondere direttamente. La scelta dei ruoli resta una decisione del modello: il runtime valida e rende eseguibili le procedure, senza un classificatore a parole chiave che imponga professioni o fasi.

## Contratto di un ruolo

`roles_json` è una lista di oggetti con:

| Campo | Contenuto |
| --- | --- |
| `id`, `title`, `mission` | Identità stabile e obiettivo concreto |
| `expertise` | Tecniche e conoscenze pertinenti agli input |
| `procedure` | Metodo operativo adattabile al problema |
| `checks` | Verifiche osservabili, con evidenze da raccogliere |
| `deliverables` | Risultati e sorgenti modificabili richiesti |
| `tools` | ID di strumenti realmente installati, anche nessuno |
| `inputs`, `risks` | File/fonti da leggere, assunzioni e limiti |

Tutti i campi dopo `mission` sono liste di stringhe. `expertise`, `procedure`, `checks` e `deliverables` devono essere non vuoti: un titolo non basta. Il compilatore rifiuta strumenti sconosciuti e istruzioni oltre i limiti di contesto, senza troncarle in silenzio. Il runtime rifiuta strumenti disabilitati.

Il coordinatore può aggiungere, sostituire o affinare i ruoli durante il lavoro. `roles_json` sostituisce l’elenco attivo: deve includere i ruoli ancora utili. Le versioni precedenti restano nei file. I limiti operativi sono 24 ruoli attivi, 4 skill CLI per incarico, 16 KiB per procedura e 60 KiB per l’elenco: servono a contenere il contesto, non definiscono professioni o un numero obbligatorio di colleghi.

## Compilazione ed esecuzione effettiva

Il compilatore produce `.studio-project/roles/<id>/<versione>/SKILL.md`. La versione comprende specifica del ruolo, hash della richiesta, memoria e versioni delle CLI selezionate. Il file include metodo, controlli e riferimenti alla richiesta completa. Una modifica pertinente produce una nuova versione; un contesto invariato conserva la stessa.

`studio_delegate(agent="workspace", role_id="ID", task="incarico concreto")` esegue il ruolo. Un’attività può indicare `agent="workspace"` e `role_id`; la delega con quel `step_id` recupera il ruolo. Il worker riceve la skill compilata e le skill native delle CLI scelte, mantenendo il modello unico della squadra. Codex e Antigravity ricevono anche il file nel proprio percorso di discovery; DeepSeek riceve la procedura nel contesto. Il contenuto è verificato tramite SHA-256 prima di essere caricato.

`workspace` è un esecutore di progetto, non una quindicesima CLI o un nuovo provider. Un ruolo senza CLI può lavorare su contenuti, codice o organizzazione con gli strumenti di base disponibili. Non implica che Python/Node/Git possano sostituire qualsiasi software professionale. Le deleghe tecniche native già esistenti continuano a funzionare.

Il pannello **Squadra** mostra missioni, strumenti, controlli previsti e versione; lo stato del lavoro mostra il ruolo effettivo. Questi controlli sono istruzioni da eseguire, non risultati già superati. Non viene imposto un flusso lineare o l’uso di tutti gli strumenti.

## Richiesta e memoria

I messaggi umani acquisiti sono conservati integralmente, con oscuramento delle credenziali riconosciute, in documenti privati versionati. `acceptance.request_manifest` ne contiene l’indice con hash. Le risposte degli strumenti e il pannello usano anteprime brevi; il worker deve leggere i documenti pertinenti. Anche i chiarimenti meno recenti restano nell’indice e contribuiscono alla versione della richiesta. Il pannello offre richiesta originale completa e indice dei messaggi.

`memory_json` è un oggetto libero, entro 40 KiB, che aggiorna chiavi della memoria: decisioni, riferimenti a file, fatti con fonti e questioni aperte. I contenuti lunghi restano nei file referenziati. La memoria è versionata e il suo hash viene verificato; non sostituisce le istruzioni originali né rende vere le affermazioni generate. Una nuova richiesta ricompila i ruoli e non eredita l’approvazione del prodotto precedente.

Le installazioni precedenti recuperano una richiesta abbreviata quando il testo integrale è ancora nella cronologia reale disponibile. Non è possibile ricostruire testo che non esiste più nel contesto o nei file.

## Limiti e verifiche

Compilare una skill struttura l’incarico: non addestra il modello, certifica un professionista o garantisce qualità artistica, correttezza tecnica o conformità normativa. Il compilatore verifica struttura, provenienza e disponibilità degli strumenti; il modello deve scegliere metodi competenti ed eseguire controlli reali. Capacità mancanti e osservazioni non eseguite restano esplicite. I contratti comuni di consegna, sorgenti, riapertura e revisione indipendente continuano ad applicarsi.

Le regressioni coprono domini diversi e uno non previsto, ruoli senza CLI e con più CLI, brief lunghi, chiarimenti oltre la finestra delle anteprime, versionamento, integrità, passaggio effettivo delle procedure al worker e visualizzazione dei ruoli nel browser. Le prove Gateway eseguono i wrapper reali di `studio_plan` e `studio_delegate`; le risposte dei provider sono fixture dichiarate. Questi test non sono una valutazione professionale degli elaborati prodotti da un modello reale.
