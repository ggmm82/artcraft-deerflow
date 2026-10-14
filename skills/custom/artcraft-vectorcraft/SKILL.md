---
name: artcraft-vectorcraft
description: "Loghi, icone, tracciati, illustrazioni e SVG. Usa questa skill per lavorare con vectorcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Grafica vettoriale

CLI: `vectorcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help vectorcraft` e consulta `/opt/artcraft/reference/vectorcraft/help.txt`.
3. Salva il registro reale con `craft commands vectorcraft > /mnt/user-data/work/vectorcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools vectorcraft --out /mnt/user-data/work/vectorcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch vectorcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Definisci dimensioni delle tavole, palette e tipografia.
- Mantieni tracciati e testo modificabili nel sorgente.
- Controlla viewBox, margini, font e rasterizzazioni nell’export SVG/PDF.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
vectorcraft-cli commands
vectorcraft-cli run --in input.vectorcraft --export output.pdf
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/vectorcraft/tree/v0.11.0
- https://github.com/storytold/vectorcraft/releases
