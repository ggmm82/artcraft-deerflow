---
name: artcraft-gridcraft
description: "Dati, formule, tabelle, grafici e file XLSX. Usa questa skill per lavorare con gridcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Fogli di calcolo

Specialista: `gridcraft` per `studio_delegate`; nome della skill: `artcraft-gridcraft`.
CLI: `gridcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa GridCraft per dati, formule, tabelle, grafici e XLSX. Fornisci a DeckCraft dati verificati e definizioni delle metriche quando serve una presentazione.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help gridcraft` e consulta `/opt/artcraft/reference/gridcraft/help.txt`.
3. Salva il registro reale con `craft commands gridcraft > "$ARTCRAFT_OUTPUT_DIR/work/gridcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools gridcraft --out "$ARTCRAFT_OUTPUT_DIR/work/gridcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch gridcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Inventaria fogli, intervalli, intestazioni, tipi, formule, righe nascoste e celle unite. Distingui zero, vuoto e dato mancante; registra duplicati e date ambigue prima della pulizia.
2. Mantieni importi e percentuali come numeri, date come date e unità nelle intestazioni. Usa la sintassi canonica delle funzioni/API; applica separatori italiani soltanto alla presentazione. Non convertire tutte le celle in testo.
3. Conserva dati originali in una copia o foglio dedicato. Inserisci formule con riferimenti corretti, ricalcola, controlla errori e riconcilia i totali con un calcolo indipendente. Non mascherare divisioni per zero senza spiegazione.

## Diagnosi e recupero CLI

- Se una formula restituisce un errore, verifica tipi delle celle, sintassi canonica, intervallo e ricalcolo. Non sostituire la formula con il risultato costante per far passare il controllo.
- Se un ID di documento o foglio diventa sconosciuto tra chiamate MCP, ricrea apertura, modifica e salvataggio in un unico craft batch; usa $result sul campo effettivo restituito e riapri poi il file salvato.
- Dopo un errore leggi il risultato e lo schema del solo tool coinvolto. Riparti dalla copia salvata più recente e verifica gli effetti già applicati prima di ripetere una mutazione.

## Controlli di accettazione

- Riapri XLSX e verifica fogli, tipi, formule e valori ricalcolati; esegui check e controlla celle con errori.
- Riconcilia numero righe e totali prima/dopo; per grafici controlla intervalli, etichette e unità.
- Consegna XLSX con formule e dati verificati in CSV/JSON per i colleghi, specificando separatore, periodo, unità e definizioni.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
gridcraft-cli info input.xlsx --json
gridcraft-cli commands --json
gridcraft-cli functions --json
gridcraft-cli eval "=SUM(1,2,3)"
gridcraft-cli cat input.xlsx --range A1:D20 --csv
gridcraft-cli check input.xlsx --json
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/gridcraft/tree/v0.7.0
- https://github.com/storytold/gridcraft/releases
