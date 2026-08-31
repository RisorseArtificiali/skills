[English](README.md) · **Italiano**

Il set di skill che usiamo ogni giorno sul nostro harness di coding agent: le skill
nostre (`skills/`), le fork di skill upstream MIT che manteniamo localmente
(`forked/`) e il workflow che le concatena. Le skill sono l'unità che rende
prevedibile il *processo* di un agente — questo repo è il nostro, opinionato e
versionato.

## Fatto per progetti grandi

Questo workflow e questa collezione di skill sono nati per progetti con
**10+ contributor attivi e 50+ persone coinvolte a vario titolo**. Non per
questo sono inadatti a quelli più piccoli — ma lì potrebbero richiedere
qualche adattamento. Il nostro consiglio: provate le skill così come sono, e
adattate il workflow alle vostre esigenze di volta in volta. E un principio non
scala con la dimensione del progetto, perché non cambia mai: il ruolo di
gestire e orchestrare gli agenti è, e resta, degli umani.

## Il workflow

Per qualsiasi feature o issue non banale, la pipeline è:

1. **brainstorming** — valuta l'idea/issue e converge su un design approvato
   (modello upstream a "tre binari": spike / bounded / architectural — la
   cerimonia scala col task, il gate di approvazione mai).
   Se l'intento è poco chiaro interviene **interview-me** *(upstream)*.
2. **grilling** *(fork)* — stress-testa le decisioni una domanda alla volta
   finché non c'è comprensione condivisa.
3. **writing-prds** — PRD per fasi con criteri di accettazione falsificabili;
   scompone in task.
4. **writing-plans** *(fork)* — un piano di implementazione per task. Aggiunta
   della fork: un *Deviation Protocol* — gli esecutori si fermano e riportano
   in caso di scostamento, mai improvvisano una fix.
5. **subagent-driven-development** *(fork)* — esegue i piani task per task con
   subagent a contesto fresco. Policy della fork: *Model Selection — always
   inherit* (ogni dispatch gira sul modello della sessione; la qualità è
   garantita dal fix loop e dai gate di review, non dal tiering dei modelli) e
   una sezione dedicata all'iterazione dei test con Maven.
6. **adversarial-code-review** — gate obbligatorio prima del merge di qualsiasi
   branch: reviewer subagent a contesto fresco che attaccano da lenti diverse,
   poi i verifier che devono *riprodurre* ogni finding. I criteri di
   accettazione della PRD sono il contratto della review.

Intorno alla pipeline: **doubt-driven-development** *(fork)* per le seconde
opinioni in itinere, **review** per le review a livello a richiesta,
**plan-walkthrough** / **pr-walkthrough** per rivedere documenti/PR sopra il
livello del codice con l'umano nel loop — ognuno lascia un **dossier visivo**
(diagrammi Mermaid: architettura prima/dopo, mappa d'impatto, grafo delle fasi,
tracciabilità, assunzioni) così che impatti e rischi si *vedano*, non si
immaginino, **issue-triage** come radar delle issue, **git-guardrails-claude-code**
come rete di sicurezza sui comandi git distruttivi, **handoff** *(fork)* per
passare il lavoro tra sessioni, **catch-me-up** / **drink-from-the-firehose**
per rientrare a freddo in un progetto. Riferimenti di mestiere:
**navigating-java** (navigazione Java a livello di simbolo), **slides**
(deck reveal.js completamente locali).

### Usarlo in un progetto

Il catalogo qui sopra dice cosa esiste e come installarlo.
[**WORKFLOW_IT.md**](WORKFLOW_IT.md) dice come si usa, per l'umano che guida
gli agenti: la piramide dei ruoli (chi dirige, chi esegue, e perché il modello
più forte pianifica), i gate dove decide un umano, il ritmo quotidiano, dove
vive la conoscenza e come cablare una nuova macchina o progetto.
[**SKILLS-CHEATSHEET_IT.md**](SKILLS-CHEATSHEET_IT.md) è la risposta a colpo
d'occhio a "quale skill adesso?" — nella pipeline e in ogni altro momento della
vita di un progetto — e `scripts/wire-machine.sh` automatizza il cablaggio.

Gli agenti veri e propri girano in [**Lince**](https://lince.sh)
([RisorseArtificiali/lince](https://github.com/RisorseArtificiali/lince)):
ogni coding agent vive in una sandbox isolata, così anche con tutti i permessi
non può danneggiare la macchina, e la dashboard li guida in parallelo — ognuno
sul proprio task, nel proprio worktree. Il nostro regime di crociera è circa
cinque agenti alla volta, su uno o due progetti. Digitare è facoltativo: l'input
vocale via [**VoxCode**](https://github.com/RisorseArtificiali/voxcode)
(trascrizione Whisper completamente locale — nessun audio lascia la macchina) è
il modo in cui il contesto lungo passa dalla tua testa all'agente.

## Skill nostre (`skills/`)

| Skill | Cosa fa |
|---|---|
| adversarial-code-review | gate di review avversariale pre-merge: reviewer a contesto fresco + gate di riproducibilità |
| review | review a livello rapida di diff/branch/PR su richiesta |
| writing-prds | PRD per fasi con criteri di accettazione falsificabili, scomposta in task |
| plan-walkthrough | review logica di PRD/piani/documenti di design come dossier visivo (grafo fasi Mermaid, matrice di tracciabilità, mappa delle assunzioni), umano nel loop |
| pr-walkthrough | review logica di una PR sopra il livello del codice: mappa Mermaid prima/dopo + mappa d'impatto, blast radius a colpo d'occhio |
| issue-triage | sweep periodico delle issue GitHub con stato rolling |
| navigating-java | navigazione strutturale Java (simboli prima di grep) |
| slides | presentazione come markdown + deck reveal.js vendored |
| catch-me-up | briefing di riallineamento dopo un'assenza |
| drink-from-the-firehose | onboarding guidato e role-aware di un progetto |

## Fork (`forked/`)

Snapshot pinnati di skill upstream MIT, alcune con modifiche locali (vedi
[`THIRD-PARTY-NOTICES_IT.md`](THIRD-PARTY-NOTICES_IT.md) per fonti, versioni
base e modifiche esatte, e [`forked/README_IT.md`](forked/README_IT.md) per le
motivazioni):

| Skill | Upstream | Delta locale |
|---|---|---|
| subagent-driven-development | obra/superpowers | + policy "Model Selection — always inherit", + sezione test-iteration Maven |
| writing-plans | obra/superpowers | + sezione "Deviation Protocol", + blocco Guardrails per task |
| doubt-driven-development | addyosmani/agent-skills | nessuna — snapshot pinnato; mantiene path usabili standalone dopo una ristrutturazione upstream |
| grilling | mattpocock/skills | flusso delle domande riscritto: una domanda alla volta con risposta consigliata (upstream fa round raggruppati) |
| handoff | mattpocock/skills | storage spostato dalla temp dir dell'OS dentro il repo, un file per handoff, ciclo pending/done |

## Skill upstream usate non modificate

Non vendute qui — installate direttamente dai loro repo (tutti MIT), citate come
ringraziamento:

| Skill | Repo |
|---|---|
| interview-me, context-engineering | addyosmani/agent-skills |
| brainstorming, dispatching-parallel-agents, finishing-a-development-branch, requesting-code-review, systematic-debugging, using-git-worktrees | obra/superpowers |
| codebase-design, diagnosing-bugs, domain-modeling, grill-with-docs, grill-me, git-guardrails-claude-code, wait-what, writing-for-agents | mattpocock/skills |
| ponytail-review | DietrichGebert/ponytail |
| humanizer | blader/humanizer |

Installale (e qualsiasi cosa da questo repo) con:

```sh
npx skills add <owner>/<repo> -g -y --agent <your-agent> --skill <skill-name>
# es. da questo repo, una volta pubblico:
npx skills add maeste/skills -g -y --agent <your-agent> --skill review
```

## Server MCP companion

Tre server MCP completano il setup — nessuno è richiesto dalle skill, tutti
vale la pena citarli:

| Server | Repo | Ruolo nel workflow |
|---|---|---|
| Serena | https://github.com/oraios/serena | retrieval e editing semantico del codice — il backend che `navigating-java` guida per la navigazione a livello di simbolo |
| Backlog.md | https://github.com/MrLesk/Backlog.md | collaborazione umano/agente su progetto in git — dove atterra la scomposizione in task di `writing-prds` |
| qmd | https://github.com/tobi/qmd | mini motore di ricerca locale su markdown — indicizza i documenti, i piani e le review che la pipeline produce |

## Anche da noi

- [**Lince**](https://lince.sh) — sandbox + dashboard + hooks: la workstation
  multi-agente dentro cui gira questo toolkit
  ([RisorseArtificiali/lince](https://github.com/RisorseArtificiali/lince)).
- [**VoxCode**](https://github.com/RisorseArtificiali/voxcode) — input vocale
  per coding agent: trascrizione Whisper locale, nessun audio lascia la
  macchina; si installa con Lince.
- [**RisorseArtificiali**](https://risorseartificiali.com) — l'organizzazione
  dietro Lince e questo set di skill.
- [**maeste.it**](https://maeste.it) — il sito di Stefano Maestri.

## Licenza

MIT — vedi [`LICENSE`](LICENSE). `forked/` deriva da lavoro upstream MIT; le
loro notice sono conservate in
[`THIRD-PARTY-NOTICES_IT.md`](THIRD-PARTY-NOTICES_IT.md).
