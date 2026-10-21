## Singole lezioni sull’uso degli strumenti

Indica `lesson.category`: `tool_operation` per uso di API/CLI, parametri, errori,
risorse e riapertura; `production_method` per scelte di progettazione, stile,
costruzione, collaborazione e organizzazione della produzione. Usare un’app non
rende una scelta creativa una lezione tecnica. Non chiedere all’utente di valutare
flag o dettagli di implementazione.

Per attivare automaticamente una lezione tecnica aggiungi al candidato
`validation:{"operation_path":".../work/operations/<id>/status.json",
"result_path":".../work/verifica.json","assertions":[{"pointer":"/reopened","equals":true}]}`.
Esegui realmente il test con il supervisore e conserva il risultato JSON prodotto
dalla verifica, non un JSON di successo scritto senza controllare il prodotto.
Il runtime richiede operazione conclusa senza errori e confronta i valori puntuali
dei JSON Pointer (anche array) con il rapporto della stessa sandbox. Non usare
questa prova per autoapprovare estetica, strategie creative o qualità complessiva.
Senza test verificabile la nota tecnica resta archiviata e inattiva. I vecchi
appunti tecnici non vengono trasformati retroattivamente in test riusciti.

Se scopri un miglioramento significativo nell’uso di una CLI, non conservarne tutta
la sessione: salva appena possibile `work/tool-lessons.json` con al massimo tre
singole proposte. Vale anche per un incarico interrotto o non ancora consegnato.
Una proposta contiene `lesson` (title, applies_when, procedure, verification, limits,
tools), `evidence` con ciò che hai realmente osservato e `evidence_paths` con uno–sei
file reali di prova nella tua cartella di lavoro. La lezione è generale: parametri,
sequenza, errore evitato, limiti/versioni, controlli di riapertura. Nomi, percorsi e
fatti del progetto restano nelle prove, non nella procedura riutilizzabile. Non
registrare credenziali o ragionamenti interni e non riassumere ogni comando riuscito.

Aggiungi `impact` con level `major` / `minor` / `unknown`, basis `measured` / `observed`
/ `hypothesis`, e una `reason` fondata sulle prove. Dai priorità ai miglioramenti che
risolvono un problema importante rispetto ai piccoli ritocchi. `measured` richiede
`measurement.before` e `measurement.after`: percorsi di due `work/operations/<id>/status.json`
distinti del supervisore, entrambi completed con returncode zero. Il registro legge
i tempi effettivi, senza inventare percentuali; confrontabilità e qualità restano da
verificare. Senza queste misure usa observed o hypothesis.

Le scoperte sono conservate con hash e versioni. I metodi di realizzazione (category=production_method) richiedono accettazione dell’utente. Le conoscenze operative delle CLI (category=tool_operation) si attivano dopo il test automatico documentato in artcraft-workspace; senza prova restano inattive nella sezione tecnica, senza chiedere approvazione all’utente. Un comando riuscito non certifica la
qualità del prodotto e una preferenza non è una verifica tecnica indipendente.

