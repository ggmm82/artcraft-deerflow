---
name: artcraft-designcraft
description: "Brochure, pubblicazioni, layout multipagina e stampa. Usa questa skill per lavorare con designcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Impaginazione editoriale

Specialista: `designcraft` per `studio_delegate`; nome della skill: `artcraft-designcraft`.
CLI: `designcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa DesignCraft per brochure, pubblicazioni multipagina e prestampa. Per testi strutturati DOCX usa WordCraft; per manipolare un PDF esistente usa PdfCraft.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help designcraft` e consulta `/opt/artcraft/reference/designcraft/help.txt`.
3. Salva il registro reale con `craft commands designcraft > "$ARTCRAFT_OUTPUT_DIR/work/designcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools designcraft --out "$ARTCRAFT_OUTPUT_DIR/work/designcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch designcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Definisci formato finito, orientamento, margini, colonne, abbondanze e area sicura. Richiedi specifiche tipografiche quando PDF/X o profili CMYK sono vincoli di stampa.
2. Imposta pagine mastro e stili coerenti; collega immagini e testi verificati. Controlla font disponibili, risoluzione effettiva delle immagini e flusso del testo prima dell’export.
3. Risolvi overflow, righe isolate e immagini mancanti. Esporta separatamente PDF per schermo e stampa se richiesti, mantenendo il sorgente e le dipendenze.

## Diagnosi e recupero CLI

- Se un export taglia il testo, controlla overflow, font sostituiti, cornici e concatenamento delle pagine; ridurre tutto il corpo non è una correzione automatica accettabile.
- Se validate-pdf rifiuta il documento, conserva il rapporto e correggi il requisito specifico. Non cambiare il nome del file o la sola estensione per dichiarare PDF/X.
- Dopo un errore leggi il risultato e lo schema del solo tool coinvolto. Riparti dalla copia salvata più recente e verifica gli effetti già applicati prima di ripetere una mutazione.

## Controlli di accettazione

- Renderizza tutte le pagine e controlla margini, allineamenti, numerazione e testo tagliato.
- Esegui validate-pdf per il profilo PDF/X supportato e registra il risultato reale: un PDF apribile non dimostra conformità PDF/X.
- Consegna sorgente, PDF e rapporto di prestampa con font, abbondanze, immagini e limiti colore.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
designcraft-cli commands
designcraft-cli run --in input.designcraft --all-pages preview
designcraft-cli run --in input.designcraft --export output.pdf
designcraft-cli validate-pdf output.pdf
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/designcraft/tree/v0.8.0
- https://github.com/storytold/designcraft/releases
