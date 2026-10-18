# Richiesta, risultato ed evidenze: contratto comune ai 13 strumenti

Un incarico terminato non prova che il prodotto soddisfi la richiesta. Nella regressione osservata il coordinatore aveva modificato il contenuto richiesto, il rapporto valutava la sua interpretazione e la revisione, eseguita nello stesso step del montaggio, nascondeva il prodotto originale. Non era un problema del codec o di uno specifico strumento.

## Memoria della richiesta

Il Gateway conserva una copia dei messaggi umani effettivamente inviati nella configurazione del run. Non modifica i messaggi, le autorizzazioni o la politica di esecuzione in background. La configurazione non può sostituire questi dati con una copia fornita dal client. I sottoagenti ereditano l’input reale e non possono promuovere i propri incarichi sintetici a nuove istruzioni dell’utente. Nel lead vengono conservati anche i messaggi originali già presenti nella conversazione.

`acceptance.user_requests` conserva la prima richiesta e fino a otto chiarimenti recenti. È separata dal `brief` del coordinatore: una sua riformulazione non diventa automaticamente una modifica autorizzata del contenuto. Se un riferimento manca, va dichiarato o richiesto; non sostituito silenziosamente con qualcosa dello stesso genere, formato o categoria.

## Criteri osservabili per qualsiasi prodotto

`studio_plan(criteria_json=...)` registra fino a 20 requisiti specifici, oltre a `request_fidelity`, aggiunto dal runtime e non indebolibile dal coordinatore. Non ci sono criteri speciali legati a una canzone, un documento, una CLI o un numero minimo di specialisti.

Ogni requisito include `id`, `requirement`, `method`, `critical` e gli eventuali `reference_paths` della conversazione. Il metodo definisce cosa deve essere osservato:

| Metodo | Cosa verifica |
| --- | --- |
| `content` | Significato e corrispondenza alla richiesta originale |
| `reference` | Confronto con un riferimento effettivamente disponibile |
| `functional` | Comportamento, calcoli o operazioni richieste |
| `structural` | Struttura del progetto e parti modificabili |
| `visual` | Immagini effettivamente osservate |
| `listening` | Ascolto effettivo |
| `technical` | Formato, decodifica e presenza di dati |

Un controllo tecnico non approva automaticamente il contenuto. Cambiare il nome del metodo per superare un requisito non è ammesso. Gli stati sono `passed`, `failed`, `not_run`: mancanza di un’osservazione non equivale a successo. I criteri aggiuntivi non essenziali possono essere dichiarati `critical:false`; quelli obbligatori ereditano la criticità dal contratto.

## Revisione legata a richiesta, prodotto e riferimenti

Il rapporto `quality-review.json` usa `requirement_id` per collegare ogni osservazione al requisito. Requisiti non coperti restano aperti. La revisione viene legata a:

- hash del contratto, che comprende la richiesta effettiva e i suoi criteri;
- SHA-256 del prodotto esaminato;
- SHA-256 dei riferimenti locali letti e dichiarati negli input del revisore.

Una nuova richiesta non eredita una vecchia approvazione. Un riferimento cambiato non eredita il vecchio confronto. Una revisione negativa più recente non viene annullata da un precedente giudizio positivo sullo stesso file.

Le capacità di osservazione sono esplicite per il collegamento del modello, senza aggiungere configurazioni per i singoli specialisti. Attualmente Codex e Antigravity nei worker hanno strumenti visivi; DeepSeek nel trasporto corrente è testuale. Nessun trasporto attuale integra un percorso di ascolto: generare un WAV, leggerne i metadati o misurarne il segnale non viene presentato come ascolto. Un confronto quantitativo pertinente può soddisfare un requisito di riferimento, dichiarandolo come confronto quantitativo.

Questa politica verifica copertura, provenienza, coerenza del metodo e condizioni tecniche. Non è un giudice semantico infallibile: la correttezza delle osservazioni creative resta dipendente dal modello e dagli strumenti effettivamente usati. La copertura delle capacità non dimostra da sola che un’osservazione sia stata eseguita. Il software non promette qualità artistica universale.

## Risultato sempre raggiungibile

Prodotto selezionato, sorgenti e rapporti sono oggetti distinti. Una revisione può usare lo stesso `step_id` della produzione senza sostituirla. Il runtime mantiene i cinque incarichi recenti e l’incarico proprietario del prodotto selezionato; quest’ultimo resta anche oltre la normale finestra della cronologia. Il catalogo del coordinatore e il pannello danno priorità al prodotto e ai suoi sorgenti.

Il controllo “Vedi risultato” usa `product_path` anche se un inventario temporaneo contiene solo rapporti. Funziona per media, documenti e progetti: anteprima per i formati supportati, collegamento al file e istruzioni per gli altri. Mostra inoltre la richiesta originale e i requisiti ancora aperti. Nessuna sequenza creativa rigida viene imposta.

## Collaudo

- Contratto comune esercitato con tutti i 13 ID del catalogo, usando fixture dichiarate di orchestrazione, non una produzione artistica.
- Produzione e revisione nello stesso step; documento e sorgenti ancora presenti dopo 24 revisioni e potatura della cronologia.
- Richiesta originale preservata dopo riformulazione del coordinatore e compattazione del contesto.
- Input reale del Gateway distinto dai messaggi sintetici dei sottoagenti.
- Rifiuto di approvazione basata soltanto sull’header, requisiti omessi, metodo sbagliato, riferimento mancante o osservazione non disponibile.
- Hash di prodotto, richiesta e riferimenti; una revisione negativa recente prevale sulla precedente positiva.
- Browser React/Tailwind desktop e mobile con inventario composto soltanto da un rapporto, prodotto multimediale ancora riproducibile, documento finale scaricabile e requisiti visibili.
- Riproduzione locale del difetto con i metadati e i file della conversazione segnalata: prima prodotto assente dall’inventario, dopo prodotto selezionato e sorgenti mantenuti. Nessuna nuova generazione o modifica della conversazione di produzione.

La CI mantiene i collaudi delle CLI native e l’avvio completo del Compose. Il Compose candidato viene pubblicato soltanto dopo i controlli, per essere provato prima del merge.
