---
name: artcraft-lightcraft
description: "Cataloghi fotografici, sviluppo RAW e lavorazioni in serie. Usa questa skill per lavorare con lightcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Fotografia e RAW

CLI: `lightcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help lightcraft` e consulta `/opt/artcraft/reference/lightcraft/help.txt`.
3. Salva il registro reale con `craft commands lightcraft > /mnt/user-data/work/lightcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools lightcraft --out /mnt/user-data/work/lightcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch lightcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Mantieni gli originali e gli eventuali sidecar intatti.
- Controlla esposizione, bilanciamento del bianco e clipping sui campioni.
- Applica elaborazioni in serie solo dopo avere verificato un’immagine campione.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
lightcraft-cli commands --json
lightcraft-cli render input.jpg -o output.jpg --set light.exposure=0.5
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/lightcraft/tree/v0.8.0
- https://github.com/storytold/lightcraft/releases
