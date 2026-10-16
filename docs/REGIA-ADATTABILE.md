# Regia adattabile e stato visibile

La squadra sceglie fra i 13 strumenti in funzione del risultato. Lavora per versioni: una prova piccola e completa appena possibile, osservazione del prodotto, revisioni mirate e consegna finale con sorgenti. Il coordinatore può cambiare ordine, riassegnare un’attività, aggiungere un’integrazione o tornare a uno specialista usando ciò che gli altri hanno già prodotto.

Il VPS da 4 GB mantiene un solo worker fisico alla volta. La regia resta adattabile: questo limite di RAM non impone una catena obbligatoria né il completamento perfetto di ogni componente prima di vedere il prodotto assemblato.

## Dove guardare nella chat

Il pannello del progetto è **sopra la casella di scrittura**, fuori dalla cronologia che scorre, nelle chat normali e in quelle degli agenti. Su desktop e mobile mostra:

- chi sta lavorando e una frase sul lavoro concreto;
- il prossimo risultato utile, oppure il motivo della pausa e l’azione necessaria;
- **Vedi risultato**: riproduce un’anteprima disponibile, etichettando la bozza e distinguendo l’eventuale audio separato;
- **Squadra**: attività modificabili e loro stato;
- **File e sorgenti**: download dei file effettivamente presenti, compresi quelli recuperabili ma da verificare;
- **Attività**: tempi, heartbeat, file provvisori e dettagli operativi, su richiesta;
- **Riprendi lavoro**: invia una normale richiesta autenticata alla conversazione, conservando i risultati. Impedisce doppi invii immediati e segnala errori di invio; non cambia servizio o riavvia processi da solo.

Il polling prosegue anche negli intervalli fra due deleghe e dopo una riconnessione; il cambio conversazione nasconde immediatamente dati e anteprima precedenti. Non ci sono percentuali o stime di consegna inventate. Il countdown tecnico del singolo incarico è nei dettagli.

## Cosa è cambiato rispetto alla prima pipeline

`studio_plan` conserva un brief, un riepilogo corrente, il prossimo passo e le attività. Gli aggiornamenti fanno upsert per ID e preservano tentativi e file: non è necessario archiviare il progetto per aggiungere un’attività. `depends_on` suggerisce input disponibili; non è un blocco di esecuzione. I profili non forzano una squadra di quattro strumenti: tutto il catalogo resta utilizzabile. `animated_video` imposta invece requisiti del prodotto (video e audio, salvo richiesta esplicita di un video muto).

`studio_delegate` registra anche attività dirette, senza un piano formale o uno `step_id` obbligatorio. Lo scopo può essere lavoro, prova, revisione, integrazione o consegna. Una revisione riapre solo l’attività interessata e conserva le altre versioni utilizzabili. I limiti facoltativi — per esempio GUI non provata — restano dichiarati, senza obbligare a rifare un lavoro valido per trasformarli in passed.

Le risposte al coordinatore sono compatte: risultati, app e ruoli dei file, controlli pertinenti, limiti e percorsi. La cronologia completa resta nei file privati. Le istruzioni richiedono di affidare l’ispezione tecnica allo specialista, evitando lunghe letture di script e log nella chat. La riduzione di questi contenuti non equivale a una misura garantita dei token di una futura generazione.

## Recuperare il lavoro invece di ricominciare

Un processo può fermarsi per quota, turni o errore dopo aver creato file validi. Il runtime restituisce l’inventario dei risultati recuperabili senza dichiararli verificati. Un collega può ispezionarli, importarli e integrarli. Il lettore recupera anche file di incarichi precedenti alla modifica che avevano salvato soltanto la cartella del job, preservando i vecchi piani senza migrazioni distruttive.

Il contatore permanente di tre tentativi è rimosso. Errori di quota o autenticazione interrompono i retry automatici nello stesso turno utente; una nuova istruzione esplicita o un cambio della configurazione condivisa consente un nuovo tentativo. Due errori identici senza file prodotti fermano quella ripetizione e richiedono una strada diversa; le altre attività rimangono utilizzabili. Le revisioni creative con risultati possono proseguire. La cronologia operativa è limitata e conserva l’ultima versione utilizzabile; i prodotti su disco non vengono cancellati.

Il budget resta di 25 minuti per incarico. Salvataggio precoce, checkpoint, segmenti di render e nuove attività permettono progetti più lunghi. Un riavvio del Gateway marca il lavoro interrotto in pausa: conserva i file e richiede una nuova esecuzione del coordinatore. La semplice chiusura della pagina usa la prosecuzione in background già prevista.

## Accettazione del prodotto completo

Per audiovisivi il coordinatore dichiara i requisiti `audio`/`video`. Una delega finale con `purpose=delivery` controlla **nel worker** il file realmente esportato tramite ffprobe e misura il segnale audio tramite ffmpeg. Un MP4 muto o con audio silenzioso non può essere marcato come prodotto finale con musica. La verifica viene legata al percorso esatto del file, così che un altro export muto nello stesso job non erediti l’approvazione.

Solo un file esistente, prodotto da uno specialista e verificato per i requisiti pertinenti può essere indicato come `product_path` con stato `ready`. Sorgenti modificabili, risorse e limiti di riapertura rimangono nella consegna. Queste verifiche tecniche non dimostrano bellezza, coreografia o qualità musicale: la prima prova va osservata prima di investire nella produzione definitiva, e visione/ascolto non eseguiti vanno dichiarati.

## Evidenza sul caso segnalato

Nella conversazione segnalata l’audio era arrivato a tre processi interrotti, mentre il video e un master WAV di 20 secondi erano già disponibili. La dipendenza rigida impediva a FilmCraft di montarli. Successivamente sono comparsi anche errori di quota di Codex e Antigravity, conteggiati come tentativi creativi.

In ambiente di collaudo sono stati scaricati i due file con l’autorizzazione dell’utente, importati nelle due tracce di un progetto FilmCraft e riesportati: il video originale risultava privo di audio; il prodotto integrato contiene video e audio non silenzioso. Il controllo dimostra che il recupero era possibile; non dichiara risolta la qualità estetica del robot. I file e le credenziali dell’utente non vengono pubblicati nel repository e il collaudo non modifica la conversazione di produzione.

## Verifiche ripetibili

- Suite Python: aggiornamento delle attività, tutti i 13 ruoli e catalogo estendibile, riassegnazioni, revisioni oltre tre tentativi, pause di quota, ripresa esplicita, risultati precedenti e isolamento dei percorsi.
- Tool wrapper LangChain reali nell’immagine Gateway: memoria compatta, trasmissione dei requisiti al worker e protezione dai retry di quota nello stesso turno.
- Chromium con React e Tailwind effettivi, media di fixture riproducibili e layout chat/composer: pannello visibile durante lo scroll su desktop e mobile, anteprima riproducibile, bozza/definitivo, pausa, invio di ripresa con errore, recupero rete, ricaricamento e cambio chat.
- Iniezione verificata contro entrambe le pagine reali upstream: un solo pannello, fuori dal MessageList e sopra InputBox; il pulsante usa il normale submit autenticato.
- Pipeline con quattro CLI reali e interruzione simulata **dopo** il bounce SoundCraft: FilmCraft integra comunque il mix realmente prodotto e il prodotto finale supera i requisiti audio/video. La CI usa i limiti RAM/CPU del VPS e mantiene anche i workflow nativi dei 13 strumenti.

Il collaudo completo di una nuova generazione artistica con il modello dell’utente richiede il deploy candidato e quota disponibile. I test deterministici e il recupero dei file reali non vengono presentati come una nuova generazione LLM riuscita.
