---
name: artcraft-designcraft
description: "Brochure, pubblicazioni, layout multipagina e stampa. Usa questa skill per lavorare con designcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Impaginazione editoriale

CLI: `designcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help designcraft` e consulta `/opt/artcraft/reference/designcraft/help.txt`.
3. Salva il registro reale con `craft commands designcraft > /mnt/user-data/work/designcraft-commands.txt`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools designcraft --out /mnt/user-data/work/designcraft-tools.json`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch designcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

- Definisci formato, margini, colonne, abbondanze e stili.
- Verifica overflow del testo, immagini mancanti e font.
- Esamina tutte le pagine renderizzate; usa validate-pdf per il controllo PDF/X supportato.

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

Restituisci al coordinatore: file sorgente, export, anteprime, controlli superati, controlli non eseguiti ed eventuali perdite di compatibilità.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/designcraft/tree/v0.8.0
- https://github.com/storytold/designcraft/releases
