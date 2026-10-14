---
name: artcraft-filmcraft
description: "Timeline, montaggio, transizioni, colore ed esportazione video. Usa questa skill per lavorare con filmcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Montaggio video

CLI: `filmcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help filmcraft` e consulta `/opt/artcraft/reference/filmcraft/help.txt`.
3. Salva il registro reale con `craft commands filmcraft > /mnt/user-data/work/filmcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools filmcraft --out /mnt/user-data/work/filmcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch filmcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Ispeziona tutti i media: durata, codec, frame rate, dimensioni e canali audio.
- Lavora su un progetto salvato; usa frame di prova prima di render lunghi.
- Verifica durata, sincronizzazione, media mancanti e file finale con ffprobe.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
filmcraft-cli probe input.mp4
filmcraft-cli commands --json
filmcraft-cli --project input.fcproj inspect
filmcraft-cli --project input.fcproj export output.mp4 --gpu-rendering off
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/filmcraft/tree/v0.7.2
- https://github.com/storytold/filmcraft/releases
