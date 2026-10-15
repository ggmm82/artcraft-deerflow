---
name: artcraft-wordcraft
description: "Documenti strutturati, stili, tabelle, DOCX e PDF. Usa questa skill per lavorare con wordcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Testi e documenti

Specialista: `wordcraft` per `studio_delegate`; nome della skill: `artcraft-wordcraft`.
CLI: `wordcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

La [ricetta CLI collaudata](references/CLI-RECIPE.md) viene inclusa automaticamente nel contesto dello specialista, insieme al percorso rapido seguente.

## Quando usarla

Usa WordCraft per relazioni, testi strutturati, tabelle e DOCX. Per impaginati editoriali con abbondanze usa DesignCraft.

## Percorso rapido verificato: relazioni brevi DOCX e PDF

Per creare da zero una relazione breve con titoli, paragrafi, elenchi e tabelle, usa **prima questo percorso**, senza esplorare tutti i comandi o ricostruire il documento con decine di operazioni MCP.
La conversione Markdown → DOCX della release 0.7.0 conserva titoli semantici e tabelle (`Heading1`, `TableGrid`), verificati con `inspect`.

1. Scrivi il contenuto completo in UTF-8 in `$ARTCRAFT_OUTPUT_DIR/work/relazione.md`. Usa titoli `#` e tabelle Markdown con riga separatrice. Mantieni dati e totale verificati, senza calcolarli di nuovo o inventare dettagli.
2. Converti con le CLI native già installate. I percorsi completi funzionano anche quando una shell di login reimposta PATH:

```bash
/usr/local/bin/wordcraft-cli convert "$ARTCRAFT_OUTPUT_DIR/work/relazione.md" "$ARTCRAFT_OUTPUT_DIR/relazione.docx"
/usr/local/bin/wordcraft-cli convert "$ARTCRAFT_OUTPUT_DIR/relazione.docx" "$ARTCRAFT_OUTPUT_DIR/relazione.pdf"
/usr/local/bin/wordcraft-cli inspect "$ARTCRAFT_OUTPUT_DIR/relazione.docx"
/usr/local/bin/pdfcraft-cli info "$ARTCRAFT_OUTPUT_DIR/relazione.pdf"
/usr/local/bin/pdfcraft-cli text "$ARTCRAFT_OUTPUT_DIR/relazione.pdf"
```

3. Verifica titolo, tabella, numeri e totale nell'ispezione e nel testo del PDF. Registra subito la consegna dei due file con i nomi finali; non perfezionare opzionalmente tutti gli stili prima di consegnare.
4. Usa il percorso di modifica sotto solo per documenti esistenti, modelli da preservare o funzionalità che Markdown non rappresenta. Non implementare client MCP manuali: per il lavoro con stato usa `craft batch`, che imposta già le radici autorizzate e gestisce la sessione.

## Scoperta per modifiche e funzioni avanzate

Usa questa sezione solo quando il percorso rapido non basta. Per una nuova relazione breve, le conversioni e i controlli sopra sono sufficienti.

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

## Diagnosi e recupero CLI

- Se il testo esiste ma l’impaginazione cambia, controlla stili, sostituzioni dei font, larghezza delle tabelle e interruzioni, distinguendo struttura DOCX e resa PDF.
- Se una conversione perde un requisito avanzato, conserva il risultato valido e passa ai tool pertinenti del registro. Non ricostruire un documento breve già valido con un client MCP improvvisato.
- Dopo un errore leggi il risultato e lo schema del solo tool coinvolto. Riparti dalla copia salvata più recente e verifica gli effetti già applicati prima di ripetere una mutazione.

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
