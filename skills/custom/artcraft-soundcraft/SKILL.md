---
name: artcraft-soundcraft
description: "Montaggio, mix, tracce, elaborazione e bounce audio. Usa questa skill per lavorare con soundcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Produzione audio

CLI: `soundcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help soundcraft` e consulta `/opt/artcraft/reference/soundcraft/help.txt`.
3. Salva il registro reale con `craft commands soundcraft > /mnt/user-data/work/soundcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools soundcraft --out /mnt/user-data/work/soundcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch soundcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Rileva frequenza di campionamento, canali e durata delle sorgenti.
- Mantieni margine di livello, evita clipping e conserva il progetto multitraccia.
- Controlla durata, picchi e formato; non dichiarare ascolto o qualità percettiva verificati senza un controllo audio reale.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
soundcraft-cli commands
soundcraft-cli run --demo --bounce output.wav
ffprobe -v error -show_format -show_streams -of json output.wav
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/soundcraft/tree/v0.7.0
- https://github.com/storytold/soundcraft/releases
