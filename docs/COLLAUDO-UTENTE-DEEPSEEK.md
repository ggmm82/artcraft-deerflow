# Collaudo utente con DeepSeek · configurazione unica

**Esito: superato il 15 ottobre 2026**, usando dal browser la chiave DeepSeek più recente fornita dal proprietario. Il modello condiviso è `deepseek-flash`; coordinatore e specialisti eseguono chiamate API reali. Nessuna chiave è inclusa nel codice, nelle immagini del rapporto o nei file consegnati.

L’utente ha scritto una richiesta normale, senza nomi di agenti o strumenti:

> Ho queste vendite e devo condividerle con un cliente. Prepara un foglio Excel modificabile con gli importi numerici e la formula del totale, poi una breve relazione in italiano sia Word sia PDF, con i risultati verificati. Usa i nomi vendite.xlsx, relazione.docx e relazione.pdf. Il lavoro deve essere essenziale e pronto da scaricare.

La squadra ha scelto GridCraft e WordCraft. La ripetizione finale ha richiesto **due incarichi**, con 14 chiamate API per ciascun worker, senza ripetere la generazione dei documenti.

## Percorso verificato

| Passaggio | Risultato osservato |
|---|---|
| Primo avvio | Creazione amministratore, nuova autenticazione e indirizzamento automatico alla configurazione. Verificati nella prima esecuzione completa. |
| Accesso con la nuova chiave | Login utente dal browser; chiave errata rifiutata senza cambiare la squadra; chiave reale accettata e campo svuotato. |
| Configurazione unica | Un salvataggio attiva coordinatore e tutti i 13 specialisti. Ogni ruolo conserva la skill comune e quella specifica. |
| Cambio modello | Menu popolato dai modelli DeepSeek disponibili; cambio e ripristino propagati ai 13 ruoli senza reinserire la chiave. |
| Un solo punto di gestione | Impostazioni → Modelli porta allo stesso pannello e chiude la finestra. Nessun selettore di motore/modello nelle schede dei singoli specialisti. |
| Avvio del lavoro | Chat già sul profilo Squadra ArtCraft, senza selezione manuale. CSV con importi 10, 20 e 30 caricato dal controllo allegati. |
| Collaborazione | Due worker Docker reali, in sequenza, con passaggio dei dati verificati. Entrambi i manifest validi; nessun controllo dichiarato fallito nella consegna finale. |
| Consegna | Stato DeerFlow `success`; archivio con esattamente vendite.xlsx, relazione.docx e relazione.pdf, scaricato dalla chat. Provato anche il download individuale. |
| Contenuto XLSX | Archivio ZIP/XML integro; importi numerici 10/20/30, formula di somma e valore salvato 60. Download individuale identico al file nell’archivio. |
| Contenuto DOCX/PDF | File leggibili, totale 60 in entrambi; PDF di una pagina, titolo e tabella corretti. Rasterizzazione e ispezione visiva indipendente: nessun taglio o sovrapposizione. |
| Riavvio | Nuova sessione browser dopo riavvio Gateway: login, riapertura della conversazione e nuovi download riusciti. Profilo DeepSeek e impostazioni ereditate conservati. |
| Mobile | Pannello verificato a 390 pixel senza scorrimento orizzontale. Accesso alla chat visibile accanto al salvataggio sul desktop. |
| Errore di lettura | Interruzione di rete simulata soltanto per il catalogo: modulo disabilitato, messaggio in italiano, pulsante Riprova; recupero contro l’API reale. |
| Credenziali e accesso | Chiave assente da catalogo e modelli; senza sessione DeerFlow catalogo, elenco modelli collegati e download restituiscono 401, anche con autenticazione del proxy. |

La prova completa finale contiene 17 controlli riusciti. La verifica separata dell’interfaccia ne contiene 6, inclusa la posizione del pulsante per aprire la chat; la riapertura dopo riavvio ne contiene 5. I conteggi comprendono controlli ripetuti su accesso e download.

La qualità dei file è stata controllata anche con parser indipendenti ZIP/XML, pypdf e PyMuPDF, oltre alle verifiche riportate dai modelli. I manifest sono stati rivalidati con il validatore di produzione montando in sola lettura i file della conversazione. GridCraft riporta 10 controlli superati; WordCraft 9 superati e uno `not_run` per la visione delle anteprime, che il motore testuale non deve dichiarare di aver eseguito. L’ispezione visiva del PDF è stata svolta separatamente nel collaudo.

## Problemi trovati e corretti

- **Configurazione dispersa:** collegare il provider, impostare il coordinatore, modificare 13 schede e cambiare modello in chat erano passaggi distinti. Ora il profilo condiviso è la fonte unica; anche gli endpoint precedenti aggiornano la squadra. Il salvataggio elimina le vecchie scelte di modello/motore dei ruoli, preservando preferenze e skills.
- **Primo accesso senza servizio:** la nuova chat indirizza alla configurazione finché la squadra non è pronta. Il modulo attende il caricamento; gli errori hanno un comando per riprovare. Il passaggio alla chat si trova accanto al salvataggio.
- **Ricopie e segnaposto:** una prova con la nuova chiave ha prodotto file temporanei impropri mentre il coordinatore tentava di ricopiare i binari nella radice. Il coordinatore ora legge e delega; non dispone dei tool di scrittura e sostituzione del Gateway. Consegna direttamente i percorsi verificati nelle sottocartelle degli specialisti. La migrazione aggiorna anche installazioni già inizializzate.
- **Turni esauriti prima del manifest:** alcuni incarichi WordCraft creavano documenti ma proseguivano con modifiche opzionali fino al limite. DeepSeek riserva gli ultimi turni o il tempo residuo a `submit_handoff`: una chiamata strutturata registra la consegna e verifica file e percorsi. I file mancanti restano un errore; i requisiti incompleti devono essere dichiarati. La compatibilità del tool forzato è stata provata anche con l’API reale. In una prova intermedia il manifest ha segnalato correttamente PDF mancante e nomi errati, consentendo una revisione mirata.
- **Procedura WordCraft troppo lunga:** la skill ora privilegia, per nuove relazioni brevi, Markdown → DOCX → PDF con le CLI native, conservando titoli e tabelle. La ricetta è stata eseguita direttamente e poi dal modello nella ripetizione finale. Il controllo CI verifica anche la tabella DOCX e il totale nel testo del PDF.

Restano i controlli precedenti su output nella cartella assegnata, risposta JSON completa, rifiuto di consegne prive di file, timeout e rimozione dei container. La suite Python comprende 36 test. Il controllo nativo `--mcp --render` comprende 59 verifiche sulle 13 CLI e sugli export di prova.

## Ambiente e limiti

Il collaudo è locale e temporaneo, **non un deploy su Hostinger**. Gateway e frontend derivano dal commit DeerFlow fissato dal repository. Il frontend è stato ricompilato con le modifiche del progetto ed eseguito come processo locale; i controlli TypeScript e lint sui componenti modificati sono riusciti.

Per il limite disco di 32 GB e il driver Docker VFS, i worker del collaudo usano Python Bookworm con le vere CLI GridCraft 0.7.0, WordCraft 0.7.0 e PdfCraft 0.8.0 estratte dall’immagine fissata, montate in sola lettura. Ricevono il codice del progetto, le skills, proxy e CA dell’ambiente con verifica TLS attiva. Questi adattamenti non sono inseriti nel Compose di produzione. GitHub Actions costruisce separatamente i quattro runtime completi, verifica tutte le CLI e avvia il Compose reale con autenticazione e CSRF.

I tentativi preliminari hanno distinto problemi del prodotto da problemi del banco di prova: dipendenze native del frontend per un sistema differente, interruzione dell’ambiente durante la compilazione e avvio del browser prima della readiness del Gateway. Il test corretto attende il caricamento delle impostazioni e la readiness dell’istanza.

Il risultato dimostra il percorso concreto CSV → XLSX + DOCX + PDF e l’ereditarietà della configurazione su tutti i ruoli. Non certifica ogni formato/import/export dei 13 programmi, gli account OAuth Codex/Gemini o il consumo di RAM su Hostinger. Le applicazioni Craft restano alpha.

Le credenziali temporanee, i container di prova e i volumi vengono rimossi alla conclusione; il pacchetto di collaudo conserva soltanto prove e prodotti, dopo verifica dell’assenza delle chiavi.

## Riproduzione

Su un’istanza isolata del progetto, installa `requirements-uat.txt` e fornisci nell’ambiente `UAT_EMAIL`, `UAT_PASSWORD`, `DEEPSEEK_API_KEY`. Se il proxy usa autenticazione HTTP, aggiungi `UAT_HTTP_USER` e `UAT_HTTP_PASSWORD`. Non inserire credenziali nei comandi versionati.

```bash
python scripts/uat_deepseek.py --initialize-admin --output reports/uat-team
```

`--initialize-admin` serve soltanto a creare il primo account della propria istanza di prova. Per verificare interfaccia e recupero senza nuove chiamate LLM, su un’istanza già collegata:

```bash
python scripts/uat_deepseek.py --settings-only --output reports/uat-settings
```

Per riprovare login e download di una conversazione completata, usa `--thread-url URL --output reports/uat-reopened`: non invia una nuova richiesta al modello. Non vengono registrati HAR, trace o corpi delle richieste di collegamento.
