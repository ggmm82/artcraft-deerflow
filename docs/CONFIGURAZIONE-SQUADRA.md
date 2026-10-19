# Un pannello per coordinatore e squadra

Apri **La tua squadra** nella barra laterale. Provider, account, modelli e ambiti si configurano qui; le skills non contengono copie delle impostazioni o delle chiavi.

1. Scegli **Applica a**: **Solo coordinatore**, **Solo squadra** oppure **Coordinatore e squadra · entrambi**.
2. Seleziona il servizio: **DeepSeek API**, **Codex con account OpenAI**, **Antigravity con account Google** oppure **OpenAI compatibile con URL e chiave API**.
3. Scegli il modello dall'elenco o lascia Automatico dove disponibile. Salva la configurazione.
4. Controlla il riepilogo: mostra distintamente il provider e modello attivi per coordinatore e squadra. Poi apri una chat con **Risolvi un problema**.

**Solo coordinatore** conserva la scelta della squadra, anche se prima il modello era condiviso. **Solo squadra** cambia tutti gli specialisti, inclusi i ruoli professionali compilati dinamicamente, conservando il coordinatore. **Entrambi** torna a un profilo condiviso. Le scelte restano dopo il riavvio; skills, preferenze e file dei progetti vengono conservati. I nuovi incarichi usano il profilo corrente, mentre quelli già avviati continuano con la configurazione iniziale.

I collegamenti agli account Codex e Antigravity e la chiave del servizio DeepSeek restano gestiti centralmente: cambiare account/chiave di uno di questi servizi riguarda chi utilizza quel collegamento. L'ambito seleziona quale provider e modello assegnare, senza duplicare la configurazione nei singoli specialisti.

## Endpoint OpenAI compatibile

Inserisci **URL base dell'API**, **chiave API** e **ID modello**. Esempi di forma dell'URL: `https://provider.example/v1` o `https://provider.example/api/v1`. Un URL senza percorso viene normalizzato a `/v1`; un URL che termina con `/chat/completions` o `/models` viene ricondotto al relativo URL base. HTTP è utilizzabile anche per servizi privati raggiungibili dall'installazione. Sono rifiutati credenziali nell'URL, query, frammenti e schemi diversi da HTTP/HTTPS. L'endpoint deve essere raggiungibile dai componenti che lo utilizzano.

Il servizio deve supportare **Chat Completions e function calling**. Al salvataggio una breve richiesta verifica che il modello esegua una chiamata di strumento; la prova può consumare credito del provider. Una risposta testuale generica non basta ad attivare un modello incapace di usare gli strumenti. Il controllo verifica il collegamento, non la qualità professionale di un lavoro.

La prova riconosce anche i provider che richiedono `max_completion_tokens` al posto di `max_tokens` e i modelli con ragionamento attivo (ad esempio Kimi K3 e K2.6) che rifiutano una `tool_choice` forzata su una funzione specifica o qualsiasi `tool_choice` esplicita: in caso di HTTP 400 la verifica riprova in sequenza con `max_completion_tokens`, con la richiesta di uno qualsiasi degli strumenti offerti e infine senza `tool_choice`. I parametri riusciti vengono conservati per i worker; non occorre configurarli in un altro punto.

**ID del modello** permette l'inserimento manuale, inclusi identificatori con maiuscole o nomi come `organizzazione/modello`. Non è obbligatorio che `/models` sia disponibile: con un ID esplicito viene provata direttamente l'API di completamento. Dopo aver inserito URL e chiave puoi usare **Aggiorna elenco modelli** prima di salvare, se il provider lo offre. Il caricamento dell’elenco non salva credenziali e non cambia i profili attivi. Scegliere un elemento dell’elenco prevale sull’eventuale ID manuale precedente.

Le credenziali vengono conservate nel volume privato `studio-state`, separate dalla configurazione dei modelli. Il catalogo pubblico e le risposte del pannello non restituiscono la chiave; il campo viene svuotato dopo il salvataggio e non usa localStorage. Per cambiare soltanto modello non occorre reinserirla. Se cambi URL devi inserire nuovamente la chiave, così quella precedente non viene inviata per errore a un altro endpoint.

Ogni collegamento personalizzato salvato ha un selettore privato stabile. Cambiare endpoint o chiave del solo coordinatore conserva il collegamento precedente della squadra. Il worker riceve in sola lettura il solo file delle credenziali selezionate, senza ricevere gli altri collegamenti. Le immagini e il Compose non contengono chiavi.

## Compatibilità e limiti

Le installazioni esistenti continuano con il profilo condiviso finché non viene scelta una separazione. Gli identificatori delle conversazioni restano validi e puntano al profilo del coordinatore; il catalogo dei modelli della chat continua a mostrare un solo ingresso di coordinamento, evitando un secondo punto di configurazione. Gli endpoint precedenti di collegamento DeepSeek e configurazione del coordinatore mantengono il comportamento condiviso per compatibilità; il nuovo selettore usa `PUT /studio/api/team` con `scope=coordinator|squad|both`.

I provider CLI mantengono accesso ufficiale, modelli disponibili e quote dei rispettivi account. Il nuovo trasporto usa Chat Completions, non l'API Responses; non aggiunge un client OAuth o un programma CLI per i provider personalizzati. La compatibilità richiede uno schema OpenAI effettivo: campi specifici DeepSeek come `thinking` non vengono inviati al servizio custom. La valutazione visiva del trasporto custom rimane non certificata e l'ascolto non viene simulato. Gli errori di autenticazione, quota e rete vengono mostrati senza riportare corpi di risposta che potrebbero contenere credenziali.
