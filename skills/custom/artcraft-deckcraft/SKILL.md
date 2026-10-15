---
name: artcraft-deckcraft
description: "Struttura narrativa, slide, layout, grafici e PPTX. Usa questa skill per lavorare con deckcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Presentazioni

Specialista: `deckcraft` per `studio_delegate`; nome della skill: `artcraft-deckcraft`.
CLI: `deckcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa DeckCraft per presentazioni e PPTX. Analisi numerica e riconciliazione dei dati appartengono a GridCraft; loghi e illustrazioni a VectorCraft.

## Ricetta operativa collaudata

Leggi [la ricetta CLI verificata](references/CLI-RECIPE.md), inclusa anche dal runtime. Mantieni i controlli e adatta la procedura agli input reali.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help deckcraft` e consulta `/opt/artcraft/reference/deckcraft/help.txt`.
3. Salva il registro reale con `craft commands deckcraft > "$ARTCRAFT_OUTPUT_DIR/work/deckcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools deckcraft --out "$ARTCRAFT_OUTPUT_DIR/work/deckcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch deckcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Definisci pubblico, messaggio, durata, numero indicativo di slide e formato. Prepara una scaletta con un messaggio verificabile per slide e usa solo metriche e asset forniti o controllati.
2. Imposta griglia, gerarchia tipografica e palette coerenti. Crea grafici editabili quando supportati; registra fonte, unità, periodo e denominatore. Non trasformare tutte le slide in immagini se serve PPTX modificabile.
3. Mantieni testi brevi e leggibili, allineamenti e margini regolari. Usa note per dettagli e fonti; controlla font disponibili e contrasto. Non alterare numeri per adattarli alla narrazione.

## Diagnosi e recupero CLI

- Se un grafico non è modificabile, verifica il tipo di oggetto e i dati incorporati nel file finale; una bitmap con etichette non soddisfa il requisito di grafico editabile.
- Se l’export differisce dal render sorgente, controlla font e capacità PPTX della release. Verifica tutte le slide dopo la conversione e registra gli elementi rasterizzati.
- Dopo un errore leggi il risultato e lo schema del solo tool coinvolto. Riparti dalla copia salvata più recente e verifica gli effetti già applicati prima di ripetere una mutazione.

## Controlli di accettazione

- Riapri PPTX, controlla numero e ordine slide e confronta tutti i numeri con i dati di origine.
- Renderizza tutte le slide: controlla sovrapposizioni, testi tagliati, etichette, contrasto e leggibilità alla risoluzione finale.
- Consegna sorgente, PPTX e anteprime di tutte le slide; dichiara elementi rasterizzati, font sostituiti e limiti di animazioni.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
deckcraft-cli commands
deckcraft-cli info input.pptx
deckcraft-cli render input.pptx --all preview
deckcraft-cli convert input.deckcraft output.pptx
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/deckcraft/tree/v0.7.0
- https://github.com/storytold/deckcraft/releases
