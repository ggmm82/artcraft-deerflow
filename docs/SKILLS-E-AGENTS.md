# Skills, Agents e squadra di progetto

Verifica del 21 ottobre 2026 sul commit DeerFlow fissato dal progetto, `0bbcccfeb117a73cdeb7a8366f56ba71c25d6f5d`, e confronto della documentazione upstream corrente. Nessun aggiornamento automatico del framework o dei provider in questa integrazione.

## Dove risiedono le competenze

Il loader ufficiale `LocalSkillStorage` legge `<root>/public/<nome>/SKILL.md` e `<root>/custom/<nome>/SKILL.md`. In ArtCraft la sorgente versionata è `skills/custom`, copiata nel Gateway in `/app/skills` con `DEER_FLOW_SKILLS_PATH=/app/skills`, e nei worker in `/mnt/skills`. I riferimenti restano nel pacchetto della skill. È la collocazione prevista dal framework.

Gli **Agents** sono profili riutilizzabili dell’utente: configurazione, istruzioni/SOUL, modello e riferimenti alle skills disponibili. Il campo `AgentConfig.skills` seleziona nomi: `None` eredita quelle abilitate, `[]` le disabilita, una lista limita la selezione. Non contiene copie delle skills. Non è sufficiente inserire un file nella cartella di un Agent per registrarlo come skill globale.

La **squadra di progetto** ArtCraft compila invece ruoli temporanei, attività, criteri e competenze pertinenti. Non deve salvare ogni incarico come un nuovo Agent permanente. I worker ricevono le skills selezionate e la procedura compilata; Codex/Antigravity le scoprono anche nei rispettivi percorsi nativi, limitati al run. Provider e modello continuano a provenire dalla configurazione condivisa.

Il catalogo delle skills eseguibili dagli specialisti ArtCraft è attualmente quello distribuito e collaudato con l’immagine. Una skill esterna aggiunta dalla UI DeerFlow o selezionata in un profilo Agents non viene automaticamente installata con tutte le dipendenze nei worker ArtCraft. Il loader del coordinatore e l’installazione del runtime sono passaggi distinti: non presentarli come propagazione già implementata. Integrare una nuova procedura richiede verificarne anche risorse e comandi nel worker.

`scripts/check_skill_wiring.py` verifica nella vera immagine Gateway il loader DeerFlow, il parsing di tutte le skills e i riferimenti `AgentConfig`, senza chiamate a modelli. Questo controllo di cablaggio non certifica l’intero editor Agents o una migrazione di tutti i suoi profili.

## Skills già pronte considerate

Una skill pubblicata è una procedura, non un eseguibile universale: va verificata insieme a dipendenze, riferimenti, tool e licenza. Le integrazioni di questa PR mantengono procedure ArtCraft testate sul runtime effettivo; non installano automaticamente tutti gli script delle raccolte esterne.

| Fonte ufficiale | Utilità per ArtCraft | Compatibilità osservata e scelta |
|---|---|---|
| [Anthropic webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Esplorazione prima dell’interazione, selettori, prove browser | Apache-2.0 nel `LICENSE.txt` della skill. L’originale usa Python Playwright e helper propri; ArtCraft usa Node Playwright installato e un supervisore comune. Procedure adattate nel metodo della skill, senza dichiarare disponibili gli helper originali. |
| [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | Casi rappresentativi, valutazione e confronto di procedure | Apache-2.0 nel suo `LICENSE.txt`. Il flusso e gli script originali presumono un altro ambiente; usare il principio di valutazione con prove native e proposte di lezioni approvate singolarmente, senza auto-modificare skills di produzione. |
| [Anthropic doc-coauthoring](https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring) | Brief, struttura, revisione dal punto di vista del lettore | Procedura trasversale utile: applicare domande solo quando cambiano il risultato e verificare contenuti reali. Non imporre un workflow editoriale fisso a ogni progetto. Prima di copiare la distribuzione completa verificare la licenza specifica e tutti i riferimenti. |
| [Anthropic docx](https://github.com/anthropics/skills/tree/main/skills/docx) | Conoscenza dei formati Word e loro limiti | Il frontmatter dichiara **Proprietary**; non viene redistribuita o presentata come open source. Inoltre presuppone `docx` npm e helper differenti. WordCraft/Pandoc rimangono le capacità realmente installate. |
| [OpenAI Playwright](https://github.com/openai/skills/tree/main/skills/.curated/playwright) | Browser guidato da terminale e snapshot | Licenza Apache-2.0 nel pacchetto. L’originale usa wrapper/percorsi Codex specifici; non confonderlo con il nostro adattatore o prometterne comandi non installati. |
| [OpenAI PDF](https://github.com/openai/skills/tree/main/skills/.curated/pdf) | Distinzione fra testo estratto e revisione del layout renderizzato | L’originale presume Poppler e librerie Python come reportlab/pdfplumber/pypdf. Le procedure ArtCraft usano i renderer installati e dichiarano la revisione visiva non eseguita quando non disponibile. Non importare istruzioni con dipendenze inesistenti. |

Queste fonti integrano conoscenza di processo; non sostituiscono la scoperta delle API delle CLI realmente fissate. Per ciascuna nuova skill esterna servono versione/revisione, licenza, dipendenze effettive, ricetta eseguita, esempio rappresentativo e prova di errore. Una raccolta famosa non dimostra da sola un miglioramento nel nostro progetto.

## Conservare ciò che migliora

La lezione utile descrive una condizione generale, il metodo che ha funzionato, la prova e il beneficio osservato. Può riguardare anche un filtro, una sequenza di comandi o una modalità di salvataggio appresa nella sandbox. Non salva il fatto specifico del cliente come regola universale. Confrontare almeno un caso rappresentativo e un caso limite prima di proporla; ordinarla per impatto osservato, conservando evidenza e versione dello strumento. L’utente accetta i metodi di realizzazione. Le conoscenze tecniche si attivano con prove automatiche verificate, senza una coda di approvazione dei dettagli CLI; le note senza test restano inattive.
