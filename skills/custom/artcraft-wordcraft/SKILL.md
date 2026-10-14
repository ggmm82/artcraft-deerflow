---
name: artcraft-wordcraft
description: "Documenti strutturati, stili, tabelle, DOCX e PDF. Usa questa skill per lavorare con wordcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Testi e documenti

CLI: `wordcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help wordcraft` e consulta `/opt/artcraft/reference/wordcraft/help.txt`.
3. Salva il registro reale con `craft commands wordcraft > /mnt/user-data/work/wordcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools wordcraft --out /mnt/user-data/work/wordcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch wordcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Scrivi in italiano salvo diversa richiesta; usa stili e titoli strutturati.
- Separa contenuti, riferimenti e dati da elementi decorativi.
- Verifica testo, numerazione, interruzioni, tabelle e anteprime delle pagine esportate.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
wordcraft-cli commands --json
wordcraft-cli inspect input.docx
wordcraft-cli convert input.docx output.pdf
wordcraft-cli render input.docx preview.png --page 1
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/wordcraft/tree/v0.7.0
- https://github.com/storytold/wordcraft/releases
