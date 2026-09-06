[English](CODEX.md) · **Italiano**

# Usare il toolkit con Codex

Il profilo Codex installa 37 skill: le 15 mantenute qui e 22 selezionate da
upstream. Repository, commit completi e percorsi sono versionati in
[`compat/codex/upstream.lock.json`](compat/codex/upstream.lock.json).

## Installazione e aggiornamento

Servono Python 3.9+ e Git; per i workflow GitHub serve anche `gh` autenticato.
Da questo checkout:

```sh
AGENT=codex scripts/wire-machine.sh --dry-run --skills
AGENT=codex scripts/wire-machine.sh --skills
AGENT=codex scripts/wire-machine.sh --check
```

Le cartelle locali vengono collegate a `~/.agents/skills/`: le modifiche nel
repository si riflettono direttamente sull'installazione. Gli upstream vengono
scaricati ai commit fissati sotto `${CODEX_HOME:-~/.codex}/toolkit/upstream/`;
sono esposte soltanto le skill selezionate. Conservare gli snapshot completi
mantiene licenze, script e riferimenti esterni alle singole cartelle. Il codice
upstream non viene eseguito durante l'installazione. Un download interrotto non
pubblica link a skill incomplete.

Lo script rifiuta di sovrascrivere cartelle o link estranei e rileva omonimi
nell'installazione legacy `$CODEX_HOME/skills`. Le riesecuzioni conservano i link
invariati e aggiornano soltanto quelli gestiti. Gli snapshot precedenti restano
disponibili: rimuoverli manualmente soltanto dopo aver verificato che nessun link
li utilizzi.

Percorsi alternativi, anche per macchine con directory in sola lettura:

```sh
python3 scripts/install-codex-skills.py --dest /percorso/.agents/skills --cache /cache/scrivibile
```

Codex supporta link simbolici e discovery locale. Nei prompt CLI/IDE si usano
`$review`, `$writing-plans`, ecc.; nelle altre interfacce il selettore delle skill.
Se il turno successivo non vede le nuove skill, riavviare Codex.
[Documentazione ufficiale](https://learn.chatgpt.com/docs/build-skills).

## Cosa comprende il profilo

| Fonte | Selezione |
|---|---|
| Questo repository | Tutte le voci in `skills/` e `forked/`; prevalgono i nostri fork |
| obra/superpowers | Le sei voci del README più `executing-plans`, `test-driven-development`, `verification-before-completion`, `receiving-code-review` |
| mattpocock/skills | Le sette voci portabili del README |
| addyosmani/agent-skills | `interview-me`, `context-engineering` |
| DietrichGebert/ponytail | `ponytail-review` e `ponytail-audit`, citata nella cheatsheet |
| blader/humanizer | `humanizer` |

`executing-plans` completa il percorso di esecuzione alternativo; TDD e verifica
del completamento sono dipendenze di `systematic-debugging`; ricevere una review
ha la sua skill complementare. I riferimenti a letture correlate non comportano
l'installazione automatica di interi framework.

`git-guardrails-claude-code` è esclusa da questo profilo: configura gli hook
`PreToolUse` di Claude e non applica protezioni a Codex. Il percorso di
installazione Claude continua a includerla. Lince e VoxCode sono applicazioni
dell'ambiente ospite: lo script non le installa né le riconfigura.

## Adattamenti mantenuti nel repository

- Istruzioni locali basate sugli strumenti effettivi dell'host: subagent Codex a
  contesto fresco, modello ereditato, widget supportati e worktree esclusivi per
  chi modifica file o esegue build.
- Riferimenti fra skill risolti per nome installato. Il prompt della review
  finale SDD si trova in `requesting-code-review`, non in una cartella sorella
  inesistente del fork.
- Doubt review senza dipendenze da directory `references/` o persona mancanti.
  Avviare Codex da Codex non prova una diversità di modello.
- Flag esistenti di invocazione esplicita conservati, con policy equivalenti
  in `agents/openai.yaml`. Restano le estensioni frontmatter di Claude: il
  validatore OpenAI stretto rifiuta quelle chiavi aggiuntive anche se YAML e
  metadati richiesti sono validi.
- [`skill-header.md`](compat/codex/skill-header.md) inserito negli entrypoint
  upstream selezionati: traduce strumenti e namespace. Sostituisce anche il
  riferimento Codex di Superpowers, evitando che le istruzioni sul tiering
  contraddicano la policy di ereditarietà. I flag upstream di invocazione
  esplicita ricevono i metadati Codex quando mancanti.
- Helper SDD con percorsi su stdout e diagnostica su stderr. Lo scaffold usa
  `git rev-parse --git-path info/exclude`, valido anche nei worktree collegati,
  ed esclude il proprio `AGENTS.local.md`.

Non vengono attivati bootstrap globali dei plugin o fork upstream omonimi.
Per aggiornare un upstream, rivedere le modifiche e cambiare il lock file;
una modifica all'adattatore genera una nuova voce di cache. Gli adattamenti
vanno fatti nei file versionati, mai modificando la cache locale.

## Strumenti companion opzionali

La scelta dipende dal progetto destinatario. Installare le skill non collega
server MCP e non crea backlog o indici di ricerca.

| Strumento | Valutazione e configurazione |
|---|---|
| [Serena](https://github.com/oraios/serena#quick-start) | Utile per Java e navigazione a simboli. Richiede il backend linguistico; seguire la guida corrente per il client Codex. `navigating-java` ha già un fallback CLI. |
| [Backlog.md](https://github.com/MrLesk/Backlog.md#mcp-integration-model-context-protocol) | Utile nei progetti con backlog inizializzato. Usabile via CLI o `backlog mcp start`; `writing-prds` supporta anche la scomposizione in Markdown. |
| [qmd](https://github.com/tobi/qmd#quick-start) | Utile con grandi raccolte Markdown. Installare `@tobilu/qmd`, scegliere le radici delle raccolte e indicizzare; la ricerca semantica scarica modelli locali. Un piccolo catalogo di skill non richiede un indice. |

Per il wiring di progetto Codex legge `.codex/config.toml` nei repository
attendibili. Integrare le tabelle dei server necessari nella configurazione del
progetto e versionarla lì; usare `cwd` o l'opzione di progetto del server per
delimitare l'ambito. Non copiare direttamente `.mcp.json` di Claude.
[Configurazione MCP ufficiale](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

## Verifiche

```sh
python3 scripts/test_codex_install.py
bash -n scripts/wire-machine.sh
git diff --check
```

I test verificano link aggiornabili, idempotenza, preservazione delle collisioni,
duplicati legacy, dry run senza scritture, scaffold nei worktree e percorsi
utilizzabili prodotti dagli helper SDD. Non sostituiscono la prova delle skill
su un progetto reale o di una connessione MCP opzionale.
