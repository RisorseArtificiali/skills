[English](README.md) · **Italiano**

# Skill forkate

Questa cartella contiene copie di skill da altri repository. Tutte sono MIT; le
fonti upstream, le versioni base e i testi di licenza sono registrati in
[`THIRD-PARTY-NOTICES_IT.md`](../THIRD-PARTY-NOTICES_IT.md).

Teniamo copie locali per due motivi:

1. **Pinning.** Congeliamo una versione che abbiamo testato. Le skill upstream
   evolvono in fretta, e a volte vengono ridisegnate del tutto. Un redesign può
   essere ottimo per il suo autore e sbagliato per noi — con una copia pinnata,
   il nostro workflow quotidiano non può cambiare da un giorno all'altro senza
   una decisione nostra.
2. **Migliorie locali.** Alcune fork portano modifiche di cui abbiamo bisogno e
   che upstream non ha: uno stile d'intervista diverso, un posto più sicuro dove
   salvare gli handoff, regole extra per i nostri build tool. Dove abbiamo
   cambiato qualcosa, questa pagina dice esattamente cosa e perché.

La tabella qui sotto è stata verificata contro upstream `main` il **2026-08-28**.

| Skill | Repo upstream | Snapshot base | Modifiche nostre | Upstream nel frattempo |
|---|---|---|---|---|
| grilling | mattpocock/skills | 2026-07-28 (`4128367`) | flusso delle domande riscritto | ha evoluto ulteriormente lo stile a batch |
| handoff | mattpocock/skills | 2026-07-28 (`4128367`) | storage e ciclo di vita ridisegnati | salva ancora nella temp dir dell'OS |
| writing-plans | obra/superpowers | 2026-07-28 (`44c9b2d`) | + Deviation Protocol, + Guardrails per task | aggiunta una riga "Spec" al template |
| subagent-driven-development | obra/superpowers | 2026-07-28 (`44c9b2d`) | + policy always-inherit sui modelli, + test iteration Maven | sviluppo attivo nel frattempo |
| doubt-driven-development | addyosmani/agent-skills | 2026-07-26 (`7829ffd`) | nessuna — snapshot esatto | repo ristrutturato; la nostra copia mantiene path standalone-friendly |

Skill che un tempo vendevamo e oggi installiamo non modificate da upstream:

- `brainstorming` (obra/superpowers) — abbiamo valutato il redesign upstream
  (il modello a "tre binari": spike / bounded / architectural) e lo abbiamo
  adottato; una volta adottato non restava alcun delta locale da giustificare
  una fork.
- `grill-me` e `git-guardrails-claude-code` (mattpocock/skills) — le nostre
  copie non avevano modifiche locali, e upstream oggi differisce solo per una
  riga di formulazione.

Vedi il README principale per la lista as-is.

## Le fork nel dettaglio

### grilling

Sottopone a stress-test un piano o una decisione intervistandoti finché te e
l'agente non avete la stessa comprensione. La nostra versione fa **una domanda
alla volta**, e per ogni domanda l'agente dichiara la sua risposta consigliata.
I fatti che si possono cercare nel repo vengono cercati, non chiesti; le
decisioni vere vanno sempre a te. Nulla viene messo in atto finché non confermi
la comprensione condivisa.

**Le nostre modifiche:** upstream mappa un "design tree" e lancia a ogni round
l'intera "frontier" di domande aperte, numerate in blocco. Abbiamo riscritto
quel flusso nella versione sequenziale descritta qui sopra.

**Perché:** più domande insieme sono difficili da gestire bene, e una risposta
di solito cambia la domanda successiva che vale la pena fare. La risposta
consigliata ti mantiene al comando: la accetti con una parola o la contesti.

### handoff

Comprime la conversazione corrente in un documento di handoff che una nuova
sessione agente può raccogliere: lo stato del lavoro, cosa è stato provato,
quali skill dovrebbe usare l'agente successivo.

**Le nostre modifiche:** upstream salva l'handoff nella directory temporanea
del sistema operativo. Noi lo salviamo dentro il repo, in
`.reviews/handoffs/<data>-<tema>.md`, tenuto fuori dal versionamento tramite
`.git/info/exclude` (mai `.gitignore`). Il tema viene dall'argomento del
comando o dal nome del branch; un file per handoff, così sessioni parallele non
si sovrascrivono. Un handoff consumato viene spostato in `handoffs/done/` — e
siccome nessuna skill gira sul lato che riceve, l'istruzione per farlo viaggia
dentro il documento stesso.

**Perché:** una temp directory può essere cancellata in qualunque momento, e
l'handoff deve sopravvivere fino alla prossima sessione — forse giorni dopo,
magari su un'altra macchina. Con il file accanto al repo, la nuova sessione lo
trova dove vive il lavoro.

### writing-plans

Trasforma un task in un piano di implementazione per un agente esecutore che
non vedrà mai questa conversazione: file esatti, snippet di codice esatti,
passi di verifica. Il piano è un ordine di lavoro per uno sconosciuto.

**Le nostre modifiche — due aggiunte al template del piano:**

- **Deviation Protocol.** Se un passo non produce il risultato atteso
  dichiarato, l'esecutore deve fermare il task e riportare — atteso vs
  osservato, e la più piccola domanda che sblocca. Niente adattare il piano,
  niente fix improvvisate, niente saltare avanti.
- **Guardrails per task.** Ogni task porta con sé verbatim le invarianti del
  repo: regole di architettura, confini dei moduli, dipendenze vietate.
  L'esecutore vede solo il proprio task, quindi le regole devono viaggiare
  dentro di esso.

**Perché:** un esecutore fresco non condivide alcun contesto con noi, quindi le
fix non pianificate sono invisibili a tutti. Un task fermato costa minuti; un
esecutore che improvvisa oltre una deviazione trasforma una piccola sorpresa in
rework.

### subagent-driven-development

Esegue un piano di implementazione task per task con subagent freschi: un
implementer scrive il codice, un task reviewer lo verifica contro il piano, un
fix loop risolve i finding, e una review finale copre l'intero branch.

**Le nostre modifiche — due policy:**

- **Model Selection — always inherit.** Ogni dispatch (implementer, reviewer,
  verifier, review finale) gira sul modello della sessione. Upstream assegnava
  modelli economici ai task "meccanici"; abbiamo rimosso quel tiering. Se un
  dispatch è troppo pesante, la risposta è un implementer fresco con più
  contesto — mai un incremento silenzioso del modello.
- **Fast, safe test iteration (solo progetti Maven).** Regole per tenere basso
  il costo per iterazione: quale plugin gira quale suffisso di test, perché
  `-DskipTests` può riportare un falso verde silenzioso sui test di
  integrazione, come eseguire un solo test di integrazione per modulo, e perché
  due build Maven non devono mai condividere lo stesso working tree.

**Perché:** nella pratica un task resta "meccanico" solo finché non succede
qualcosa di inatteso, e i modelli più economici rispondono all'inatteso
improvisando invece di fermarsi. La qualità viene dal fix loop, dal Deviation
Protocol e dai gate di review — non dal tier del modello. Le regole Maven
esistono perché un falso verde è peggiore di un fallimento: termina il loop
mentre il codice è ancora rotto.

### doubt-driven-development

Sottopone una decisione non banale a una review avversariale a contesto fresco
*mentre il lavoro è in corso* — il complemento in itinere di
adversarial-code-review, che gira alla fine.

**Le nostre modifiche:** nessuna. Questo è lo snapshot upstream esatto.

**Perché teniamo la fork:** upstream ha poi ristrutturato il proprio repository, e
la nuova versione referenzia i suoi file di supporto con path che funzionano
solo dentro quel layout. Il nostro snapshot mantiene i path relativi
standalone-friendly, così la skill resta usabile da sola, senza adottare la
struttura di directory forzata di upstream — installala ovunque e funziona.
