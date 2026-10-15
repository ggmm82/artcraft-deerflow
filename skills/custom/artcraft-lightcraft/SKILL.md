---
name: artcraft-lightcraft
description: "Cataloghi fotografici, sviluppo RAW e lavorazioni in serie. Usa questa skill per lavorare con lightcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Fotografia e RAW

Specialista: `lightcraft` per `studio_delegate`; nome della skill: `artcraft-lightcraft`.
CLI: `lightcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa LightCraft per sviluppo fotografico RAW, esposizione, colore e serie di foto. Per maschere e compositing con molti livelli usa PhotoCraft.

## Ricetta operativa collaudata

Leggi [la ricetta CLI verificata](references/CLI-RECIPE.md), inclusa anche dal runtime. Mantieni i controlli e adatta la procedura agli input reali.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help lightcraft` e consulta `/opt/artcraft/reference/lightcraft/help.txt`.
3. Salva il registro reale con `craft commands lightcraft > "$ARTCRAFT_OUTPUT_DIR/work/lightcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools lightcraft --out "$ARTCRAFT_OUTPUT_DIR/work/lightcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch lightcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Inventaria originali, metadati, orientamento, profilo e sidecar. Non modificare o spostare i RAW originali. Definisci destinazione, spazio colore, dimensioni e convenzione dei nomi.
2. Sviluppa un’immagine rappresentativa: bilanciamento del bianco, esposizione, recupero luci, ombre e contrasto. Controlla istogramma e clipping prima di sincronizzare le impostazioni.
3. Dividi la serie per condizioni di luce quando necessario. Verifica campioni scuri e chiari; non applicare automaticamente la stessa esposizione a tutta la raccolta. Conserva ricetta/sidecar modificabili se supportati.

## Diagnosi e recupero CLI

- Se una serie produce risultati diversi, raggruppa gli input per profilo, orientamento e luce e verifica una ricetta per gruppo; non correggere sovrascrivendo RAW o sidecar originali.
- Se un RAW non è supportato, registra il formato e l’errore; non spacciare un JPEG incorporato per sviluppo del RAW. Verifica la reale capacità della release prima del lavoro in serie.
- Dopo un errore leggi il risultato e lo schema del solo tool coinvolto. Riparti dalla copia salvata più recente e verifica gli effetti già applicati prima di ripetere una mutazione.

## Controlli di accettazione

- Confronta conteggio input/output e segnala gli scarti; riapri gli export e controlla risoluzione, orientamento e profilo colore.
- Confronta campioni prima/dopo per alte luci, ombre e dominanti. Dichiara ogni controllo visivo non eseguito.
- Consegna export, ricette disponibili e rapporto delle impostazioni senza includere falsi RAW modificabili.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
lightcraft-cli commands --json
lightcraft-cli render input.jpg -o output.jpg --set light.exposure=0.5
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/lightcraft/tree/v0.8.0
- https://github.com/storytold/lightcraft/releases
