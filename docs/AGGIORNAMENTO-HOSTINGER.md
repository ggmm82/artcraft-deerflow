# Aggiornamento dell’istanza Hostinger

Istanza da aggiornare: https://artcraft-deerflow.srv1757745.hstgr.cloud/

1. Aprire il progetto Docker **esistente** in Hostinger. Conservare nome del progetto, variabili e volumi; salvare un backup dei dati prima dell’aggiornamento.
2. Sostituire il Compose con l’allegato del rilascio verificato oppure usare questo URL:

   https://github.com/ggmm82/artcraft-deerflow/releases/latest/download/compose.hostinger.yaml

   Avviare l’aggiornamento scaricando le immagini indicate. Non rimuovere i volumi. Non occorre inserire le chiavi dei modelli nel Compose.
3. Attendere che il Gateway risulti pronto, aprire il sito e accedere con l’account **amministratore DeerFlow già esistente**. Aprire “La tua squadra”, scegliere Codex, Gemini o DeepSeek e completare il collegamento nello stesso pannello. Salvare la squadra una volta: il modello si applica al coordinatore e a tutti gli specialisti.

Dalla chat descrivere il problema e allegare gli input. Per una prova semplice chiedere di creare un foglio con 10, 20, 30 e la somma e un documento PDF con lo stesso totale. Scaricare i file e controllare che il totale sia 60. Codex e Gemini richiedono il proprio accesso ufficiale e disponibilità del servizio.

Il controllo iniziale sul VPS ha confermato readiness e login browser, ma ha rilevato il vecchio catalogo senza configurazione unica. Dopo l’aggiornamento `/studio/api/catalog`, consultato come amministratore, deve includere `team` ed `effective_agents`; un account ordinario riceve 403 sulla configurazione e continua a lavorare dalla chat. L’endpoint `/studio/api/team/models` deve essere disponibile; un errore di collegamento del provider è distinto dal precedente 404 per rotta assente.

Il Compose non aggiorna automaticamente un progetto già attivo. La verifica del nuovo rilascio sul dominio reale va eseguita dopo l’installazione.
