---
name: artcraft-cadcraft
description: "Disegno tecnico, geometrie, quote e scambio DXF. Usa questa skill per lavorare con cadcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Disegno CAD

CLI: `cadcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help cadcraft` e consulta `/opt/artcraft/reference/cadcraft/help.txt`.
3. Salva il registro reale con `craft commands cadcraft > /mnt/user-data/work/cadcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools cadcraft --out /mnt/user-data/work/cadcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch cadcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Dichiara unità, scala, origine e tolleranze del disegno.
- Controlla dimensioni geometriche e quote, non soltanto l’immagine.
- Registra eventuali perdite di dati nell’import/export dei formati.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
cadcraft-cli commands
cadcraft-cli info input.dxf
cadcraft-cli convert input.dxf output.svg
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/cadcraft/tree/v0.7.0
- https://github.com/storytold/cadcraft/releases
