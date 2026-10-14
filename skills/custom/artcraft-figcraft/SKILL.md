---
name: artcraft-figcraft
description: "Layout UI, componenti, variabili, frame e prototipi. Usa questa skill per lavorare con figcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Interfacce e prototipi

Specialista: `figcraft` per `studio_delegate`; nome della skill: `artcraft-figcraft`.
CLI: `figcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa FigCraft per layout UI, componenti e prototipi. Per illustrazioni e loghi usa VectorCraft; un prototipo non equivale a un sito funzionante.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help figcraft` e consulta `/opt/artcraft/reference/figcraft/help.txt`.
3. Salva il registro reale con `craft commands figcraft > "$ARTCRAFT_OUTPUT_DIR/work/figcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools figcraft --out "$ARTCRAFT_OUTPUT_DIR/work/figcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch figcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Definisci utenti, flussi, viewport desktop/mobile e contenuti reali. Inventaria frame, componenti, variabili e asset del file esistente.
2. Crea griglia, spaziature e token coerenti; usa componenti riutilizzabili e vincoli/auto layout supportati. Prevedi stati default, hover/focus, errore, vuoto e caricamento quando pertinenti.
3. Verifica testi lunghi, adattamento ai viewport e contrasto; collega i passaggi del prototipo richiesti. Non attestare conformità di accessibilità senza controlli specifici.

## Controlli di accettazione

- Riapri il sorgente e verifica struttura di frame/componenti, variabili e collegamenti del prototipo.
- Renderizza ogni viewport e stato rilevante; controlla overflow, dimensioni dei bersagli e contrasto misurato.
- Consegna sorgente editabile e anteprime con specifiche; dichiara i limiti dell’export .fig, delle interazioni e della resa responsive.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
figcraft-cli commands --json
figcraft-cli info input.figcraft --json
figcraft-cli render input.figcraft -o preview.png --scale 2
figcraft-cli export input.figcraft -o exports --format svg
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/figcraft/tree/v0.6.0
- https://github.com/storytold/figcraft/releases
