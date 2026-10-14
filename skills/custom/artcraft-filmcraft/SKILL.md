---
name: artcraft-filmcraft
description: "Timeline, montaggio, transizioni, colore ed esportazione video. Usa questa skill per lavorare con filmcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Montaggio video

Specialista: `filmcraft` per `studio_delegate`; nome della skill: `artcraft-filmcraft`.
CLI: `filmcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa FilmCraft per montaggio, timeline e integrazione audio/video. Usa EffectCraft per composizioni animate e SoundCraft per un mix multitraccia complesso.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help filmcraft` e consulta `/opt/artcraft/reference/filmcraft/help.txt`.
3. Salva il registro reale con `craft commands filmcraft > "$ARTCRAFT_OUTPUT_DIR/work/filmcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools filmcraft --out "$ARTCRAFT_OUTPUT_DIR/work/filmcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch filmcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Ispeziona ciascun media con probe/ffprobe: durata, codec, frame rate, dimensioni, rotazione, canali e sample rate. Stabilisci risoluzione, fps, aspect ratio e durata di destinazione.
2. Crea una timeline con tagli e sincronizzazione espliciti; conserva i media collegati. Esegui una breve esportazione di prova con rendering CPU prima di render lunghi sulla VPS.
3. Verifica inizio, transizioni, sincronizzazione labiale, titoli e finale. Esporta il progetto modificabile e un file con codec/container concordati; non presumere che l’estensione determini il codec.

## Controlli di accettazione

- Con ffprobe confronta durata, fps, risoluzione e stream audio con il brief; controlla media mancanti e decodifica del file.
- Genera fotogrammi iniziale/intermedi/finale e campioni delle transizioni; un frame corretto non dimostra la qualità dell’intero video.
- Indica separatamente controlli tecnici, visione e ascolto eseguiti. Consegna progetto, dipendenze e video.

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

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/filmcraft/tree/v0.7.2
- https://github.com/storytold/filmcraft/releases
