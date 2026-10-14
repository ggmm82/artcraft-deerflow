---
name: artcraft-gridcraft
description: "Dati, formule, tabelle, grafici e file XLSX. Usa questa skill per lavorare con gridcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Fogli di calcolo

CLI: `gridcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help gridcraft` e consulta `/opt/artcraft/reference/gridcraft/help.txt`.
3. Salva il registro reale con `craft commands gridcraft > /mnt/user-data/work/gridcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools gridcraft --out /mnt/user-data/work/gridcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch gridcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Conserva i valori numerici come numeri; unità e descrizioni nelle intestazioni.
- Presenta numeri con convenzioni italiane; nelle API mantieni la sintassi canonica richiesta dalla CLI.
- Controlla formule, riferimenti, totali e valori di errore dopo il ricalcolo.
- Consegna XLSX con formule e, se richiesto, CSV UTF-8 con separatore esplicito.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
gridcraft-cli info input.xlsx --json
gridcraft-cli commands --json
gridcraft-cli functions --json
gridcraft-cli eval "=SUM(1,2,3)"
gridcraft-cli cat input.xlsx --range A1:D20 --csv
gridcraft-cli check input.xlsx --json
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/gridcraft/tree/v0.7.0
- https://github.com/storytold/gridcraft/releases
