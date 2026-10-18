# Risorse e avanzamento dei lavori pesanti

La creazione del contenuto può essere breve mentre render, export o conversioni richiedono molto più tempo. Un heartbeat dimostra che il worker è raggiungibile, non che l'esportazione avanzi. Questa integrazione distingue stato del modello, processo nativo, campioni effettivi e uso della memoria.

## Un solo budget

In **La tua squadra → Risorse della squadra**, Automatico legge CPU e RAM del Docker host e calcola il limite comune: al massimo 4 CPU, lasciando mezzo core ai servizi, e al massimo 6 GiB RAM, entro metà della RAM totale e con una riserva di 2 GiB quando possibile. Sotto queste capacità si applica un minimo prudente. Se il daemon non risponde, il pannello dichiara il mancato rilevamento e usa un budget provvisorio di 1,5 CPU e 2 GiB.

È disponibile un budget manuale entro i limiti dell'host e della riserva. La configurazione persistente è una sola (`runtime.json` nel volume privato), applicata a tutti gli specialisti e a tutti i provider, senza cambiare modelli o credenziali. Il budget viene fissato all'avvio dell'incarico: un salvataggio non ridimensiona container già attivi. Non è un rilevamento della RAM libera istantanea: altri carichi sul VPS possono comunque causare pressione. Non è una prenotazione di memoria.

Il Gateway propaga quota CPU, limite RAM, tmpfs e numero di thread; nessun socket Docker viene passato ai worker. La concorrenza rimane un worker alla volta. Il pannello resta protetto dall'autenticazione amministrativa e dal controllo di origine.

## Supervisore comune agli strumenti

Per un comando costoso nella sandbox:

```bash
python3 /opt/studio/operations.py --key "export-v1" --label "Esportazione finale" --timeout 1200 -- programma argomenti
```

La chiave identifica quella versione del lavoro; non va cambiata per eludere un processo ancora attivo. Il supervisore mantiene stato e log privati in `work/operations`, usa un lock comune al worker e verifica l'identità Linux del processo. Anche se il supervisore viene ucciso, la presenza del processo precedente impedisce di avviarne un duplicato. Timeout e interruzioni gestibili terminano il gruppo dei processi, compresi i figli. Alla scadenza del worker il Gateway rimuove comunque l'intero container.

Non vengono adottati processi avviati esternamente, disaccoppiati con `nohup` o che creano una nuova sessione: le skills vietano queste scorciatoie per i lavori pesanti. Il software non può impedire a una CLI di terze parti di ignorare volontariamente il supervisore. La CLI ufficiale Blender rimane disponibile, ma gli script lunghi devono usare il medesimo supervisore.

## Blender: misurare prima di renderizzare

`blender-cli profile SCENA.blend --frame 1` misura un ritaglio rappresentativo con Cycles CPU. `render` lo esegue automaticamente, riusando il campione se progetto, frame, budget e codice sono invariati. La misura produce una stima indicativa del render finale, senza modificare il `.blend` o abbassarne la qualità. Comprende i costi di avvio e può sovrastimare o sottostimare molto una scena non uniforme. Il confronto con il budget residuo evita di avviare un render intero che il campione indica come troppo lungo: conserva il sorgente e richiede checkpoint, porzioni seriali o continuazione fedele al brief. Le altre modalità di rendering richiedono un collaudo separato.

La memoria di un piccolo campione non prova che l'intera immagine rientri in RAM. I limiti restano applicati e gli errori vanno riportati. Il limite di 25 minuti della singola delega non viene rimosso: progetti più lunghi continuano tramite file e checkpoint persistenti.

I parametri dei comandi e i log non vengono pubblicati nel pannello. Vengono mostrati soltanto nome dell'operazione, stato, durata, stima iniziale e campioni realmente riportati da Cycles, oltre a RAM del worker e limite assegnato. I campioni non sono una percentuale del progetto intero. Per le altre CLI restano disponibili stato, durata e risorse; non si inventano percentuali.

## Memoria e arresti forzati

Con cgroup v2, il worker legge `memory.current`, `memory.peak`, `memory.max`, `memory.events` e `cpu.stat`. Un incremento di `oom_kill` conferma che il kernel ha terminato un processo per memoria esaurita. Per l'arresto dell'intero worker il Gateway verifica anche `State.OOMKilled` prima di rimuoverlo. Il codice 137 da solo resta un arresto forzato con causa non determinata. Quando i contatori non sono disponibili, il pannello non li presenta come misure effettuate.

Un errore confermato di memoria suggerisce di correggere il budget o il metodo prima di ripetere. Gli output parziali restano disponibili e non sono promossi a consegne verificate. Non vengono rigenerati automaticamente i lavori già presenti nelle chat.

## Collaudi

- Processi reali: timeout con figli, recupero successivo, supervisore ucciso e rifiuto del duplicato anche con una chiave diversa.
- Separazione fra uscita 137 e OOM confermato; test CI in un container dedicato a 256 MiB con allocatore figlio e lettura dei contatori reali.
- Budget automatico/manuale, persistenza, riserva host e rifiuto di configurazioni eccessive senza sovrascrivere la precedente.
- Browser desktop/mobile: un solo pannello, salvataggio e riapertura, campioni e RAM visibili durante il lavoro.
- Blender reale: profilo campione, hash del sorgente invariato, render, riapertura, GLB e ZIP; regressioni native dei restanti strumenti e avvio completo del Compose.

Il tempo sul VPS dipende da hardware, scena e carichi presenti. Questi controlli eliminano attese e tentativi evitabili e rendono misurabile il lavoro; non promettono un tempo massimo di consegna o qualità artistica automatica.
