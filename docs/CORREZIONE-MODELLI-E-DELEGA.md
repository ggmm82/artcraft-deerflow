# Correzione dei modelli e della delega dopo il deploy

Il collaudo amministratore sull'istanza Hostinger ha riprodotto due problemi che le prove precedenti non avevano coperto:

- Il pannello accettava `GPT-6.1 Sol` come identificatore del modello. Il catalogo della CLI distingue etichette e ID; quello corretto è `gpt-6.1-sol`. Anche il vecchio default `gpt-5.4` non compare più nel catalogo della CLI 0.162.1 verificato. La richiesta minima al coordinatore Codex con `gpt-6.1-sol` è riuscita sul VPS.
- Il selettore nativo della chat consentiva di usare un profilo DeepSeek aggiunto al catalogo DeerFlow, mentre gli specialisti ereditavano ancora Codex dalla squadra. I messaggi tecnici delle deleghe fallite confermano `engine: codex`: il test non stava provando worker DeepSeek. Con DeepSeek configurato nel pannello comune, WordCraft ha prodotto DOCX e PDF, scaricati e verificati indipendentemente: testo esatto e PDF di una pagina.

La correzione legge i modelli Codex dal protocollo ufficiale `app-server model/list`, inclusi paginazione, etichette e modello consigliato. Il salvataggio usa soltanto gli ID restituiti e rifiuta valori estranei senza cambiare la squadra. La chat espone soltanto il profilo Squadra ArtCraft e normalizza le preferenze precedenti sul profilo comune; gli altri cataloghi persistenti sono conservati. La normalizzazione conserva input, ragionamento e opzioni del run e non aggira l'autenticazione.

Sono stati corretti anche gli errori diagnostici: il corpo HTTP Codex viene letto prima di chiudere lo stream; i worker usano l'output JSON della CLI e ricevono il prompt via stdin. Gli errori strutturati vengono estratti senza sostituirli con la coda del contesto. Il bearer è oscurato nei messaggi HTTP.

Le prove HTTP sul VPS usano conversazioni di collaudo separate. Le prove che inizialmente usavano un limite di ricorsione 30 sono state fermate dal limite del banco di prova, non da un difetto del prodotto: il collaudo completo usa il valore 1000 del frontend reale. Questo limite non viene attribuito ai provider.

La chiave DeepSeek già fornita per le prove è stata collegata nel pannello comune; nessuna chiave viene copiata nei rapporti o nel repository. La scelta Codex originaria viene mantenuta correggendo l'ID del modello. I controlli automatici includono stream HTTP realmente chiusi, chiamate agli strumenti, catalogo CLI paginato, ID/etichette diversi, selezioni legacy della chat e diagnostica dei worker. La CI verifica anche `model/list` con il binario nativo, senza generazioni.


Il collaudo illustrativo ha trovato anche un limite reale del worker DeepSeek: la produzione veniva congelata al turno 28, pur avendo tempo residuo e un batch di costruzione quasi pronto. La nuova soglia è 64 chiamate con avviso negli ultimi quattro turni; l’esecuzione dei batch preparati resta possibile fino alla chiamata finale riservata. `submit_handoff` è disponibile fin dall’inizio per chiudere appena il prodotto è pronto. I file interni sotto `work/` non possono sostituire gli output del brief. La skill VectorCraft specifica ora la via rapida SVG XML originale → import nativo → export SVG/PNG, evitando decine di operazioni MCP per costruire da zero un disegno semplice.

Le nuove prove automatiche coprono anche l’esecuzione di una produzione preparata durante la riserva finale e il rifiuto dei cataloghi interni come prodotti. Il caso illustrativo fallito sul vecchio runtime rimane tale e non viene contato come riuscito.


## Stato verificato del rilascio

Runtime `345840fa88153500158c2bde8e6a5041ddb682fc`: tutti i sei job CI e avvio completo verdi, sia nella [PR](https://github.com/ggmm82/artcraft-deerflow/actions/runs/38727278651) sia nella [pubblicazione](https://github.com/ggmm82/artcraft-deerflow/actions/runs/38727399776). Il Compose nel repository usa questi runtime. Il download anonimo dell’[asset versionato](https://github.com/ggmm82/artcraft-deerflow/releases/download/studio-345840fa88153500158c2bde8e6a5041ddb682fc/compose.hostinger.yaml) è stato confrontato con il file generato.

Sono passati 62 test Python: 57 locali e cinque contratti provider nell’immagine Gateway effettiva, compreso il retry limitato dopo 429. La CI comprende inoltre le verifiche native delle 13 app e il collaudo del protocollo Codex senza generazione.

Sul VPS sono state prodotte e scaricate una DOCX e una PDF con testo/pagina verificati indipendentemente. Il percorso rapido illustrativo ha completato VectorCraft → PhotoCraft con SVG, sorgente VectorCraft, PNG trasparente e PSD a tre livelli. Il controllo visivo ha rilevato un’ombra duplicata nel primo export PhotoCraft: una terza delega ha nascosto quel livello e riesportato i file. Il PNG finale è stato visto, il PSD riaperto e la trasparenza verificata: la sagoma trasparente/opaca corrisponde al render vettoriale; l’antialiasing di bordo varia leggermente dopo il compositing. È un disegno stilizzato 512×512; il PSD separa soggetto e sfondo, non le singole parti del corpo.

La configurazione live mantiene Codex con il corretto ID `gpt-6.1-sol`. DeepSeek è collegato nel pannello comune. Il profilo DeepSeek separato della chat è stato disattivato, conservando la configurazione persistente: il selettore mostra solo Squadra ArtCraft. Le conversazioni dell’utente non sono state modificate.

Il coordinatore Codex risponde con l’ID corretto. La produzione del worker Codex resta da verificare **dopo l’installazione di questo rilascio**: il vecchio worker nascondeva la causa nel contesto troncato ed è stato osservato anche HTTP 429. Non viene dichiarata riuscita senza output finali. L’aggiornamento Docker sul VPS è eseguito dall’utente.


## Collaudo successivo al deploy: percorsi CLI WordCraft

Il nuovo endpoint del catalogo Codex risponde correttamente sul VPS. La prima delega Codex ha superato l'avvio del modello, ma non ha prodotto documenti: il manifest registra `python: command not found` e `/opt/artcraft/bin/wordcraft-cli: No such file or directory`. La skill WordCraft indicava erroneamente quella cartella; l'installer reale crea i link in `/usr/local/bin` e il runtime installa `python3`.

La skill ora usa i percorsi reali. Il prompt del worker e la procedura comune specificano `python3` e `/usr/local/bin` per tutti gli specialisti. La validazione del catalogo rifiuta il vecchio percorso nelle skill e nelle ricette. Quando un manifest non contiene output validi, il runtime continua a rifiutare la consegna, includendo specialista, cartella e cause dei controlli falliti anziché soltanto l'errore di schema. La diagnostica non segue manifest collegati fuori dalla cartella assegnata.

La verifica della produzione Codex con i percorsi corretti è in corso; questo aggiornamento non viene contato come collaudo riuscito finché i documenti non sono scaricati e controllati.
