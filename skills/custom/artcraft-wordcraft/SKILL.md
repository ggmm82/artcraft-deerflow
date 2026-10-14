---
name: artcraft-wordcraft
description: "Documenti strutturati, stili, tabelle, DOCX e PDF. Usa questa skill per lavorare con wordcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Testi e documenti

Specialista: `wordcraft` per `studio_delegate`; nome della skill: `artcraft-wordcraft`.
CLI: `wordcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa WordCraft per relazioni, testi strutturati, tabelle e DOCX. Per impaginati editoriali con abbondanze usa DesignCraft.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help wordcraft` e consulta `/opt/artcraft/reference/wordcraft/help.txt`.
3. Salva il registro reale con `craft commands wordcraft > "$ARTCRAFT_OUTPUT_DIR/work/wordcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools wordcraft --out "$ARTCRAFT_OUTPUT_DIR/work/wordcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch wordcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Ispeziona struttura, stili, sezioni, intestazioni, note, tabelle e immagini del documento. Separa testo fornito, fonti e dati da contenuti da redigere; non inventare citazioni.
2. Usa stili semantici di titolo e corpo, elenchi e numerazione coerenti. Definisci lingua, formato pagina e margini; evita spazi ripetuti come strumento di allineamento.
3. Controlla interruzioni di pagina/sezione, intestazioni ripetute delle tabelle e didascalie. Aggiorna campi e sommario se supportati; dichiara quelli non ricalcolati.

## Controlli di accettazione

- Riapri DOCX, confronta testo e struttura con i requisiti; verifica numerazione e presenza di tutte le tabelle.
- Esporta PDF e renderizza le pagine del DOCX per individuare overflow, tabelle troncate e font sostituiti. WordCraft non riapre il PDF esportato come documento: usa `pdfcraft-cli info` e `pdfcraft-cli text` per controllare pagine e testo del PDF; non ripetere conversioni PDF→DOCX/TXT con WordCraft.
- Consegna DOCX modificabile, PDF se richiesto e anteprime; segnala perdite di compatibilità e font o campi non verificati.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
wordcraft-cli commands --json
wordcraft-cli inspect input.docx
wordcraft-cli convert input.docx output.pdf
wordcraft-cli render input.docx preview.png --page 1
pdfcraft-cli info output.pdf
pdfcraft-cli text output.pdf
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/wordcraft/tree/v0.7.0
- https://github.com/storytold/wordcraft/releases
