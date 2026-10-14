# Fonti e versioni

Verifica: 14/10/2026. Le configurazioni sono state controllate sul codice, non eseguite in Docker in questo ambiente.

- DeerFlow: https://github.com/bytedance/deer-flow/tree/0bbcccfeb117a73cdeb7a8366f56ba71c25d6f5d
- Codex CLI: https://github.com/openai/codex (npm `@openai/codex@0.162.1`)
- Gemini CLI: https://github.com/google-gemini/gemini-cli (npm `@google/gemini-cli@0.64.0`)
- Autenticazione Codex: https://developers.openai.com/codex/auth/
- Autenticazione Gemini headless: `packages/core/src/code_assist/oauth2.ts`, funzione `authWithUserCode` nel repository ufficiale.
- Sandbox: immagine di questo progetto, base Node.js 22/Debian Bookworm; non usa AIO o Kubernetes.
- Catalogo: https://github.com/storytold/craft-launcher

- PhotoCraft: https://github.com/storytold/photocraft/releases/tag/v0.8.2
- VectorCraft: https://github.com/storytold/vectorcraft/releases/tag/v0.11.0
- FilmCraft: https://github.com/storytold/filmcraft/releases/tag/v0.7.2
- LightCraft: https://github.com/storytold/lightcraft/releases/tag/v0.8.0
- PdfCraft: https://github.com/storytold/pdfcraft/releases/tag/v0.8.0
- EffectCraft: https://github.com/storytold/effectcraft/releases/tag/v0.10.0
- DesignCraft: https://github.com/storytold/designcraft/releases/tag/v0.8.0
- GridCraft: https://github.com/storytold/gridcraft/releases/tag/v0.7.0
- WordCraft: https://github.com/storytold/wordcraft/releases/tag/v0.7.0
- DeckCraft: https://github.com/storytold/deckcraft/releases/tag/v0.7.0
- CADCraft: https://github.com/storytold/cadcraft/releases/tag/v0.7.0
- SoundCraft: https://github.com/storytold/soundcraft/releases/tag/v0.7.0
- FigCraft: https://github.com/storytold/figcraft/releases/tag/v0.6.0

I checksum nel lock provengono dai digest SHA-256 degli asset delle release GitHub. Il downloader ricontrolla il file prima dell’estrazione. Il pacchetto non redistribuisce i binari: vengono scaricati durante la build. Le licenze e gli avvisi upstream restano negli archivi estratti.
