[English](SKILLS-CHEATSHEET.md) · **Italiano**

# CHEATSHEET DELLE SKILL — quale skill, quando

Una tabella di lookup per l'umano: senti un bisogno, trovi la skill. Il
[workflow](WORKFLOW_IT.md) racconta la storia; questa pagina è l'indice. Se due
righe sembrano andare entrambe, le "regole dei due secondi" in fondo
dirimono la questione.

## Nella pipeline (stadio per stadio)

| Quando | Skill | Il tuo ruolo |
|---|---|---|
| Arriva un'idea, una issue o una richiesta | `brainstorming` (+ `interview-me` se l'intento è poco chiaro) | rispondi alle domande; approvi il design |
| Il design va stress-testato | `grilling` | una domanda alla volta; le decisioni restano tue |
| Comprensione condivisa raggiunta | `writing-prds` | approvi la PRD prima che esista un task qualsiasi |
| PRD o piano è scritto | `plan-walkthrough` | lo giudichi al gate di stadio 3 |
| I task sono approvati | `writing-plans`, poi `subagent-driven-development` | rispondi solo ai report di deviazione |
| Un branch è finito | `adversarial-code-review` | leggi il verdetto; poi il merge — esplicitamente |

## In qualsiasi momento, su richiesta

| Stai pensando... | Skill |
|---|---|
| "Non sono sicuro di questa decisione che abbiamo appena preso" | `doubt-driven-development` |
| "Dai un'occhiata rapida a questo diff" | `review` (seconda opinione veloce, a metà lavoro) |
| "Sta per andare in merge, o tocca qualcosa di rischioso" | `adversarial-code-review` |
| "Aiutami a capire / rivedere questa PR grossa" | `pr-walkthrough` — mappa Mermaid della modifica; blast radius e rischi a colpo d'occhio |
| "Questo documento (PRD, piano, design, issue) va bene?" | `plan-walkthrough` — dossier visivo: grafo delle fasi, matrice di tracciabilità, mappa delle assunzioni |
| "Questo test fallisce / si è rotto / è diventato lento" | `systematic-debugging`, `diagnosing-bugs` |
| "Dov'è questa cosa nel codice Java? Chi la chiama?" | `navigating-java` — prima di ogni grep |
| "Quest'area di design risulta intrecciata" | `codebase-design` |
| "È over-engineered?" | `ponytail-review` (un diff), `ponytail-audit` (un repo intero) |
| "Questi task sono indipendenti — falli girare in parallelo" | `dispatching-parallel-agents` |
| "Questo lavoro richiede isolamento dal mio workspace" | `using-git-worktrees` |
| "Il branch è finito — e adesso?" | `finishing-a-development-branch` |
| "Scrivi o aggiorna i documenti per gli agenti" | `writing-for-agents` |
| "L'output dell'agente sta degradando — controlla il setup del contesto" | `context-engineering` |

## Per momento

### Inizio progetto
- Nuovo sul progetto (umano!) → `drink-from-the-firehose` — onboarding
  role-aware e quiz-driven; ogni affermazione porta la sua fonte.
- Stai preparando una nuova macchina o repo → la
  [checklist di wiring](WORKFLOW_IT.md#cablare-una-nuova-macchina-o-progetto)
  e `scripts/wire-machine.sh`.

### Giorno per giorno
- Torni dopo qualche giorno → `catch-me-up` — un report unico, il tuo lavoro
  aperto in cima.
- La sessione si chiude → `handoff` — la prossima sessione legge un documento,
  non la tua memoria.
- Una decisione ti sembra traballante mentre il lavoro è in volo →
  `doubt-driven-development`.

### Periodico
- Ogni settimana, o ogni volta che rientri → `issue-triage` — il radar: cosa è
  nuovo, cosa è cambiato, cosa serve da te.

### Decisioni che meritano di lasciare tracce
- Il design merita ADR e un glossario → `grill-with-docs` invece di
  `grilling` — stessa intervista, ma scrive mentre va.
- I termini di dominio vanno fissati → `domain-modeling`.

### Comunicazione
- Qualcosa va presentato → `slides` — sorgente markdown + deck offline.
- Una spiegazione non è passata → `wait-what` — "riproposta più semplice".
- Vuoi che sia l'agente a intervistarti → `grilling` (o `/grill-me`).

## Regole dei due secondi

- **Merge-bound o rischioso?** → `adversarial-code-review`, non `review`.
  `review` è lo strumento di tutti i giorni; il gate è il gate.
- **Documento o codice?** Documento → `plan-walkthrough`. Codice → `review` /
  `pr-walkthrough` (sopra il livello del codice) — mai nitpicking di riga a un gate.
- **Davanti a una PR grossa o un documento lungo?** Parti dalla mappa visiva
  del walkthrough (Mermaid): prima impatti e rischi, lo zoom dopo. Al ritmo
  dell'AI, la mappa è l'unica parte della review che scala.
- **Decisione già presa o no?** Non ancora presa → `doubt-driven-development`.
  Presa e costruita → la famiglia delle review.
- **Quanto è fuzzy l'idea?** Fuzzy → `brainstorming`. Idea chiara, decisioni
  contestate → `grilling`. Comprensione condivisa → `writing-prds`.
- **Java e struttura del codice?** → prima `navigating-java`, grep dopo.
  Stringhe, config, risorse? → lì il grep è lo strumento giusto.
- **Modello datato o piccolo?** Tieni comunque la pipeline — le skill sono il
  suo guardrail, non un extra opzionale.
