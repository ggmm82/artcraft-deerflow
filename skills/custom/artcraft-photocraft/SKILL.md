---
name: artcraft-photocraft
description: "Livelli, maschere, correzioni, compositing e PSD. Usa questa skill per lavorare con photocraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Immagini e ritocco

CLI: `photocraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help photocraft` e consulta `/opt/artcraft/reference/photocraft/help.txt`.
3. Salva il registro reale con `craft commands photocraft > /mnt/user-data/work/photocraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools photocraft --out /mnt/user-data/work/photocraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch photocraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Ispeziona dimensioni, profilo colore, livelli e trasparenza prima delle modifiche.
- Conserva il sorgente con livelli e salva gli export separatamente.
- Verifica l’anteprima, il ritaglio e la leggibilità alla risoluzione di consegna.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
photocraft-cli info input.psd
photocraft-cli commands --filter blur
photocraft-cli convert input.psd output.png
```

## Consegna

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/photocraft/tree/v0.8.2
- https://github.com/storytold/photocraft/releases
