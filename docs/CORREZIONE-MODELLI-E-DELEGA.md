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
