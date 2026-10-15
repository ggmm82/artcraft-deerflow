---
name: artcraft-cadcraft
description: "Disegno tecnico, geometrie, quote e scambio DXF. Usa questa skill per lavorare con cadcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Disegno CAD

Specialista: `cadcraft` per `studio_delegate`; nome della skill: `artcraft-cadcraft`.
CLI: `cadcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa CADCraft per disegno tecnico, geometrie, layer, quote e DXF. Una rappresentazione grafica non sostituisce la verifica delle dimensioni.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help cadcraft` e consulta `/opt/artcraft/reference/cadcraft/help.txt`.
3. Salva il registro reale con `craft commands cadcraft > "$ARTCRAFT_OUTPUT_DIR/work/cadcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools cadcraft --out "$ARTCRAFT_OUTPUT_DIR/work/cadcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch cadcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Definisci unità, scala, origine, sistema di coordinate e tolleranze. Se mancano misure essenziali non inventarle: esplicita le assunzioni o segnala il blocco.
2. Organizza layer e geometrie; verifica chiusura dei contorni, intersezioni, duplicati e coerenza delle quote. Distingui unità del modello e scala di stampa.
3. Misura entità e ingombri numericamente prima dell’export. Conserva geometria editabile e controlla le entità supportate dal formato di scambio.

## Diagnosi e recupero CLI

- Se le dimensioni differiscono, controlla unità del disegno, fattore di conversione e scala di stampa separatamente. Misura numericamente il DXF riaperto, senza inferire distanze dai pixel.
- Se un contorno non è chiuso, individua vertici estremi, tolleranze e duplicati; non unire automaticamente geometrie che cambiano misure o vincoli del brief.
- Dopo un errore leggi il risultato e lo schema del solo tool coinvolto. Riparti dalla copia salvata più recente e verifica gli effetti già applicati prima di ripetere una mutazione.

## Controlli di accettazione

- Riapri DXF e confronta unità, bounding box, conteggio entità e distanze campione con i requisiti e le tolleranze.
- Genera un’anteprima con quote leggibili, verificando scala e orientamento; la sola anteprima non prova accuratezza metrica.
- Consegna disegno sorgente, DXF e riepilogo delle misure; segnala spline, quote o layer persi in conversione.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
cadcraft-cli commands
cadcraft-cli info input.dxf
cadcraft-cli convert input.dxf output.svg
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/cadcraft/tree/v0.7.0
- https://github.com/storytold/cadcraft/releases
