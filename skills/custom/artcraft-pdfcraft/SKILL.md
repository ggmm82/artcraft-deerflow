---
name: artcraft-pdfcraft
description: "Ispezione, estrazione, unione, moduli e trasformazioni PDF. Usa questa skill per lavorare con pdfcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Documenti PDF

CLI: `pdfcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help pdfcraft` e consulta `/opt/artcraft/reference/pdfcraft/help.txt`.
3. Salva il registro reale con `craft commands pdfcraft > /mnt/user-data/work/pdfcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools pdfcraft --out /mnt/user-data/work/pdfcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch pdfcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Rileva pagine, testo, moduli e restrizioni del documento.
- Controlla le pagine coinvolte e verifica il numero pagine dopo le modifiche.
- Non dichiarare una redazione sicura soltanto perché il testo è coperto visivamente: verifica il contenuto estratto.

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

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/pdfcraft/tree/v0.8.0
- https://github.com/storytold/pdfcraft/releases
