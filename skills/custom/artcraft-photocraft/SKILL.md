---
name: artcraft-photocraft
description: "Livelli, maschere, correzioni, compositing e PSD. Usa questa skill per lavorare con photocraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Immagini e ritocco

Specialista: `photocraft` per `studio_delegate`; nome della skill: `artcraft-photocraft`.
CLI: `photocraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa PhotoCraft per ritocco raster, livelli, maschere e compositing. Per lo sviluppo RAW usa LightCraft; per loghi scalabili usa VectorCraft.

## Ricetta operativa collaudata

Leggi [la ricetta CLI verificata](references/CLI-RECIPE.md), inclusa anche dal runtime. Mantieni i controlli e adatta la procedura agli input reali.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help photocraft` e consulta `/opt/artcraft/reference/photocraft/help.txt`.
3. Salva il registro reale con `craft commands photocraft > "$ARTCRAFT_OUTPUT_DIR/work/photocraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools photocraft --out "$ARTCRAFT_OUTPUT_DIR/work/photocraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch photocraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Rileva dimensioni in pixel, orientamento EXIF, profilo colore, profondità, alpha e struttura dei livelli. Chiarisci il formato e la risoluzione di consegna; non confondere DPI e numero di pixel.
2. Duplica il documento e mantieni livelli nominati, maschere modificabili e originale intatto. Applica correzioni su un campione prima di operazioni estese; evita ricampionamenti ripetuti.
3. Esporta una copia nel profilo richiesto. Per JPEG scegli uno sfondo esplicito; per PNG controlla trasparenza e bordi. Non promettere funzioni PSD che la release non conserva.

## Diagnosi e recupero CLI

- Se un filtro non produce l’effetto atteso, verifica livello attivo, selezione, maschera e visibilità prima di ripeterlo. Non applicare lo stesso filtro due volte alla cieca.
- Se l’export perde alpha o livelli, confronta capacità del formato e modalità di esportazione nel registro. Conserva il progetto e dichiara l’eventuale appiattimento.
- Dopo un errore leggi il risultato e lo schema del solo tool coinvolto. Riparti dalla copia salvata più recente e verifica gli effetti già applicati prima di ripetere una mutazione.

## Controlli di accettazione

- Riapri sorgente ed export e confronta dimensioni, livelli e alpha attesi.
- Genera anteprima complessiva e dettagli al 100% di bordi, maschere e ritocchi; registra se non puoi ispezionarli visivamente.
- Consegna sorgente con livelli, immagine finale e anteprime; dichiara eventuali livelli appiattiti o variazioni del profilo.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
photocraft-cli info input.psd
photocraft-cli commands --filter blur
photocraft-cli convert input.psd output.png
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/photocraft/tree/v0.8.2
- https://github.com/storytold/photocraft/releases
