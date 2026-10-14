---
name: artcraft-deckcraft
description: "Struttura narrativa, slide, layout, grafici e PPTX. Usa questa skill per lavorare con deckcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Presentazioni

CLI: `deckcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help deckcraft` e consulta `/opt/artcraft/reference/deckcraft/help.txt`.
3. Salva il registro reale con `craft commands deckcraft > /mnt/user-data/work/deckcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools deckcraft --out /mnt/user-data/work/deckcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch deckcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Definisci pubblico, obiettivo e formato prima delle slide.
- Usa dati e asset verificati dagli altri specialisti.
- Controlla tutte le slide renderizzate per tagli, sovrapposizioni e leggibilità.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
deckcraft-cli commands
deckcraft-cli info input.pptx
deckcraft-cli render input.pptx --all preview
deckcraft-cli convert input.deckcraft output.pptx
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/deckcraft/tree/v0.7.0
- https://github.com/storytold/deckcraft/releases
