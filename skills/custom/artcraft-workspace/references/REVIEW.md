## Revisione della qualità senza riscrivere il prodotto

Quando `Scopo incarico: review` riguarda il prodotto conclusivo, valuta il file esistente rispetto al brief e ai criteri `references/QUALITY.md`. Usa immagini reali in un tool visivo, campioni delle transizioni e ascolto effettivo quando disponibili. Il collegamento DeepSeek corrente è testuale: non può attestare visione o ascolto. Non modificare il prodotto durante questa verifica; indica difetti e correzioni mirate. Non promuovere una bozza solo perché è decodificabile.

Consegna nella tua cartella `quality-review.json`, ruolo `report`, elencato in `output_files`; il prodotto esaminato deve essere in `source_files`. Se manca `handoff.json` o sono errati i suoi metadati, il runtime compila l’involucro dal rapporto valido, conserva l’originale in work/ e mantiene i controlli dichiarati falliti, senza alterare i giudizi. Il rapporto può indicare `source_files` e deve usare il `product_sha256` effettivamente osservato quando lo dichiara. La revisione non deve copiare o riesportare il prodotto per diventare una consegna valida. Esempio di struttura (non di valutazione da copiare):

```json
{
  "product_path": "/mnt/user-data/outputs/filmcraft/JOB/video.mp4",
  "criteria": [
    {"criterion": "Silhouette e articolazioni leggibili nel brief", "method": "visual", "status": "not_run", "evidence": "Sostituire con osservazioni sui frame reali e tool usato, oppure motivo della mancata visione"},
    {"criterion": "Coreografia e ritmo coerenti con la musica", "method": "listening", "status": "not_run", "evidence": "Sostituire con ascolto e confronto reali, oppure limite della modalità disponibile"}
  ]
}
```

Metodi: `visual`, `listening`, `technical`, `content`. Criteri pertinenti e specifici al prodotto, non una lista generica di complimenti. Stati: `passed`, `failed`, `not_run`. Il runtime lega la valutazione all’hash del prodotto: una modifica richiede revisione della nuova versione. Un prodotto visivo richiede almeno un criterio visivo, un prodotto audio almeno un criterio d’ascolto. Se non puoi valutare, consegna il rapporto e mantieni lo stato da valutare; non avviare rigenerazioni inutili. Non usare sole misure tecniche per approvare contenuto creativo.



## Contratto comune: contenuto richiesto, evidenze e riferimenti

Il runtime fornisce `acceptance` nell’incarico: messaggi originali dell’utente, modifiche successive e requisiti con ID. Il piano del coordinatore è una proposta operativa e non può cambiare da solo il contenuto richiesto. Rispetta i messaggi successivi dell’utente quando correggono i precedenti. Questa procedura è comune a tutti gli strumenti.

Prima di produrre in grande, scegli un campione rappresentativo e verifica il requisito più rischioso con gli input effettivi. Un file valido, dati presenti o segnale non silenzioso non dimostrano che contenuti, calcoli, forma, stile o riferimenti siano quelli richiesti. Se manca un riferimento indispensabile o una capacità reale, segnalalo e conserva i risultati; non sostituire il requisito con un’alternativa più facile senza l’utente.

Nella revisione `quality-review.json` ogni criterio deve indicare `requirement_id` copiato da acceptance, `criterion`, `method`, `status`, `evidence` e facoltativamente `critical:false` per controlli aggiuntivi non essenziali. Includi sempre `request_fidelity`: confronta il prodotto con la richiesta originale e le sue modifiche, non con il riassunto del produttore. I criteri non coperti restano non verificati. La revisione è legata sia ai byte del prodotto sia al contratto: una richiesta cambiata non eredita l’approvazione precedente.

Esempio di voce (da adattare e osservare realmente):

```json
{"requirement_id":"request_fidelity","criterion":"Contenuto conforme ai messaggi dell’utente","method":"content","status":"not_run","evidence":"Sostituire con osservazioni reali sul contenuto o con il motivo della mancata verifica"}
```

Metodi comuni: `content` per significato/contenuto, `structural` per struttura modificabile, `functional` per comportamento/calcoli, `reference` per confronto con risorse effettive, `visual` per immagini osservate, `listening` per ascolto effettivo, `technical` per formato/decodifica. Usa il metodo previsto dal requisito, senza rinominare una misura tecnica come giudizio percettivo. Per `reference` devi avere letto i `reference_paths` in `source_files`; il runtime ne conserva gli hash. Se il collegamento non offre il metodo necessario, registra `not_run`. L’ascolto non è attualmente collegato nei trasporti supportati; DeepSeek non offre neppure visione. Un confronto numerico appropriato al requisito può essere descritto come tale, non come ascolto o visione inventati.

Le revisioni possono riusare lo stesso step_id della produzione: il software mantiene il prodotto selezionato, i sorgenti e le revisioni recenti come consegne distinte. Non rigenerare un risultato perché il suo rapporto è diventato il file più recente. Comunica “versione disponibile / requisiti da verificare” finché il contratto non è soddisfatto, senza dichiarare tutto concluso.


## Dalla revisione alla correzione

Le assunzioni del coordinatore non diventano automaticamente vincoli dell'utente. Prima di dichiarare un metodo incapace, confronta le richieste originali e le scelte delegate alla squadra. Descrivi cosa hai realmente provato, quale capacità manca e un'alternativa operativa pertinente. Un ritocco degli stessi elementi non dimostra che sia stato tentato un metodo differente; un titolo professionale non è una prova di competenza. Nella revisione giudica le evidenze indipendentemente dal giudizio suggerito nell'incarico. Non abbassare i criteri per autorizzare la produzione.

Una revisione non termina con una lista di difetti. In `quality-review.json` aggiungi `revision_actions`: fino a 12 oggetti con `requirement_id` del criterio, `action` concreta, `reason`, `priority` 1–3 e `strategy` tra `revise`, `change_method`, `verify`, `missing_dependency`. Se non sai proporre una correzione affidabile, dichiara il limite; non inventare che un filtro risolva un problema strutturale. Il runtime conserva anche i precedenti `targeted_corrections`.

Per una versione corretta leggi anche il precedente artefatto, includilo in `source_files` e indica `baseline_path`. Aggiungi `comparison`: lista di `requirement_id`, `status` tra `improved`, `unchanged`, `regressed`, `not_verified` ed `evidence` puntuale. Il runtime registra gli hash dei due file, rifiuta miglioramenti su byte identici e mantiene non verificato ciò che il collegamento non permette di osservare. Migliorato non significa necessariamente sufficiente: i criteri ancora falliti rimangono falliti.

