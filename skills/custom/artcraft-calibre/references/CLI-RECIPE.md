# Ricette CLI verificate

L’adattatore distingue i profili Qt: conversione e rendering usano Xvfb/xcb con OpenGL software; `inspect` e `check` del contenitore usano offscreen, senza dipendenza dal display. Un crash Qt/GLX non dimostra che il libro sia corrotto: conserva log ed exit code, ripeti il controllo nella configurazione pertinente e mantieni separato il fallimento storico dal risultato corrente. Non disattivare la validazione e non dichiarare compatibilità con lettori non provati.

`check` conserva la severità nativa degli avvisi e indica separatamente `blocking`. Un `DanglingLink` (destinazione assente) blocca il prodotto anche quando Calibre lo chiama warning; `NonLinearItems` resta un avviso compatibile con percorsi interattivi intenzionali. Non ridurre tutti gli avvisi a errori e non ignorare una risorsa mancante per ottenere un passed.

Sostituisci i percorsi con file reali del lavoro; output nuovi, mai l’originale. Queste prove minime verificano le API, non il livello del risultato richiesto.

```sh
craft help calibre
craft commands calibre
craft tools calibre
calibre-cli convert /mnt/user-data/input/documento.xhtml /mnt/user-data/outputs/prodotto.epub --epub-version 3 --title "Titolo" --authors "Nome Cognome" --language it
calibre-cli inspect /mnt/user-data/outputs/prodotto.epub
calibre-cli check /mnt/user-data/outputs/prodotto.epub
calibre-cli unpack /mnt/user-data/outputs/prodotto.epub /mnt/user-data/outputs/sorgenti
# Modifica XHTML/CSS nella copia estratta; conserva .artcraft-source.json.
calibre-cli pack /mnt/user-data/outputs/sorgenti /mnt/user-data/outputs/ricostruito.epub
calibre-cli check /mnt/user-data/outputs/ricostruito.epub
calibre-cli convert /mnt/user-data/outputs/prodotto.epub /mnt/user-data/outputs/prodotto.pdf
calibre-cli metadata /mnt/user-data/outputs/prodotto.epub /mnt/user-data/outputs/metadata.epub --title "Titolo corretto"
calibre-cli polish /mnt/user-data/outputs/prodotto.epub /mnt/user-data/outputs/rifinito.epub --smarten-punctuation
```

Le chiamate MCP usano gli stessi argomenti JSON in `craft batch calibre`: un file JSON contiene una lista come `[{"name":"calibre.convert","arguments":{"input":"/mnt/user-data/input/documento.xhtml","output":"/mnt/user-data/outputs/prodotto.epub","epub_version":"3"}}]`. Esegui `craft batch calibre /mnt/user-data/work/operazioni.json --out /mnt/user-data/work/esiti.json`. La libreria locale è opzionale: `calibre-cli call library '{"library":"/mnt/user-data/work/libreria","action":"add","input":"/mnt/user-data/outputs/prodotto.epub"}'`; list restituisce gli ID da usare per export.

Per `delivery`, allega sorgenti, prodotto, istruzioni e rapporto delle verifiche. ZIP standard con percorsi relativi e tutti gli asset; verifica con `python3 /opt/studio/source_packages.py verify PACCHETTO.zip --native`. Non usare `source_packages.py pack` per EPUB: quel comando prepara progetti Craft JSON. Dopo il trasferimento riapri e ricostruisci una copia. Il rapporto nativo non certifica lettori, impaginazione, accessibilità o qualità editoriale.
