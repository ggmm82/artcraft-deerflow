---
name: artcraft-pdfcraft
description: "Ispezione, estrazione, unione, moduli e trasformazioni PDF. Usa questa skill per lavorare con pdfcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Documenti PDF

Specialista: `pdfcraft` per `studio_delegate`; nome della skill: `artcraft-pdfcraft`.
CLI: `pdfcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa PdfCraft per ispezione, estrazione, unione, pagine e moduli PDF. Per riscrivere un documento usa WordCraft; per impaginazione da stampa usa DesignCraft.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help pdfcraft` e consulta `/opt/artcraft/reference/pdfcraft/help.txt`.
3. Salva il registro reale con `craft commands pdfcraft > "$ARTCRAFT_OUTPUT_DIR/work/pdfcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools pdfcraft --out "$ARTCRAFT_OUTPUT_DIR/work/pdfcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch pdfcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Rileva pagine, ordine, rotazione, dimensioni, testo, moduli, allegati, restrizioni e firme. Distingui PDF testuale e scansione; non inventare testo quando serve OCR non disponibile.
2. Esegui modifiche su una copia; mantieni una mappa delle pagine prima/dopo. Per moduli distingui valori compilati e campi interattivi; avvisa se una modifica invalida firme o appiattisce campi.
3. Per oscuramenti permanenti controlla che il contenuto sia rimosso da testo e oggetti: un rettangolo nero non basta. Non attestare redazione sicura se la release o i controlli non lo consentono.

## Diagnosi e recupero CLI

- Se il testo estratto è vuoto, verifica la presenza di pagine raster prima di dichiarare il PDF privo di contenuto. Distingui estrazione e OCR.
- Per un oscuramento ricontrolla il testo estratto e gli oggetti anche dopo aver riaperto il file finale; se il dato è recuperabile, il controllo è fallito anche con anteprima nera.
- Dopo un errore leggi il risultato e lo schema del solo tool coinvolto. Riparti dalla copia salvata più recente e verifica gli effetti già applicati prima di ripetere una mutazione.

## Controlli di accettazione

- Riapri il PDF, verifica conteggio/ordine pagine e valori dei campi; estrai il testo per confrontare i contenuti attesi.
- Renderizza tutte le pagine modificate e controlla tagli, rotazioni e leggibilità.
- Consegna PDF e rapporto con pagine coinvolte, controlli, firme/moduli alterati e limiti OCR o redazione.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
pdfcraft-cli info input.pdf
pdfcraft-cli tools
pdfcraft-cli combine input.pdf appendix.pdf --out output.pdf
pdfcraft-cli text output.pdf
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/pdfcraft/tree/v0.8.0
- https://github.com/storytold/pdfcraft/releases
