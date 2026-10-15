# Una configurazione per tutta la squadra

Apri **La tua squadra** nella barra laterale. Al primo accesso la nuova chat porta automaticamente qui finché non è stato collegato un servizio.

1. Scegli **DeepSeek** e incolla la chiave API, oppure **Codex** e completa l’accesso ufficiale.
2. Lascia **Automatico** e premi **Salva e attiva la squadra**. Con DeepSeek vengono controllati chiave e modelli disponibili prima di modificare le impostazioni.
3. Premi **Risolvi un problema**, allega eventuali file e descrivi il risultato desiderato. La squadra sceglie i ruoli utili, esegue gli incarichi e consegna i file nella chat.

Esempio: «Ho queste vendite e devo condividerle con un cliente. Prepara un foglio con i totali e una breve relazione in Word e PDF».

Non occorre indicare agenti, skills o strumenti. Il modello condiviso coordina il lavoro; ciascuno dei 13 specialisti mantiene la propria procedura, i comandi del programma e i controlli sul formato. Gli incarichi vengono eseguiti uno alla volta per il profilo VPS da 4 GB.

Per cambiare modello torna nello stesso riquadro. **Aggiorna elenco modelli** legge quelli disponibili nel servizio già collegato; non richiede di reinserire la chiave. Premi **Salva modifiche**: il salvataggio aggiorna coordinatore e specialisti. **Risolvi un problema** si trova accanto al pulsante di salvataggio. **Impostazioni → Modelli** rimanda a questo stesso pannello.

Le schede degli specialisti sono chiuse per impostazione iniziale: puoi consultarne i ruoli e, facoltativamente, aggiungere preferenze o competenze. Non contengono selettori di motore o modello.

## Installazioni precedenti

Il primo salvataggio della squadra sostituisce le vecchie scelte di motore/modello dei 13 specialisti con l’ereditarietà. Conserva istruzioni, skills aggiuntive e stato attivo. Gli identificatori dei vecchi profili Studio restano utilizzabili dalle conversazioni salvate, ma seguono la nuova scelta condivisa. I vecchi endpoint di configurazione del coordinatore e di collegamento DeepSeek aggiornano anch’essi la squadra.

La configurazione del profilo nel volume `studio-state` è la fonte del modello effettivo: le skills non contengono copie del modello o delle credenziali. La chiave viene custodita separatamente, non è restituita dal catalogo e il browser svuota il campo dopo il salvataggio. Non viene salvata in localStorage.

Il profilo condiviso supporta DeepSeek API e Codex. Gemini CLI resta disponibile alle integrazioni precedenti; non viene offerto come coordinatore perché questa funzione non è implementata.
