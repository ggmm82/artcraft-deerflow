# Regia adattabile

Compila i ruoli professionali dal brief con `studio_plan(roles_json=...)`, senza un elenco di professioni. Il catalogo contiene gli strumenti installati, non tutti i mestieri possibili: seleziona le CLI pertinenti oppure usa il workspace senza CLI. Esegui i ruoli compilati con `studio_delegate(agent="workspace", role_id=...)` e torna ai ruoli quando il prodotto lo richiede. La memoria delle attività non è una pipeline rigida: si può cambiare ordine, aggiungere un’integrazione di prova prima della produzione completa e far controllare a un collega i risultati incompleti.

## Esempio: robot che balla

Concorda stile, durata e ritmo; poi crea una breve prova coerente del soggetto, del movimento e della base musicale. PhotoCraft può preparare asset e texture, EffectCraft il movimento, SoundCraft un breve loop e FilmCraft una prima versione audiovisiva. Non attendere che ogni componente sia perfetto per controllare il risultato completo. Verifica inquadratura, proporzioni, pose riconoscibili, luce, ritmo e presenza di audio prima di estendere il render.

Un ordine utile può essere concept → breve prova di movimento → ritmo di prova → primo montaggio → revisione di camera/materiali → musica definitiva → montaggio finale. Se gli asset esistono già, parti dall’integrazione. Se il mix richiede una piccola attenuazione, falla correggere senza bloccare il video per una sessione non chiusa o uno ZIP mancante. Non promettere che una mesh procedurale sia fotorealistica soltanto perché è tecnicamente 3D.

Mantieni `summary` e `next_action` brevi e aggiornati tramite `studio_plan`. L’utente deve riconoscere dove guardare: il pannello è sopra la casella di scrittura. «Vedi risultato» apre una bozza o il prodotto finale, «Squadra» descrive le attività, «File e sorgenti» mantiene i download e «Attività» raccoglie dettagli e cronologia. Evita resoconti di cartelle e letture CLI nella conversazione.

## Recupero

- Un WAV già esportato può essere verificato e importato in FilmCraft anche se SoundCraft ha esaurito i turni prima del manifesto.
- Una revisione dell’animazione non cancella il mix pronto. Controlla se tempi e cue cambiano; aggiorna solo le parti coinvolte.
- Una quota esaurita richiede pausa e azione sul servizio condiviso. Conserva i file e mostra il problema in chiaro; non continuare a chiamare lo stesso provider.
- Un controllo GUI non disponibile va dichiarato, non aggirato inventando un passed e non usato come motivo per ricominciare tutto.
- Un risultato utile ma provvisorio può diventare input di una verifica. Per la consegna finale restano necessari sorgenti, risorse, riapertura e requisiti reali del prodotto.

## Comporre altre squadre

| Bisogno | Collaborazione tipica |
| --- | --- |
| Report con dati | GridCraft → WordCraft → PdfCraft per il controllo PDF richiesto |
| Brochure | WordCraft + PhotoCraft/VectorCraft → DesignCraft → PdfCraft |
| Presentazione | GridCraft + WordCraft + PhotoCraft/VectorCraft → DeckCraft |
| Foto RAW per catalogo | LightCraft → PhotoCraft → DesignCraft |
| Logo o identità | VectorCraft → PhotoCraft per mockup e varianti raster se utili |
| Interfaccia/prototipo | WordCraft/contenuti + VectorCraft/PhotoCraft → FigCraft |
| Tavola tecnica | CadCraft → DesignCraft/WordCraft per manuale, PdfCraft per PDF se richiesto |
| Video con effetti e musica | PhotoCraft/VectorCraft → EffectCraft + SoundCraft → FilmCraft |
| Semplice ritocco o taglio audio | Un solo specialista pertinente, senza piano complesso |

Adatta ruoli e controlli al brief; gli esempi non autorizzano sostituzioni silenziose, conteggi di tool decorativi o capacità inesistenti.

## Accettazione della consegna

`purpose=delivery` prepara una versione disponibile; leggi `delivery.issues` e completa i sorgenti prima di dichiararla pronta. `purpose=review` valuta separatamente il file esatto con `quality-review.json` e criteri specifici al brief; il runtime conserva il suo hash. Le verifiche automatiche non sono una recensione artistica. Per audiovisivi la revisione deve includere la modalità realmente necessaria (visione/ascolto), oppure restare da valutare. Il trasporto DeepSeek corrente è solo testuale. Non rigenerare un prodotto perché manca una capacità sensoriale e non cambiare servizio automaticamente.
