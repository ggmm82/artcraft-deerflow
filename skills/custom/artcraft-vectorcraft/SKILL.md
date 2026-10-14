---
name: artcraft-vectorcraft
description: "Loghi, icone, tracciati, illustrazioni e SVG. Usa questa skill per lavorare con vectorcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Grafica vettoriale

Specialista: `vectorcraft` per `studio_delegate`; nome della skill: `artcraft-vectorcraft`.
CLI: `vectorcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa VectorCraft per loghi, icone, illustrazioni e tracciati scalabili. Il ritocco fotografico appartiene a PhotoCraft; componenti UI e prototipi a FigCraft.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help vectorcraft` e consulta `/opt/artcraft/reference/vectorcraft/help.txt`.
3. Salva il registro reale con `craft commands vectorcraft > "$ARTCRAFT_OUTPUT_DIR/work/vectorcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools vectorcraft --out "$ARTCRAFT_OUTPUT_DIR/work/vectorcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch vectorcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Definisci tavole, unità, viewBox, palette e ingombro finale. Per icone considera anche una versione alla dimensione minima richiesta.
2. Organizza gruppi e livelli con nomi; mantieni tracciati e testo modificabili. Usa geometrie coerenti, allineamenti e spessori controllati; evita immagini raster incorporate quando il requisito è vettoriale.
3. Conserva una copia con testo editabile prima di convertire caratteri in tracciati. Verifica font e licenze degli asset forniti; non sostituire silenziosamente il marchio.

## Controlli di accettazione

- Riapri SVG/PDF e controlla viewBox, clipping, proporzioni e presenza di bitmap inattese.
- Renderizza su sfondo chiaro e scuro se è previsto alpha; verifica i tratti e la leggibilità alla dimensione d’uso.
- Consegna sorgente, SVG e varianti richieste; segnala font sostituiti, testo convertito e limiti dell’export.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
vectorcraft-cli commands
vectorcraft-cli run --in input.vectorcraft --export output.pdf
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/vectorcraft/tree/v0.11.0
- https://github.com/storytold/vectorcraft/releases
