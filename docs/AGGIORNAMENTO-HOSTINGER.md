# Un giro solo: prova la PR, poi promuovi le stesse immagini

## Per ogni modifica

1. **Apri la PR.** La pipeline costruisce le quattro immagini una volta, esegue test Python, integrazioni dei provider, lavorazioni delle 13 CLI e avvio completo. Il test di avvio usa i digest delle immagini già verificate, senza ricostruirle.
2. **Quando la CI è verde, scarica «Compose di prova PR».** Il collegamento è nel riepilogo del controllo `release`, sotto **Compose pronto**, ed è anche negli allegati del prerelease GitHub. Il file si chiama sempre `compose.hostinger.yaml`. Non serve fare prima il merge.
3. **Installa e collauda la prova.** Usa un progetto Hostinger separato con nome diverso, per esempio `artcraft-prova`, e imposta `ARTCRAFT_PROJECT_NAME=artcraft-prova`; il nome della produzione resta quello esistente. Mantieni separati volumi, account, dati e credenziali di prova. Il dominio viene derivato dal nome progetto e da `TRAEFIK_HOST`. Su un VPS con risorse limitate assicurati che il progetto di prova abbia memoria disponibile durante gli incarichi; puoi usare un’istanza dedicata al collaudo.
4. **Fai il merge dopo il collaudo.** Se il contenuto Git è identico a quello provato, la pipeline riutilizza i quattro digest e lo stesso Compose: non ricompila e non ripete i test già passati. Pubblica soltanto il rilascio stabile. Se nel frattempo il contenuto è cambiato, esegue le prove necessarie sulla versione effettivamente unita.
5. **Aggiorna la produzione dal collegamento stabile.** Il merge pubblica il rilascio, non installa sul VPS:

   https://github.com/ggmm82/artcraft-deerflow/releases/latest/download/compose.hostinger.yaml

   Apri il progetto Docker Hostinger **esistente**, ricarica il Compose dall’URL o scaricalo e sostituiscilo, quindi esegui il deploy. Conserva nome del progetto, variabili e volumi. Se il candidato era già installato nell’ambiente di prova, le immagini sono le stesse. Non occorre cambiare digest o tag a mano.

## Quale file usare

- **Prova prima del merge:** allegato `compose.hostinger.yaml` del prerelease indicato dalla CI di quella PR. Il collegamento è specifico di run e tentativo: identifica esattamente la versione provata. Se aggiorni la PR, usa il nuovo file dopo i nuovi controlli.
- **Produzione:** `releases/latest/download/compose.hostinger.yaml`, aggiornato solo da un rilascio stabile completato. I prerelease PR non cambiano questo collegamento.
- **Sviluppo locale:** `docker-compose.yaml` nel repository.
- **Template interno:** `config/compose.hostinger.template.yaml`. Serve alla pipeline; non va installato direttamente. Il vecchio file installabile nella radice è stato rimosso per evitare di riutilizzare riferimenti obsoleti.

`runtime-manifest.json`, allegato insieme al Compose, registra le quattro immagini per digest, il contenuto Git verificato, il run CI e il checksum del Compose. La promozione non modifica questi file: lo stabile usa esattamente i byte del candidato. I digest impediscono che lo stesso file scarichi in futuro immagini diverse.

## Collaudo utente minimo

Apri il dominio di prova, crea un amministratore e configura una volta **La tua squadra** con un account/chiave dedicato alle prove. Login del sito e password `STUDIO_PASSWORD` sono distinti. Invia un incarico normale, allega un input, verifica la scelta dello specialista, la consegna di sorgenti ed export, la loro apertura nell’app e il download. Per una prova semplice chiedi un foglio con 10, 20, 30 e somma 60, oppure una relazione Word e PDF di una pagina. I test automatici non sostituiscono autenticazione e generazione reali con i tuoi provider.

Per la produzione usa i volumi e le impostazioni già presenti; non collegarla ai volumi del progetto di prova. Non mettere chiavi nel Compose pubblico. Le chiavi e i modelli rimangono nel pannello comune; non vanno riconfigurati a ogni aggiornamento della produzione. Prima di aggiornare servizi con dati fai backup dei volumi. Non usare `down -v` sulla tua installazione.

## Quando può servire una nuova build

Un nuovo contenuto richiede una nuova verifica: PR aggiornata, merge che incorpora cambiamenti ulteriori di `main`, push diretto o avvio manuale. Serve anche se manca o è scaduta la prova CI della PR. Non si riutilizzano run falliti, artefatti incoerenti o immagini appartenenti a un altro repository/workflow.

Le PR provenienti da fork ricevono verifiche senza privilegi di pubblicazione: non hanno un Compose pubblico di prova e il controllo di avvio isolato può ricostruire le immagini. Il percorso con una sola build e prerelease vale per le PR dello stesso repository, come quelle preparate per questo progetto.

Un errore lascia disponibile l’ultimo rilascio stabile riuscito. Un run vecchio non può rimpiazzare la pubblicazione di un `main` più recente. Le bozze vengono pubblicate solo dopo il caricamento degli allegati; un nuovo prerelease non viene dichiarato «latest».
