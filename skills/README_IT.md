[English](README.md) · **Italiano**

# Skill

Questa cartella contiene le skill che abbiamo scritto noi. Una skill è una
procedura scritta che un coding agent carica e segue: insegna all'agente come
fare un determinato lavoro, passo per passo, invece di lasciare il metodo al
caso.

Perché dovrebbe interessarti? Un agente senza un processo fisso non è coerente.
Rivede il codice in modo diverso ogni volta, dimentica passaggi, e ti dà
risposte di cui non puoi fidarti in pieno. Una skill rende il processo
ripetibile: gli stessi gate di qualità girano su ogni task, e puoi aprire il
file `SKILL.md` e leggere esattamente cosa farà l'agente.

Ogni skill vive in una sua cartella. Questa pagina descrive, per gli umani,
cosa fa ogni skill e cosa ci guadagni a usarla. Per come si concatenano in un
workflow completo, vedi il [README principale](../README_IT.md).

## Pianificare e specificare

### writing-prds

Trasforma un'idea o una issue approvata in una PRD (documento dei requisiti)
per fasi, e poi la scompone in task pronti per il backlog con criteri di
accettazione verificabili. Non scrive una PRD da un'idea grezza — le decisioni
devono già esistere (da brainstorming o da una issue discussa). Le fasi sono
ordinate per rischio, ogni fase consegna qualcosa che puoi verificare da sola,
e ogni criterio di accettazione deve essere falsificabile: dev'esserci un
controllo concreto che fallisce se il lavoro non è fatto.

**Cosa ci guadagni:** un documento di requisiti che un agente che non ti ha mai
incontrato può eseguire e rivedere. I desideri vaghi ("funziona bene", "è
robusto") vengono riscritti in comportamento osservabile prima che qualcuno
costruisca qualcosa — è questo che impedisce all'ambiguità di arrivare al
codice.

## Review

### adversarial-code-review

Il gate di review obbligatorio prima di fare il merge di un branch o di una
PR. Crea una copia isolata del repo (un worktree git), verifica che la suite
di test sia verde, poi manda un panel di subagent reviewer a contesto fresco
ad attaccare la modifica da angoli diversi: correttezza, test, sicurezza,
semplificazione e conformità alla spec. Ogni finding che producono va a uno
scettico subagent che deve riprodurlo eseguendo davvero il codice. Solo i
finding riprodotti contano come confermati.

**Cosa ci guadagni:** una review senza le due modalità di guasto classiche. Un
reviewer che condivide il contesto dell'autore tende ad approvare codice
sbagliato; un reviewer che legge soltanto produce finding che sembrano giusti
ma non si riproducono. Questa skill blocca entrambi, e il suo report è onesto
su cosa è confermato, cosa è solo plausibile e cosa non è stato coperto.

### review

La versione veloce ed everyday della review qui sopra. Uno o due subagent
reviewer a contesto fresco guardano il tuo diff corrente, un branch o una PR —
prima i bug di correttezza, poi i miglioramenti di riuso e semplificazione.
Ogni finding viene verificato prima di arrivarti, e la lista è ordinata per
gravità. I livelli controllano la profondità: low/medium ti dà pochi finding
ad alta confidenza; high allarga la rete e segna ciò che non è stato
riprodotto.

**Cosa ci guadagni:** una seconda opinione veloce da chiedere a metà lavoro,
con rumore quasi nullo. "Nessun finding" è una risposta vera — la skill non
inventa nitpick per giustificare l'esecuzione.

### plan-walkthrough

Una review logica di un *documento* — una PRD, un piano di implementazione, un
documento di design, una issue GitHub — con te nel loop. Apre un **dossier
visivo**: un grafo Mermaid di fasi e dipendenze (con un avviso su ogni fase che
fallisce il test "mergieremmo comunque ciò che viene prima?"), una matrice di
tracciabilità dai requisiti ai criteri di accettazione, e una mappa delle
assunzioni dove ogni affermazione sul codebase è marcata verificata, non
verificata o falsa. Poi ti accompagna nel documento passo per passo con
domande chiuse e triaggia i finding con te.

**Cosa ci guadagni:** i buchi di un piano emergono prima che qualcuno lo
costruisca — obiettivi poco chiari, criteri di accettazione mancanti, assunzioni
che non reggono contro il codebase reale. Correggere un piano costa minuti;
correggere il codice costruito sopra costa giorni. E il giudizio è visivo: vedi
la copertura mancante e le assunzioni false in un diagramma, non sepolte nella
prosa.

### pr-walkthrough

La stessa idea per una pull request o un branch. Produce un **dossier visivo**:
una mappa Mermaid prima/dopo dell'architettura (solo la parte toccata), una
mappa d'impatto che si irradia dalla modifica a ogni superficie interessata —
il blast radius a colpo d'occhio — e un semaforo a sette dimensioni: intento,
architettura, impatti, user experience, operazioni, documentazione, test. Poi
ti accompagna nella PR sopra il livello del codice.

**Cosa ci guadagni:** puoi davvero rivedere una PR troppo grossa o troppo
sconosciuta per essere compresa dal solo diff — come reviewer, o prima del tuo
stesso merge. Oltre la scala hello-world, impatti e rischi sono invisibili in
un diff grezzo; qui vengono disegnati. E quando l'AI rende il ritmo di
produzione così veloce che il volume di PR cresce oltre ogni lettura riga per
riga, la mappa è ciò che tiene viva la review: prima vedi dove siede il
rischio, poi zoomi solo dove conta.

## Navigare il codice

### navigating-java

Un metodo per muoversi nei codebase Java con strumenti a livello di simbolo
(trova definizione, trova chiamanti, trova implementazioni, gerarchia dei
tipi) invece della ricerca testuale — più la conoscenza della struttura dei
moduli Maven che va con esso. Elenca anche ciò che gli strumenti a simboli non
vedono (reflection, dependency injection per nome, service loader) e la ricerca
a stringhe che deve accompagnarli prima di qualunque rinomina o cancellazione.

**Cosa ci guadagni:** risposte corrette alle domande su cui grep si sbaglia in
Java, tipo "chi chiama questo metodo?" e "cosa si rompe se cambio questa
firma?". Mantiene anche piccolo il contesto dell'agente: overview a simboli
invece di file interi letti dall'inizio alla fine.

## Restare orientati

### catch-me-up

Dopo qualche giorno di assenza, raccoglie tutto ciò che è successo nel
progetto: PR, issue, release, commit sul branch principale, nuove decisioni e
documenti — più gli item assegnati a te. Ordina il materiale per importanza e
consegna un riassunto di un minuto in chat, poi una pagina HTML completa dove
ogni item linka la sua fonte.

**Cosa ci guadagni:** di nuovo nel quadro in pochi minuti, con una ricevuta per
ogni affermazione, e il tuo lavoro aperto (issue assegnate, review in stallo)
in cima.

### drink-from-the-firehose

Un walkthrough di onboarding guidato e quiz-driven di un progetto. Scansiona il
repo, costruisce un piano a capitoli (cos'è il progetto, la mappa dei moduli,
dove vivono le decisioni, come si builda e si testa, e così via), poi insegna
capitolo per capitolo. Brevi quiz verificano la comprensione, e la difficoltà si
adatta alle tue risposte. Scegli un ruolo — developer, PM, designer, user — e
fonti e profondità lo seguono.

**Cosa ci guadagni:** onboarding strutturato invece di lettura casuale, e ogni
affermazione accompagnata da un file o documento che puoi aprire da te.

### issue-triage

Uno sweep veloce e regolare delle issue GitHub di un repository. Controlla cosa
è nuovo, cambiato o appena commentato dall'ultima esecuzione (tiene un piccolo
documento di stato rolling), poi ti accompagna nelle issue una alla volta:
breve sintesi, cosa è cambiato, urgenza proposta. Legge soltanto — non chiude,
non assegna, non commenta nulla se non lo dici tu.

**Cosa ci guadagni:** un giro veloce sul backlog ogni volta che torni su un
repo, con rischio zero di azioni accidentali su GitHub.

## Comunicare

### slides

Costruisce una presentazione come coppia di artefatti: un file markdown — la
fonte di verità, con note per il relatore — e un deck reveal.js che funziona
completamente offline. Gli asset del deck sono vendored (niente CDN), e il tema
è generato da design token, così è coerente e facile da ridisegnare.

**Cosa ci guadagni:** presentazioni che puoi modificare come testo, versionare
in git e proiettare ovunque — anche senza connessione internet.
