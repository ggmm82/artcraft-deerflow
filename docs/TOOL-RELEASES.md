# Release degli strumenti — 24 ottobre 2026

Ultime release stabili rilevate nelle fonti ufficiali; non sono inclusi canali nightly, beta o release candidate. La versione distribuita rimane fissata fino a un aggiornamento esplicito e collaudato.

| Strumento | Prima | Release fissata | Fonte |
|---|---|---|---|
| PhotoCraft | v0.8.2 | **v0.15.1** | [upstream](https://github.com/storytold/photocraft/releases/latest) |
| VectorCraft | v0.11.0 | **v0.16.0** | [upstream](https://github.com/storytold/vectorcraft/releases/latest) |
| FilmCraft | v0.7.2 | **v0.12.0** | [upstream](https://github.com/storytold/filmcraft/releases/latest) |
| LightCraft | v0.8.0 | **v0.13.0** | [upstream](https://github.com/storytold/lightcraft/releases/latest) |
| PdfCraft | v0.8.0 | **v0.13.0** | [upstream](https://github.com/storytold/pdfcraft/releases/latest) |
| EffectCraft | v0.10.0 | **v0.16.0** | [upstream](https://github.com/storytold/effectcraft/releases/latest) |
| DesignCraft | v0.8.0 | **v0.12.0** | [upstream](https://github.com/storytold/designcraft/releases/latest) |
| GridCraft | v0.7.0 | **v0.11.1** | [upstream](https://github.com/storytold/gridcraft/releases/latest) |
| WordCraft | v0.7.0 | **v0.10.0** | [upstream](https://github.com/storytold/wordcraft/releases/latest) |
| DeckCraft | v0.7.0 | **v0.10.0** | [upstream](https://github.com/storytold/deckcraft/releases/latest) |
| CADCraft | v0.7.0 | **v0.12.0** | [upstream](https://github.com/storytold/cadcraft/releases/latest) |
| SoundCraft | v0.7.0 | **v0.12.1** | [upstream](https://github.com/storytold/soundcraft/releases/latest) |
| FigCraft | v0.6.0 | **v0.10.0** | [upstream](https://github.com/storytold/figcraft/releases/latest) |
| Blender | 4.5.14 | **5.2.3** | [upstream](https://download.blender.org/release/Blender5.2/) |
| Calibre | 9.16.0 | **9.17.0** | [upstream](https://download.calibre-ebook.com/9.17.0/) |
| Playwright | 1.62.0 | **1.64.1** | [upstream](https://registry.npmjs.org/@playwright/test/-/) |
| aubio | 0.4.9 | **0.4.9** | [upstream](https://deb.debian.org/debian/pool/) |
| FluidSynth | 2.3.1 | **2.6.1** | [upstream](https://github.com/FluidSynth/fluidsynth/releases/tag/v2.6.1) |
| EPUBCheck | v5.4.0 | **v5.4.0** | [upstream](https://github.com/w3c/epubcheck/releases/latest) |
| Pandoc | 3.12.1 | **3.12.1** | [upstream](https://github.com/jgm/pandoc/releases/latest) |
| Typst | v0.15.1 | **v0.15.1** | [upstream](https://github.com/typst/typst/releases/latest) |
| FreeCAD | 0.20.2 | **1.1.4** | [upstream](https://github.com/FreeCAD/FreeCAD/releases/latest) |
| whisper.cpp | v1.9.5 | **v1.9.5** | [upstream](https://codeload.github.com/ggml-org/whisper.cpp/tar.gz/refs/tags/) |
| FFmpeg | 5.1.9 | **9.0.2** | [upstream](https://github.com/FFmpeg/FFmpeg/tree/n9.0.2) |
| Codex CLI | 0.162.1 | **0.164.0** | [release ufficiale](https://github.com/openai/codex/releases/tag/rust-v0.164.0) |
| Antigravity CLI (`agy`) | 1.4.0 | **1.4.7** | [release ufficiale](https://github.com/google-antigravity/antigravity-cli/releases/tag/1.4.7) |

## Installazione e coerenza

`versions.lock.json` è il catalogo autorevole. Il controllo del catalogo verifica anche la corrispondenza con il lock binario Antigravity e con le dipendenze Playwright. `scripts/sync_catalog.py` propaga il catalogo nel runtime; `scripts/render_capability_docs.py` aggiorna le mappe delle skills. Codex viene installato leggendo il catalogo, senza un secondo numero nel Dockerfile. Il vecchio identificatore interno `gemini` resta un alias Antigravity per le configurazioni esistenti.

Gli archivi binari sono fissati con URL, dimensione e SHA-256; per Antigravity anche SHA-512. Per Craft, FreeCAD, Codex e Antigravity i digest sono confrontati con quelli pubblicati nelle release ufficiali. Per Blender viene usato il file ufficiale dei checksum. Per Calibre, Playwright e i tar sorgente FFmpeg/FluidSynth il digest viene calcolato sul download dalla fonte indicata e fissato nel catalogo. Le dipendenze Debian usano i repository autenticati della distribuzione.

FreeCAD viene estratto dalla AppImage ufficiale senza FUSE ed eseguito con il proprio Python, non con il modulo Debian 0.20.2. FFmpeg e FluidSynth sono compilati dai tag upstream, con FFmpeg/ffprobe disponibili nel PATH e sintesi MIDI offline con SoundFont. Le risorse Whisper e SoundFont mantengono i propri pin e le licenze: non sono versioni delle CLI. Il runtime completo resta Linux amd64 per il vincolo della distribuzione Blender.

## Prove

Il collaudo della nuova Calibre ha rilevato un crash QtWebEngine nei controlli CSS con piattaforme offscreen/headless prive di contesto grafico. Anche il controllo strutturale usa ora Xvfb e OpenGL software, come le conversioni. Restano attivi i controlli nativi su CSS, link, risorse e spine, con rifiuto dei casi negativi; non viene trasformato un crash in un risultato positivo. La sandbox installa esplicitamente `libxcb-shape0`/`libxcb-sync1`; il controllo di build verifica le dipendenze del plugin Qt e riporta il nome della libreria mancante. Il flusso Calibre completo è stato riprodotto e superato anche in un container Bookworm senza rete, con 1536 MiB, 1,5 CPU, 256 processi e capability disabilitate.

Verificati localmente tutti i 13 registri Craft (7.057 ID complessivi includendo gli adattatori), i contratti CLI di Codex/Antigravity e il protocollo headless senza account. Le prove di authoring Craft comprendono apertura/esportazione e sorgenti, MIDI sintetizzato in SoundCraft e riapertura della sessione trasferita. FreeCAD 1.1.4 è stato provato con geometria parametrica, sketch vincolato, Pad, modifica quote, ricalcolo e riapertura STEP e ZIP dei sorgenti.

La CI del rilascio deve inoltre costruire l’immagine e passare smoke/MCP, confronto dei registri e tutti i 24 flussi nativi offline, compresi i casi negativi. Versione e avvio riusciti da soli non autorizzano un rilascio. Queste prove verificano compatibilità e operazioni ripetibili; non sono nuove generazioni autenticate né una garanzia di qualità estetica. I collaudi storici mantengono la versione con cui furono eseguiti.

Il Compose installabile viene pubblicato solo al termine delle verifiche, con digest delle immagini provate. L’aggiornamento non modifica automaticamente le immagini già installate su Hostinger.
