# Calibre CLI come capacità disponibile

Release ufficiale **9.16.0** fissata con URL, dimensione e SHA-256 per amd64 e arm64 in `versions.lock.json`. Il runtime completo resta linux/amd64 per il vincolo Blender. Nessun aggiornamento automatico al riavvio.

L’installazione espone i launcher ufficiali dalla radice della distribuzione (`ebook-convert`, `ebook-meta`, `ebook-polish`, `calibre-debug`, `calibredb`, `ebook-edit`) e l’adattatore headless `calibre-cli`. Non installa il server Calibre, non pubblica porte, non connette librerie personali e non crea una configurazione modello separata. Qt usa offscreen nel worker isolato; nessuna GUI web viene promessa.

Le otto operazioni MCP sono convert, inspect, check, metadata, polish, unpack, pack e library. Input preservati, output nuovi, percorsi confinati, processi supervisionati, errori e avvisi nativi. La skill documenta discovery, operazioni, ricette, sorgenti e controlli; il contesto compilato del ruolo la carica quando Calibre è selezionato fra i suoi strumenti.

L’integrazione non introduce professioni predefinite o una sequenza editoriale. Per qualsiasi progetto il coordinatore chiarisce risultato, formato, uso e criteri mancanti, compila i ruoli necessari e assegna attività adattabili. Calibre serve dove una capacità documentale è utile, anche come parte di un progetto di software, architettura, eventi o altro. Gli strumenti non vanno usati tutti per principio.

## Verifiche e sorgenti

Il collaudo nativo automatizzato produce EPUB, AZW3, PDF e DOCX da XHTML, legge metadati e ordine di lettura, modifica una copia estratta e la ricostruisce, prova polish, libreria locale, export e trasferimento ZIP. Controlla contenuti testuali e input intatti; verifica che file corrotti e risorse mancanti falliscano.

L’estensione dei controlli mantiene riconosciuti gli hash esatti dei preparatori FilmCraft già pubblicati; i vecchi script non vengono eseguiti dal verificatore e gli script sconosciuti restano rifiutati.

Il runtime controlla EPUB/AZW3 consegnati e presenti negli archivi con il checker Calibre reale. Gli avvisi sono conservati, gli errori impediscono l’approvazione tecnica. Non viene dichiarata una certificazione EPUBCheck, accessibilità, qualità dei contenuti o resa in ogni lettore. Le altre conversioni esposte richiedono verifica nel formato e nell’app richiesti, non sono tutte certificate dal singolo test EPUB.

Consegna il file finale e il sorgente di authoring effettivo con risorse e istruzioni. EPUB è modificabile in `ebook-edit`; uno ZIP XHTML/CSS/OPF può agevolare la lavorazione ma non sostituisce arbitrariamente un originale DOCX complesso. La riapertura CLI non significa che sia stata provata l’interfaccia grafica.

## Aggiungere un altro strumento

Lo stesso percorso vale per nuove CLI: release e checksum nel catalogo, launcher espliciti se la distribuzione ne contiene più di uno, adattatore MCP se manca, skill operativa con ricette provate e limiti, accettazione nativa che verifica file reali e round-trip dei sorgenti. Poi `scripts/sync_catalog.py` propaga catalogo e routing mantenendo `model: inherit`. I ruoli restano compilati sul brief, senza aggiungere un catalogo universale di professioni. La CI costruisce e collauda il Compose candidato della PR prima del merge.
