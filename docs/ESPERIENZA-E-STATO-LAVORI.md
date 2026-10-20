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

Le osservazioni sono **fonti**, non istruzioni da copiare nelle skills. Il coordinatore
usa `studio_lessons` per proporre solo singole lezioni che meritano di essere conservate:
condizioni d’uso, procedura generale, verifiche e limiti. Le fonti prive di una lezione
utile possono essere valutate senza generalizzarle; restano nell’archivio. Non c’è
l’obbligo di imparare tutta l’esperienza né di svuotare una coda prima della consegna.

## Accettazione delle singole lezioni

Apri **Dettagli progetto → Lezioni**. Ogni nuova lezione è una proposta inattiva:
solo **Accetta questa lezione** ne autorizza il riutilizzo. Il coordinatore può
proporre ma non accettare. La scelta riguarda l’esatta versione della lezione;
un’altra formulazione richiede una nuova accettazione. **Rimuovi dalle skills**
revoca il riutilizzo successivo senza cancellare fonti e storia. Nessuna accettazione
massiva o riutilizzo automatico delle vecchie osservazioni.

La compilazione seleziona al massimo sei lezioni accettate, entro un budget di testo.
La pertinenza usa strumenti/versioni o sovrapposizione di termini per principi generali;
non è una ricerca semantica. I fatti e i file del progetto di origine non vengono
iniettati nelle nuove skills. Le fonti rimangono referenziate separatamente e distinguono
preferenze dell’utente da verifiche positive e difetti. Le condizioni e i limiti
restano da controllare nel nuovo contesto. La validazione blocca percorsi, identificatori
e credenziali, ma non può certificare automaticamente la bontà della generalizzazione:
la lettura e l’accettazione della singola proposta restano necessarie.

**Squadra** mostra quante lezioni sono incluse nelle skills. L’accettazione o la revoca
si applica alla compilazione successiva, senza riscrivere incarichi già avviati.
Per le vecchie chat, **Fonti, preferenze e archivio → Recupera esperienza di questa chat**
raccoglie revisioni utilizzabili senza duplicarle. Non accetta lezioni, non importa
tutte le conversazioni e non ricostruisce versioni CLI storiche ignote.

L'archivio non sostituisce la memoria personale nella pagina Settings/Memory e non
attiva l'addestramento del modello o la riscrittura automatica delle skills Git.
Per non perdere l'esperienza nei deploy conserva e includi nei backup l'intero
volume `deerflow-data`, insieme alle cartelle dei progetti che contengono i file
originali. L'export JSON conserva osservazioni e lezioni con le relative accettazioni; non è un backup dei
prodotti né offre importazione automatica di procedure considerate affidabili.

## Conservare un metodo preferito

In **Lezioni → Fonti, preferenze e archivio**, scegli la lavorazione e descrivi cosa vuoi riutilizzare, poi premi
**Conserva questo metodo**. Si conservano la tua valutazione, il contesto dichiarato
del produttore, modello, strumenti e hash dei file. La preferenza è separata dagli
esiti delle verifiche e non porta il progetto a ready. Può riguardare un campione
riuscito anche se la consegna completa deve ancora finire.

Il software non deduce da un'immagine il processo che l'ha generata: i passaggi e
le capacità non registrati restano sconosciuti. I file restano nei progetti di
origine e vanno inclusi nel backup del volume. Una preferenza può essere fonte di una proposta di lezione, da accettare singolarmente; non garantisce lo stesso risultato né
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

Apri **Intervieni** accanto alla chat. Puoi scegliere immagini generate,
grafica vettoriale modificabile, tecnica mista o lasciare la scelta alla squadra,
quando la scelta è pertinente. «Come indicato nel brief o in chat» mantiene le
indicazioni già date. Il campo libero vale per qualsiasi tipo di progetto: stile,
strumenti, sorgenti e cambi di direzione. Le scelte del pannello appartengono
all'utente e un aggiornamento del piano del coordinatore non le sovrascrive.
In chat il coordinatore chiede soltanto le scelte decisive ancora mancanti.

Con **Applica e riprendi** il pannello arresta e attende la chiusura dei lavori
prima di salvare le indicazioni e riavviare il coordinatore. Le nuove scelte
aggiornano memoria e contratto dei prossimi incarichi e invalidano le vecchie
approvazioni; non modificano retroattivamente i file già salvati. I file precedenti
restano disponibili. Non è prevista la modifica in diretta di un prompt mentre
una singola generazione è già in corso.

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

## Console e interventi durante il lavoro

Accanto alla chat: identità del progetto, stato attuale, avanzamento sintetico e azioni
**Vedi anteprima / Apri consegna**, **Intervieni**, **Metti in pausa**. I dettagli si
aprono in una finestra con sezioni **Stato, Risultato, Squadra, Consegne, Attività,
Lezioni**. Intestazione e azioni restano raggiungibili anche sul telefono; solo il
contenuto centrale scorre. Modello, risorse, tempi e cronologia sono espandibili.

**Applica e riprendi** chiude prima il cancello delle nuove deleghe, arresta la
conversazione, attende l’esito e la rimozione delle sandbox attive, salva le nuove
indicazioni e invia un nuovo messaggio al coordinatore. Se la chiusura non è
confermata il progetto resta in pausa: nessun nuovo incarico viene avviato dal pannello.
I file salvati restano disponibili; lo stato in memoria di un processo terminato
non è recuperabile. La pausa manuale sopravvive alla ripianificazione del coordinatore.

Stile estetico, tecnica e modificabilità sono decisioni distinte. Le domande decisive
registrate non possono essere cancellate nello stesso turno utente; la produzione
attende una nuova risposta reale. Il sistema non può riconoscere automaticamente
ogni scelta omessa dal coordinatore: prompt e scheda del risultato devono chiarirle.

## Versioni del prodotto e verifiche

**Consegne** mette davanti le versioni del prodotto completo, numerate una sola volta.
I numeri non cambiano quando vengono aggiunte verifiche o ridotta la cronologia degli
incarichi. Una versione può essere in lavorazione, incompleta o selezionata: il numero
non certifica che sia pronta. **Risultato** mostra il numero della versione visualizzata
e indica se la squadra ne sta preparando un’altra. Anteprima e sorgenti dello stesso
riquadro restano associati alla medesima consegna.

Campioni, contributi e rapporti sono raccolti separatamente. Ogni verifica disponibile
indica il risultato controllato; se riguarda una versione precedente o un brief cambiato
non è presentata come approvazione della nuova versione. La relazione deriva dal file
indicato nel rapporto, non dal titolo dell’incarico o dalla parola «revisione».
Per le lavorazioni storiche non più presenti non viene inventata una corrispondenza.

Un requisito può avere più controlli: se almeno uno fallisce, il riepilogo resta
**Da correggere**. Esiti favorevoli parziali non nascondono i difetti e `not_run`
non diventa approvazione. La stessa sintesi aggregata è visibile al coordinatore.
I campioni devono essere scelti rispetto ai rischi e alla varietà del progetto:
un miglioramento locale non prova che l’intero prodotto soddisfi il brief.

## Apprendere l’uso migliore delle CLI senza accumulare rumore

Anche una sandbox può proporre una singola lezione: parametro utile, sequenza di
comandi, errore risolto, gestione di risorse o compatibilità dei sorgenti. Il registro
facoltativo `work/tool-lessons.json` conserva al massimo tre proposte con file di prova
e versioni reali; può essere recuperato anche da una lavorazione parziale. Non copia
la sessione intera e non considera ogni comando riuscito una buona pratica. Per i
vecchi lavori il coordinatore può ispezionare il procedimento già registrato nelle
fonti; ciò che non è stato registrato non viene inventato.

Le proposte sono ordinate per significatività, distinguendo miglioramenti rilevanti,
perfezionamenti minori e impatto da valutare. Le prime tre sono visibili; le altre e
le lezioni già accettate sono espandibili. Un beneficio piccolo ma osservato precede
un grande beneficio soltanto ipotizzato. L’impatto viene motivato, non ricavato dal
numero di comandi o di file. Le misure richiedono due stati reali del supervisore,
con tempi e hash registrati; senza misure si parla di osservazione o ipotesi, senza
percentuali inventate. Input comparabili e qualità dell’output rimangono da verificare.

Anche queste proposte restano inattive fino all’accettazione individuale. Nelle skills
entrano condizioni, procedura, verifiche e limiti; tempi e fatti del vecchio progetto
restano nell’archivio delle fonti, non diventano promesse per il progetto successivo.
