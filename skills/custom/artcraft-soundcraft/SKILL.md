---
name: artcraft-soundcraft
description: "Montaggio, mix, tracce, elaborazione e bounce audio. Usa questa skill per lavorare con soundcraft-cli, ispezionare il documento, modificarlo, esportarlo e controllare il risultato."
---

# Produzione audio

Specialista: `soundcraft` per `studio_delegate`; nome della skill: `artcraft-soundcraft`.
CLI: `soundcraft-cli`. La release è fissata in `/opt/artcraft/versions.lock.json`.

## Quando usarla

Usa SoundCraft per montaggio audio, mix, tracce e bounce. Il sincronismo finale con immagini e montaggio video appartiene a FilmCraft.

## Avvio e scoperta

1. Leggi la skill comune `artcraft-workspace`.
2. Esegui `craft help soundcraft` e consulta `/opt/artcraft/reference/soundcraft/help.txt`.
3. Salva il registro reale con `craft commands soundcraft > "$ARTCRAFT_OUTPUT_DIR/work/soundcraft-commands.txt"`.
4. Cerca nel registro solo i comandi pertinenti. I parametri non sono uniformi tra applicazioni.
5. Per i tool MCP nativi usa `craft tools soundcraft --out "$ARTCRAFT_OUTPUT_DIR/work/soundcraft-tools.json"`.
   È un processo locale nella sandbox: non occorre un server sempre acceso.
6. Per una sequenza MCP con stato usa `craft batch soundcraft sequenza.json`; tutte le chiamate della sequenza condividono la stessa sessione.
   La sequenza deve includere il salvataggio del documento prima dell'uscita.

## Procedura professionale

1. Ispeziona sample rate, canali, durata e formato delle sorgenti con ffprobe. Definisci destinazione, durata, mono/stereo, loudness e picco richiesti; non presumere un target universale.
2. Organizza tracce e tagli non distruttivi, applica dissolvenze e conserva margine di livello. Evita clipping, conversioni ripetute e normalizzazione che alteri il rapporto tra tracce senza motivo.
3. Conserva progetto multitraccia e asset mantenendo i percorsi relativi: se sposti il progetto nella cartella finale, copia anche la cartella dei media collegati (per esempio `Audio Files/`). Riapri il progetto dalla posizione di consegna e risolvi ogni avviso `missing media`. Esegui un bounce breve di prova; esporta WAV master e formati compressi richiesti con parametri espliciti.

## Diagnosi e recupero CLI

- Se la riapertura segnala missing media, verifica i percorsi dalla cartella di consegna e copia le dipendenze conservandone la struttura; il bounce non sostituisce il progetto modificabile.
- Se il master clippa o supera il target, misura il file finale e correggi livelli/processamento nella sessione. Ricalcola loudness e true peak dopo ogni nuova esportazione, senza riusare le misure di un altro file.
- Dopo un errore leggi il risultato e lo schema del solo tool coinvolto. Riparti dalla copia salvata più recente e verifica gli effetti già applicati prima di ripetere una mutazione.

## Controlli di accettazione

- Con ffprobe verifica durata, sample rate, canali e codec. Controlla `ffmpeg -filters` e usa `ebur128=peak=true`, se presente, per loudness integrata e true peak sul file finale effettivo. Non equiparare picco campione e true peak e non trasferire le misure del bounce intero a un estratto. Non dichiarare assente un misuratore senza averne verificato la disponibilità.
- Controlla clipping, silenzi iniziali/finali e fade; indica separatamente ascolto reale e controlli numerici.
- Consegna progetto, mix/master ed eventuali stem; riporta target e misure senza dichiarare qualità percettiva non ascoltata.

## Sintassi di riferimento

Gli esempi seguenti indicano la sintassi; i file `input.*` devono esistere e i percorsi vanno adattati alla cartella assegnata.
Il `--help`, il registro e gli schemi della release installata restano la fonte operativa.

```bash
soundcraft-cli commands
soundcraft-cli run --demo --bounce output.wav
ffprobe -v error -show_format -show_streams -of json output.wav
ffmpeg -hide_banner -nostats -i output.wav -af ebur128=peak=true -f null -
```

## Consegna

Scrivi `handoff.json` nella cartella assegnata secondo `artcraft-workspace`: elenca sorgenti, export, anteprime e controlli con prove concrete. Per ogni limite usa `warnings`; per un controllo non eseguito usa `status: "not_run"`.
Non presentare una semplice anteprima come documento modificabile.

## Fonti

- https://github.com/storytold/soundcraft/tree/v0.7.0
- https://github.com/storytold/soundcraft/releases
