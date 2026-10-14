---
name: artcraft-effectcraft
description: "Composizioni, keyframe, motion graphics ed effetti video. Usa questa skill per lavorare con effectcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Animazione ed effetti

CLI: `effectcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help effectcraft` e consulta `/opt/artcraft/reference/effectcraft/help.txt`.
3. Salva il registro reale con `craft commands effectcraft > /mnt/user-data/work/effectcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools effectcraft --out /mnt/user-data/work/effectcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch effectcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Definisci durata, frame rate, risoluzione e composizione principale.
- Verifica frame iniziale, intermedio e finale prima di esportare il video.
- Controlla dipendenze, media collegati, alpha e formato di consegna.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
effectcraft-cli commands
effectcraft-cli info input.ecproj
effectcraft-cli render --comp Main --out output.mp4 input.ecproj
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/effectcraft/tree/v0.10.0
- https://github.com/storytold/effectcraft/releases
