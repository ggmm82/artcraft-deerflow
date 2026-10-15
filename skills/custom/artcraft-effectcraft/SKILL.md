---
name: artcraft-effectcraft
description: "Composizioni, keyframe, motion graphics ed effetti video. Usa questa skill per lavorare con effectcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Animazione ed effetti

Specialista: `effectcraft` per `studio_delegate`; nome della skill: `artcraft-effectcraft`.
CLI: `effectcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa EffectCraft per composizioni, motion graphics, keyframe ed effetti. Il montaggio finale di molte clip appartiene a FilmCraft.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help effectcraft` e consulta `/opt/artcraft/reference/effectcraft/help.txt`.
3. Salva il registro reale con `craft commands effectcraft > "$ARTCRAFT_OUTPUT_DIR/work/effectcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools effectcraft --out "$ARTCRAFT_OUTPUT_DIR/work/effectcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch effectcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Definisci composizione principale, risoluzione, fps, durata e sfondo/alpha. Elenca livelli, media, font e dipendenze prima di impostare animazioni.
2. Organizza livelli e precomposizioni; imposta valori iniziali/finali, keyframe e interpolazione in unità temporali esplicite. Controlla punti di ancoraggio e trasformazioni.
3. Renderizza frame iniziale, centrale e finale e i punti di cambio prima della sequenza completa. Per loop verifica continuità; per alpha scegli un formato che lo conservi.

## Diagnosi e recupero CLI

- Se un’animazione è statica, verifica composizione esportata, livello, proprietà animata, intervallo temporale e interpolazione nello schema reale, prima di aggiungere altri keyframe.
- Se manca la trasparenza, controlla canale alpha e formato/codec effettivo; non dedurla dall’estensione. Per un loop confronta anche il raccordo tra ultimo e primo frame.
- Dopo un errore leggi il risultato e lo schema del solo tool coinvolto. Riparti dalla copia salvata più recente e verifica gli effetti già applicati prima di ripetere una mutazione.

## Controlli di accettazione

- Confronta durata e numero frame attesi con l’export; verifica fps, risoluzione e alpha tramite metadati e riapertura.
- Controlla dipendenze mancanti, bordi, testi e interpolazione sui frame campione; registra visione non eseguita.
- Consegna progetto modificabile, asset necessari ed export; indica effetti non supportati o sostituiti.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
effectcraft-cli commands
effectcraft-cli info input.ecproj
effectcraft-cli render --comp Main --out output.mp4 input.ecproj
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/effectcraft/tree/v0.10.0
- https://github.com/storytold/effectcraft/releases
