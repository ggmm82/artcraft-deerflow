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

Ai nuovi worker viene richiesto anche `work/method.json`: approccio effettivo,
azioni svolte, riferimenti agli script e limiti. Il registro esperienza ne conserva
una copia dichiarata con hash, insieme ai riferimenti e agli hash degli script.
Non riesegue la ricetta e non presume che le dichiarazioni siano dimostrate.
Per le lavorazioni storiche prive di questo documento compare «procedimento non
registrato»: la preferenza resta utile, ma non ricostruisce passaggi sconosciuti.

Per gli eventi strutturati Codex riconosciuti viene anche conservato
`work/tool-events.json`: identità e inizio/fine degli strumenti, senza argomenti,
prompt, testo delle risposte o ragionamenti. Permette di distinguere, quando la CLI
lo espone, un generatore immagini da un comando di impaginazione. Il registro
esperienza ne conserva il riferimento e l'hash, non ricostruisce eventi storici
mai salvati né presume che tutte le CLI espongano gli stessi eventi.

In **Attività → Interrompi questa fase** puoi fermare un worker della versione
aggiornata senza annullare la conversazione. L'API verifica sia il proprietario
della chat sia le etichette Docker di installazione e workspace. Il coordinatore
riceve l'interruzione e i percorsi parziali; non deve rilanciare automaticamente lo
stesso incarico. Restano i file già salvati, mentre lo stato non salvato del
processo può andare perso. Il comando non richiede socket nelle sandbox.

## Cambiare metodo durante il progetto

In **Progetto → Le tue scelte sul metodo** puoi scegliere immagini generate,
grafica vettoriale modificabile, tecnica mista o lasciare la scelta alla squadra.
«Come indicato nel brief o in chat» mantiene le indicazioni già date. Il campo
libero vale per qualsiasi tipo di progetto: stile, strumenti, sorgenti e cambi
di direzione. Le scelte del pannello appartengono all'utente e un aggiornamento
del piano del coordinatore non le sovrascrive. In chat il coordinatore chiede
soltanto le scelte decisive ancora mancanti; non chiede di nuovo quelle esplicite.

Salvare aggiorna memoria e contratto dei prossimi incarichi e invalida le vecchie
approvazioni; non cambia retroattivamente un worker già avviato. Per cambiare
subito usa **Attività → Interrompi questa fase**, poi chiedi in chat di ripianificare.
I file precedenti restano disponibili. Non è prevista la modifica in diretta di
un prompt mentre una singola generazione è già in corso.

## Generazione nativa Codex

Codex CLI è fissata alla **0.162.1**. Il worker usa il protocollo ufficiale
`codex app-server` su stdio, senza aprire porte: `exec --json` di questa versione
non pubblica gli eventi `imageGeneration`. Il bridge osserva avvio/conclusione
reali e trasferisce soltanto il PNG indicato da `savedPath` all'interno di
`CODEX_HOME/generated_images`, mai i file di autenticazione. Con la scelta
«Grafica vettoriale modificabile» disabilita la feature `image_generation`.
Le altre modalità permettono il tool, senza imporne l'uso. La disponibilità
configurata è distinta da quella verificata con l'account, il modello e la quota.

Le copie sono in `generated_images/<sha256>.png`, senza conversioni: i byte e i
metadati incorporati restano intatti. `work/imagegen-<sha256>.json` registra tool,
evento, prompt esposto come `revisedPrompt`, trasparenza, dimensioni e hash.
Il produttore deve conservare anche prompt e riferimenti realmente usati in
`work/method.json` o file collegati. Il registro esperienza conserva i riferimenti
e gli hash dei rapporti nativi; non ricostruisce prompt storici sconosciuti.
Il trasferimento controlla struttura/chunk/CRC del PNG, non la qualità visiva o
l'autenticità crittografica C2PA. Un PNG non è un sorgente a livelli o vettoriale:
layout, testo e asset vanno consegnati distintamente con i limiti reali.

La CI esegue il binario Codex fissato contro un servizio HTTP locale, con credenziali
fittizie e rete esterna disabilitata: verifica eventi immagini, copia PNG,
provenienza, esecuzione di un comando e assenza del tool nella modalità vettoriale.
Il protocollo app-server è marcato experimental dal fornitore: la versione resta
fissata e gli aggiornamenti richiedono il superamento di questo contratto.

## Stop della chat, chiusura e risorse

Lo **Stop della chat** ora propaga la cancellazione asyncio al worker sincrono:
annullare soltanto il Future non ferma il thread Python che sta aspettando Docker.
Ogni delega ha un segnale isolato; l'arresto usa il suo nome di job e le label di
installazione/workspace. La cancellazione di un incarico ancora in coda impedisce
l'avvio del suo container e non arresta il lavoro che occupa la squadra. Chiudere
la pagina con la politica predefinita `continue` non invia questo segnale.

Il pannello distingue avvio Codex, incarico accettato, strumento nativo attivo e
pulizia del container. Un avvio senza conferma ha un limite separato di 60 secondi;
questo limite non si applica a una generazione accettata. Restano il budget di fase
(25 minuti), il salvataggio progressivo e il budget di silenzio opzionale.

`worker_exit_at`, `cleanup_started_at`, `cleanup_finished_at` e
`resources_reclaimed` distinguono uscita del processo e rimozione Docker. La UI
scrive «Container rimosso» soltanto dopo la conferma di `docker rm`. Se la rimozione
fallisce, lo segnala e non ammette un altro worker. Un errore nella sola telemetria
non deve impedire rimozione o rilascio del lock. Le versioni precedenti non
espongono queste conferme: il riavvio del Gateway esegue già la pulizia degli
orfani limitata all'installazione, conservando i file nel volume.

Per i soli file ausiliari `dependency` e `report`, un controllo di riapertura
`not_run` con evidenza ma lista dei limiti vuota viene riportato come limitazione e
warning dal runtime, senza scartare l'intero incarico. Resta `not_run`: non diventa
un controllo riuscito. Sorgenti, archivi, export e riaperture fallite mantengono i
controlli rigorosi già previsti.
