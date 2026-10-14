---
name: artcraft-figcraft
description: "Layout UI, componenti, variabili, frame e prototipi. Usa questa skill per lavorare con figcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Interfacce e prototipi

CLI: `figcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help figcraft` e consulta `/opt/artcraft/reference/figcraft/help.txt`.
3. Salva il registro reale con `craft commands figcraft > /mnt/user-data/work/figcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools figcraft --out /mnt/user-data/work/figcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch figcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Definisci viewport, griglia, componenti e stili condivisi.
- Verifica spaziature, vincoli, stati e contrasto dei componenti.
- Consegna sorgente modificabile e anteprime; segnala i limiti dell’export .fig.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
figcraft-cli commands --json
figcraft-cli info input.figcraft --json
figcraft-cli render input.figcraft -o preview.png --scale 2
figcraft-cli export input.figcraft -o exports --format svg
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/figcraft/tree/v0.6.0
- https://github.com/storytold/figcraft/releases
