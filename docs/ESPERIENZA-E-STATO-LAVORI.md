# Esperienza riutilizzabile e stato dei lavori

La presenza della sandbox non è una prova di avanzamento. In **Attività** sono
separati il monitor della sandbox, l'attesa del modello o il comando in corso,
l'ultimo evento ricevuto dal modello e l'ultima modifica dei file. Dopo 90 secondi
senza attività il pannello indica che l'avanzamento va verificato, distinguendo
attesa del modello e comando senza esito. Non dichiara un blocco certo e non uccide
un lavoro lungo solo perché non produce nuovi file. Il limite resta un budget di
esecuzione, non una stima di consegna. Nessun ragionamento interno o comando con
credenziali viene pubblicato.

Le deleghe sono sincrone: durante una delega il coordinatore non può inviare un
secondo comando al worker. Un supervisore indipendente applica alle CLI Codex e
Antigravity un budget opzionale senza eventi del modello (disattivato inizialmente), configurabile
nello stesso pannello **La tua squadra → Risorse**. Se scade in attesa del modello,
termina la CLI e restituisce al coordinatore un errore recuperabile con i file
parziali. Non si applica durante un comando nativo in esecuzione. I trasporti API
mantengono i propri timeout HTTP più brevi. Non è una prova che il modello fosse
morto: è una scelta di budget. Non promette ripresa automatica durante un riavvio
Gateway e non interrompe l'intera conversazione.

## Come si conserva l'esperienza

Ogni utente ha un archivio nel proprio `users/<utente>/artcraft-experience` sul
volume dati DeerFlow. Non viene montato dentro le sandbox e non è condiviso con
altri utenti. Dopo una delega vengono raccolti automaticamente i criteri con esito
positivo o negativo e le correzioni di revisioni valutate dal runtime. Un comando
con uscita zero, una dichiarazione del modello o un controllo `not_run` non bastano.

Ogni osservazione conserva l'identità del progetto, gli hash di prodotto, rapporto
e contratto, il metodo osservato e le versioni note delle CLI del produttore.
Le procedure associate sono contesto dichiarato: non si presume che ogni loro
passo sia stato eseguito. Un esito positivo non certifica qualità universale,
competenza professionale o miglioramento artistico.

Prima di compilare le skills del progetto vengono selezionate al massimo sei
osservazioni pertinenti per ruolo (entro un budget di testo). La selezione è
basata sugli strumenti o, per ruoli senza CLI, sulla sovrapposizione dei termini;
non è una ricerca semantica e può tralasciare esperienze utili. Le esperienze di
CLI con versione diversa o sconosciuta restano archiviate ma non vengono inserite
automaticamente, salvo le preferenze esplicite dell’utente che restano candidati da verificare. La versione della skill include lo snapshot delle osservazioni:
le versioni precedenti rimangono riproducibili. Il brief attuale prevale sempre.

## Controllo e recupero

La scheda **Esperienza** di ogni chat mostra l'archivio privato dell'account.
Permette di escludere e riattivare osservazioni senza cancellare la storia, nonché
esportare l'archivio completo in JSON. **Squadra** mostra quante osservazioni sono
state incluse in ogni nuova skill. Le esclusioni si applicano alle compilazioni
successive: non riscrivono procedure già in esecuzione.

Per le chat precedenti all'aggiornamento usa **Recupera esperienza di questa chat**:
il recupero è ripetibile senza duplicati e importa soltanto revisioni utilizzabili
con prodotto ancora corrispondente all'hash registrato. Le versioni CLI storiche
non registrate non vengono indovinate. Non importa da solo tutte le vecchie chat,
né recupera dati già eliminati. Non modifica il lavoro in esecuzione.

L'archivio non sostituisce la memoria personale nella pagina Settings/Memory e non
attiva l'addestramento del modello o la riscrittura automatica delle skills Git.
Per non perdere l'esperienza nei deploy conserva e includi nei backup l'intero
volume `deerflow-data`, insieme alle cartelle dei progetti che contengono i file
originali. L'export JSON è un'esportazione delle osservazioni; non è un backup dei
prodotti né offre importazione automatica di procedure considerate affidabili.

## Conservare un metodo preferito

In **Esperienza**, scegli la lavorazione e descrivi cosa vuoi riutilizzare, poi premi
**Conserva questo metodo**. Si conservano la tua valutazione, il contesto dichiarato
del produttore, modello, strumenti e hash dei file. La preferenza è separata dagli
esiti delle verifiche e non porta il progetto a ready. Può riguardare un campione
riuscito anche se la consegna completa deve ancora finire.

Il software non deduce da un'immagine il processo che l'ha generata: i passaggi e
le capacità non registrati restano sconosciuti. I file restano nei progetti di
origine e vanno inclusi nel backup del volume. Una preferenza può suggerire una
procedura alla prossima skill pertinente; non garantisce lo stesso risultato né
trasforma una bitmap in tracciati modificabili.
