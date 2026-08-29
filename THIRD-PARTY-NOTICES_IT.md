[English](THIRD-PARTY-NOTICES.md) · **Italiano**

# Notice di terze parti

La directory `forked/` contiene skill derivate da repository upstream con
licenza MIT, conservate come snapshot pinnati — alcune modificate localmente. I
testi di licenza upstream sono conservati nella lingua originale (come
richiedono le licenze) nel file
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md#license-texts); questa pagina è
la mappa di derivazione in italiano. `skills/` contiene lavoro originale (si
applica la licenza MIT del repo).

## Mappa di derivazione

Verificata il 2026-08-28 facendo il diff di ogni fork contro il suo commit di
snapshot base: "byte-identical" significa nessuna differenza alcuna. Le ragioni
di ogni modifica sono descritte in [`forked/README_IT.md`](forked/README_IT.md).

| Skill | Repo upstream | Snapshot base | Modifiche locali |
|---|---|---|---|
| forked/subagent-driven-development | https://github.com/obra/superpowers | `44c9b2d` (2026-07-28, pre-v6.3.0) | aggiunta "Model Selection — always inherit" (policy del maintainer, 2026-08-27, in sostituzione del tiering dei modelli upstream; la formulazione del fix loop è stata aggiornata di conseguenza: i round 4–5 ri-dispatchano un implementer fresco con più contesto invece di un modello più capiente) e "Fast, safe test iteration (Maven projects only)" |
| forked/writing-plans | https://github.com/obra/superpowers | `44c9b2d` (2026-07-28) | aggiunte la sezione "Deviation Protocol" e un blocco "Guardrails" per task (nessuna delle due esisteva upstream) |
| forked/doubt-driven-development | https://github.com/addyosmani/agent-skills | `7829ffd` (2026-07-26) | nessuna — byte-identical allo snapshot. Upstream ha poi ristrutturato il repository; la nostra copia mantiene i path standalone-friendly `references/` (una revisione precedente di questo file attribuiva erroneamente quelle differenze di path alle nostre modifiche locali — sono drift upstream successivo) |
| forked/grilling | https://github.com/mattpocock/skills | `4128367` (2026-07-28) | sostituito il flusso delle domande: upstream mappa un "design tree" e pone l'intera "frontier" aperta come un unico round raggruppato di domande numerate; questa copia fa una domanda alla volta, ciascuna con la risposta consigliata dell'agente, e mantiene la separazione fatti-vs-decisioni |
| forked/handoff | https://github.com/mattpocock/skills | `4128367` (2026-07-28) | lo storage degli handoff è stato spostato dalla directory temporanea dell'OS a `<repo>/.reviews/handoffs/<data>-<tema>.md` (tenuto fuori dal versionamento via `.git/info/exclude`); tema derivato dall'argomento del comando o dal nome del branch; un file per handoff; un ciclo pending/`done/` la cui istruzione di pulizia viaggia dentro il documento di handoff stesso |

Le skill upstream usate non modificate non sono vendute qui; vedi il README per
la lista.
