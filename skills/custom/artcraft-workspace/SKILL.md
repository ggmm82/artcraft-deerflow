---
name: artcraft-workspace
description: "Regole comuni per usare le CLI ArtCraft nella sandbox e scambiare file tra specialisti."
---

# Spazio di lavoro ArtCraft

- Tutti i file di lavoro devono stare sotto `/mnt/user-data`. I file temporanei fuori da questo percorso possono scomparire alla chiusura della sandbox.
- Crea `work/<incarico>/<specialista>/`, `outputs/` e `previews/` sotto `/mnt/user-data` se non esistono.
- I file caricati dall'utente sono input: non sovrascriverli. Produci nuovi sorgenti modificabili ed export.
- Ogni agente scrive solo nella cartella assegnata. La sandbox è condivisa dagli agenti della conversazione: le cartelle e le skills NON sono un confine di sicurezza fra colleghi.
- I parametri JSON restano nella sintassi richiesta dal programma. Per dati tabellari usa celle numeriche, formattazione italiana e unità nelle intestazioni.
- Prima di un lavoro verifica `craft list`, `craft help APP`, `craft commands APP`.
- `craft tools APP --out percorso.json` elenca tutti gli schemi MCP della CLI senza eseguire modifiche.
- `craft batch APP sequenza.json` esegue una lista di `{"name":"nome_tool_reale","arguments":{...}}` nella stessa sessione. Gli ID restituiti possono essere ripresi con `{"$result":"0.structuredContent.document_id"}`: il percorso deve corrispondere al risultato reale, non a un esempio inventato. Per un intero risultato usare `{"$result":"0"}`. Il batch si ferma su errori JSON-RPC o `isError`.
- Il processo MCP si chiude alla fine del batch: includi i comandi di salvataggio. Non presumere che lo stato in memoria sopravviva tra due invocazioni.
- Le CLI e i loro MCP sono locali alla sandbox. Non registrare questi eseguibili come MCP stdio nel Gateway: lì non sono installati.
- Le skills vengono scoperte dinamicamente; i tool nativi si scoprono dalla release reale. Non installare altre versioni durante un incarico.
- Verifica prima la struttura del documento, poi l'export. Per immagini/slide/PDF genera e ispeziona anteprime quando il modello può ricevere immagini. Per audio/video usa anche ffprobe; indica separatamente ciò che non hai ascoltato o visionato.
- Scrivi un piccolo `handoff.json` nella cartella assegnata con `task`, `source_files`, `output_files`, `checks`, `warnings`. Riporta percorsi completi e non nomi ambigui.
- L'accesso Internet dalla sandbox è disabilitato nella configurazione predefinita. Modelli e chat funzionano dal Gateway; per risorse esterne chiedi di caricare i file o modifica consapevolmente la politica di rete.
