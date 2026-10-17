# Consegne complete e qualità verificabile

La precedente integrazione confondeva tre proprietà: esecuzione terminata, file tecnicamente validi e qualità adeguata al brief. Il risultato poteva essere dichiarato pronto con una revisione solo numerica, sorgenti incompleti e molte versioni mescolate nel pannello.

## Cause riprodotte e correzioni

- **FilmCraft 0.7.2:** i riferimenti relativi ai media vengono risolti dalla working directory. Aprire il progetto dalla cartella estratta funzionava; aprirlo da un’altra cartella mostrava media mancanti. La timeline non era vuota nel file: mancava la risoluzione dei media. Il nuovo pacchetto include un preparatore offline che crea una copia `.locale.fcproj` con percorsi locali, lasciando intatto l’originale. Alternativa nella GUI: File > Link Media. La versione GUI/web dell’utente non è stata collaudata; la compatibilità CLI non viene presentata come compatibilità universale.
- **Dipendenze dei colleghi:** il pacchetto reale includeva progetti EffectCraft che richiamavano texture assenti. La presenza di un altro ZIP nella stessa consegna non ripara un progetto sciolto. Il controllo ora segue i riferimenti effettivi, anche negli archivi annidati.
- **Controllo qualità:** DeepSeek nel trasporto attuale riceve soltanto testo. Creare PNG o misurare luminosità/RMS non significa vedere o ascoltare il risultato. Il runtime impedisce di registrare come superata una valutazione sensoriale con quel trasporto.
- **Selezione degli strumenti:** tutte le 13 skill hanno criteri specifici della disciplina, caricati automaticamente nel worker. Le fixture minime verificano le CLI, non sono modelli estetici. Il coordinatore sceglie le competenze necessarie; non c’è un numero minimo di specialisti.
- **Versioni:** il pannello raggruppa prodotto, sorgenti e istruzioni per consegna, distinguendo quella selezionata dalle prove precedenti. Non mostra più un unico elenco indistinto di MP4, texture e ZIP.
- **Brief:** la memoria conserva fino a 4000 caratteri invece di troncare la specifica allo stesso limite di 280 caratteri delle notifiche.

## Controlli effettivi

`studio/source_packages.py` raccoglie i riferimenti esatti di FilmCraft, EffectCraft e SoundCraft. Non cerca sostituti per nome. Gestisce ZIP con limiti di dimensione/numero di file, rifiuta percorsi esterni, link, duplicati e file mancanti. I progetti vuoti non passano. I sorgenti vengono estratti altrove; le CLI fissate nel catalogo li riaprono. Per FilmCraft vengono controllati media online e timeline, poi renderizzati tre fotogrammi da una working directory estranea al pacchetto.

Per una consegna video FilmCraft il runtime confronta durata, dimensioni e tre campioni di luminanza del render dei sorgenti con il video dichiarato (tolleranza alla compressione). Questo intercetta sorgenti di una versione diversa o un progetto che non produce il video consegnato. Non dimostra uguaglianza di ogni frame, qualità estetica o equivalenza sonora. La verifica media già esistente controlla anche i flussi richiesti e audio non silenzioso.

Il runtime scrive `delivery-manifest.json` con identità della consegna, SHA-256 dei file, ruoli, istruzioni, copertura e problemi. `technical_status=needs_revision` lascia i risultati recuperabili, ma impedisce `status=ready`. I formati delle altre applicazioni richiedono le prove specifiche della skill: CRC e inventario ZIP non certificano da soli la struttura di un DOCX, PSD, DXF o altro documento.

`purpose=review` esamina un prodotto esistente in una delega separata. Il rapporto `quality-review.json` deve citare criteri del brief, metodo, stato ed evidenze. Il runtime calcola l’hash del prodotto; `ready` richiede collaudo tecnico e revisione superati per gli stessi byte. File o sorgenti cambiati dopo il collaudo non ereditano la validazione precedente. I contenuti visivi richiedono un criterio visivo, gli audio un ascolto, e un progetto che richiede audio non può essere chiuso con sole misure tecniche.

Quando la valutazione automatica non è disponibile, il proprietario della chat può guardare/ascoltare il risultato e scegliere **Ho verificato: accetta questa versione** nell’anteprima. È facoltativo e non avvia un altro job AI. Il server controlla identità della consegna, permesso di scrittura sulla chat, sorgenti e hash; una consegna incompleta non può essere accettata. L’interfaccia distingue questa scelta dalla revisione dello specialista.

La revisione creativa resta una valutazione del modello/specialista, non una garanzia oggettiva. La sua accuratezza dipende dalla capacità di osservare il materiale e dalla qualità del modello. Se manca visione/ascolto, la versione resta disponibile e da valutare: nessun cambio di provider automatico e nessuna rigenerazione alla cieca. Nel pannello il lavoro terminato non viene etichettato come “Verificata”.

## Confezionamento riproducibile

Nel worker:

```bash
python3 /opt/studio/source_packages.py pack /mnt/user-data/outputs/filmcraft/JOB/montaggio.fcproj /mnt/user-data/outputs/filmcraft/JOB/Sorgenti.zip
python3 /opt/studio/source_packages.py verify /mnt/user-data/outputs/filmcraft/JOB/Sorgenti.zip --native
```

Il pacchetto contiene progetto, media, `CONTENUTO.json` con nomi/hash e istruzioni. L’utente estrae tutto, esegue `PREPARA_SORGENTI.py` con Python 3 e apre il `.locale.fcproj` nella app desktop compatibile. Se sposta la cartella, ripete la preparazione. La preparazione non installa software e non usa la rete. Per un montaggio composto da più discipline vanno consegnati anche i pacchetti completi degli specialisti pertinenti.

Limiti operativi del verificatore: 512 MiB estratti, 12000 elementi, al massimo due livelli di archivi annidati. Per progetti più grandi dividere i pacchetti e conservare riferimenti espliciti. Non esegue script forniti dal modello: il preparatore deve corrispondere al modulo fidato installato. Non certifica automaticamente font/plugin esterni, rendering di tutti i fotogrammi, ascolto, GUI o applicazioni web diverse.

## Prove

- Unit test: sorgenti mancanti, progetti vuoti, riferimenti assoluti, archivi annidati incompleti, traversal, preparazione dopo due spostamenti, dichiarazioni di riapertura false, guardia DeepSeek e revisione legata ai byte esatti.
- Browser React/Tailwind reale, desktop e mobile: consegna selezionata distinta dalle prove, sorgenti abbinati, istruzioni, stato incompleto, anteprima, ripresa e isolamento fra chat.
- CI sandbox: tutti i 13 workflow nativi preesistenti, più scambio PhotoCraft/EffectCraft/SoundCraft/FilmCraft, confezionamento e riapertura in altro percorso. La fixture tecnica rimane `review`: non viene promossa come valutazione artistica.
- Diagnosi privata: archivio reale respinto per texture mancanti; montaggio ricostruito con i media originali e riaperto tramite FilmCraft. Nessun file privato è pubblicato nel repository e nessuna nuova generazione artistica è implicita in queste prove.

## Installazione

Usare il `compose.hostinger.yaml` della release candidata prodotta dalla CI della PR, dopo tutti i controlli verdi, **prima del merge**. Il template interno non è il file da installare. Al merge la pipeline riusa le stesse immagini se l’albero Git è identico; non occorre attendere una seconda build per provare.
