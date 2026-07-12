# Oh-My-OpenCode — Changements appliqués

Ce document répertorie **tous les changements** apportés au code source
d'oh-my-openagent (v4.17.0, commit `58000e2`) pour résoudre les problèmes
de mort à mi-travail des subworkers (faux "All tasks completed" et sessions
qui se terminent prématurément).

## Source de base

| Champ | Valeur |
|-------|--------|
| Repo | `code-yeongyu/oh-my-openagent` |
| Version | v4.17.0 |
| Commit | `58000e2` |
| Emplacement original | `/tmp/oh-my-openagent/` |
| Copie de travail | `setup/oh-my-openagent/` |

---

## Architecture de l'exécution

Avant de comprendre les correctifs, il faut savoir quel code tourne réellement :

```
trigger_template.js (subworkers/scripts/trigger_template.js)
  → which("oh-my-opencode") → symlink global
    → ~/.bun/install/global/node_modules/oh-my-opencode/bin/oh-my-opencode.js
      → détecte darwin-arm64 → oh-my-opencode-darwin-arm64/bin/oh-my-opencode.js
        → PRIORITAIRE : bun dist/cli/index.js        (Bun binary, 103k lignes)
        → FALLBACK    : node dist/cli-node/index.js   (Node.js, seulement si bun absent)
```

**Problème découvert** : Notre premier build (`build:cli-node`) ne produisait que
`dist/cli-node/index.js` (le fallback Node), mais sur macOS, bun est disponible
et le platform binary utilise **toujours** `dist/cli/index.js` (le Bun binary).
Nos 8 correctifs n'étaient jamais chargés.

**Correction** : Il faut builder les DEUX :
- `bun run build:cli-node` → `dist/cli-node/index.js` (Node fallback)
- `bun build packages/omo-opencode/src/cli/index.ts --outdir dist/cli --target bun --format esm` → `dist/cli/index.js` (Bun binary)

---

## Correctif 1 — runner.ts : Timeout watchdog 2s → 10s

**Fichier :** `packages/omo-opencode/src/cli/run/runner.ts`

**Changement :** Ligne 23

```diff
- const EVENT_PROCESSOR_SHUTDOWN_TIMEOUT_MS = 2_000
+ const EVENT_PROCESSOR_SHUTDOWN_TIMEOUT_MS = 10_000
```

**Raison :** Le shutdown de l'event processor était limité à 2 secondes.
Quand le nombre d'événements à traiter est important (sessions longues
avec beaucoup de tool calls), 2s ne suffisait pas pour un graceful shutdown.
Le processeur d'événements était tué avant d'avoir fini de traiter le flux SSE.

---

## Correctif 2 — runner.ts : Catch silencieux → log + flag

**Fichier :** `packages/omo-opencode/src/cli/run/runner.ts`

**Changement :** Lignes 116-126

```diff
- const eventProcessor = processEvents(ctx, events.stream, eventState).catch(() => {
-   // silently ignore
- })
+ const eventProcessor = processEvents(ctx, events.stream, eventState).catch(
+   (err: unknown) => {
+     eventState.eventProcessorDied = true
+     if (options.verbose) {
+       console.error(pc.red(`[event-processor] SSE stream error: ${err instanceof Error ? err.message : String(err)}`))
+     }
+   },
+ )
```

**Raison :** Le `catch` vide avalait silencieusement toutes les erreurs du
processeur d'événements SSE. Si la connexion SSE se coupait (timeout réseau,
redémarrage du serveur opencode), l'erreur était ignorée et le système
continuait à tourner sans événements, menant à un faux "All tasks completed"
quand le watchdog ne voyait plus rien arriver.

Maintenant :
1. `eventState.eventProcessorDied = true` → signalé au poll loop
2. Log de l'erreur en mode verbose

---

## Correctif 3 — runner.ts : Logging verbose du watchdog

**Fichier :** `packages/omo-opencode/src/cli/run/runner.ts`

**Changement :** Lignes 105-107 (ajout)

```diff
+      if (options.verbose) {
+        console.log(pc.dim(`Event watchdog: ${((options as any).eventWatchdogMs ?? 30000) / 1000}s, consecutive checks: 3`))
+      }
```

**Raison :** Permet de vérifier visuellement que le watchdog est bien actif
et avec quels paramètres. Utile pour le debugging.

---

## Correctif 4 — completion.ts : Enfants de statut inconnu → NON idle

**Fichier :** `packages/omo-opencode/src/cli/run/completion.ts`

**Changement :** Ligne 112

```diff
-     if (status && status.type !== "idle") {
+     if (!status || status.type !== "idle") {
```

**Raison :** La condition originale `status && status.type !== "idle"` traitait
les enfants avec un statut `undefined`/`null`/inconnu comme étant "idle"
(parce que le `status &&` court-circuitait à `false` si status était falsy).
Cela signifie qu'un enfant dont on ne connaît pas le statut était considéré
comme terminé — une hypothèse dangereuse.

La correction inverse la logique : `!status || status.type !== "idle"` → si
le statut est inconnu OU s'il n'est pas idle, l'enfant est considéré comme
non-idle. Cela retarde la détection de complétion jusqu'à ce que tous les
enfants soient confirmés idle.

**Problème avant** : Un subagent background dont le statut n'était pas
retourné par l'API était considéré comme idle → faux "All tasks completed".

---

## Correctif 5 — completion.ts : Null fallback guard pour todos

**Fichier :** `packages/omo-opencode/src/cli/run/completion.ts`

**Changement :** Lignes 60-71

```diff
  async function areAllTodosComplete(ctx: RunContext): Promise<boolean> {
    const todosRes = await ctx.client.session.todo({ ... })
-   const todos = normalizeSDKResponse(todosRes, [] as Todo[])
+   const todos = normalizeSDKResponse(todosRes, null as Todo[] | null)
+   if (todos === null) {
+     if (ctx.verbose) {
+       console.error(pc.dim("[completion] todo API returned invalid response — cannot verify completion"))
+     }
+     return false
+   }
```

**Raison :** Anciennement, le fallback était un tableau vide `[]`. Si l'API
retournait une réponse invalide, le système considérait qu'il n'y avait
aucun todo → condition de complétion satisfaite. Avec le fallback `null`,
on détecte l'erreur API et on retourne `false` (pas complété), forçant
un nouveau poll.

---

## Correctif 6 — poll-for-completion.ts : requiredConsecutive 1 → 3

**Fichier :** `packages/omo-opencode/src/cli/run/poll-for-completion.ts`

**Changement :** Ligne 8

```diff
- const DEFAULT_REQUIRED_CONSECUTIVE = 1
+ const DEFAULT_REQUIRED_CONSECUTIVE = 3
```

**Raison :** Avec `requiredConsecutive = 1`, un seul cycle de poll où toutes
les conditions semblaient satisfaites suffisait à déclencher "All tasks
completed". Si le serveur avait un délai (typique des subagents background
qui mettent ~500ms à reporter leur statut), le premier poll pouvait
détecter à tort "tout est fini".

Avec `requiredConsecutive = 3`, le système exige que les conditions de
complétion soient vérifiées 3 fois de suite (espacées de 500ms, soit 1.5s
de stabilité) avant de déclarer la session terminée. Cela élimine les
faux positifs dus à la latence asynchrone des subagents.

---

## Correctif 7 — poll-for-completion.ts : Guard eventProcessorDied

**Fichier :** `packages/omo-opencode/src/cli/run/poll-for-completion.ts`

**Changement :** Lignes 98-102 (ajout)

```diff
+     // If the SSE event processor died (connection lost), mark session as failed
+     if (eventState.eventProcessorDied) {
+       console.error(pc.red("\n\nSSE event processor died — connection to opencode server lost."))
+       return 1
+     }
```

**Raison :** Sans ce guard, la perte de connexion SSE n'était pas détectée
par le poll loop. L'event processor tombait silencieusement, le watchdog
ne voyait plus d'événements, et après le timeout de 30s, la session était
déclarée idle → "All tasks completed" avec exit code 0.

Ce guard transforme la perte de connexion SSE en une erreur explicite avec
exit code 1, permettant aux triggers de faire un retry.

---

## Correctif 8 — event-stream-processor.ts : Filtrage par session du watchdog

**Fichier :** `packages/omo-opencode/src/cli/run/event-stream-processor.ts`

**Changement :** Lignes 53-57

```diff
-     // Only update the watchdog timestamp for events belonging to our main session
-     // Events from background subagents should NOT prevent the watchdog from firing
-     state.lastEventTimestamp = Date.now()
+       if (isMainSessionEvent(ctx, payload)) {
+         state.lastEventTimestamp = Date.now()
+       }
```

**Raison :** Le watchdog détecte l'absence d'événements pour déclencher
une vérification de session. Mais les événements des subagents background
(notifications `tui.toast.show`, `session.updated` de sessions filles,
heartbeats) maintenaient artificiellement `lastEventTimestamp` à jour,
empêchant le watchdog de se déclencher. Si la session principale était
bloquée (modèle qui répond pas, erreur silencieuse), le watchdog ne le
remarquait jamais car les subagents continuaient à émettre des événements.

La fonction `isMainSessionEvent()` (déjà présente dans le fichier) extrait
le session ID de chaque payload et ne retourne `true` que pour les événements
de la session principale (ou les événements système sans session ID).

---

## Correctif 9 — event-toast-handlers.ts : Filtrage par session ID

**Fichier :** `packages/omo-opencode/src/cli/run/event-toast-handlers.ts`

**Changement :** Lignes 10-12 (ajout)

```diff
+     // Only process toasts for our session (if a session ID is present in the event)
+     const toastSessionId = props.sessionID ?? props.sessionId
+     if (toastSessionId && toastSessionId !== ctx.sessionID) return
```

**Raison :** Les notifications toast (`tui.toast.show`) sont des événements
globaux qui peuvent provenir de n'importe quelle session. Un toast d'erreur
émis par un subagent background (ex : "API rate limit exceeded") était
intercepté par le handler et marquait `mainSessionError = true` sur la
session principale, causant une complétion avec erreur alors que la session
principale n'avait aucun problème.

Le filtre vérifie que le toast provient bien de notre session (si un
session ID est présent dans l'événement) avant de le traiter.

---

## Correctif 10 — event-state.ts : Nouveau champ eventProcessorDied

**Fichier :** `packages/omo-opencode/src/cli/run/event-state.ts`

**Changement :** Lignes 47-48 et 80

```diff
  export interface EventState {
    ...
+   /** Set to true when the SSE event processor dies (connection lost) */
+   eventProcessorDied: boolean
  }

  export function createEventState(): EventState {
    return {
      ...
+     eventProcessorDied: false,
    }
  }
```

**Raison :** Ce champ est le flag de signalisation entre l'event processor
(correctif 2) et le poll loop (correctif 7). Sans ce champ, l'event
processor ne pouvait pas communiquer la perte de connexion au poll loop.

---

## Build et déploiement

```bash
# 1. Build du Node fallback (dist/cli-node/index.js)
cd setup/oh-my-openagent
bun run build:cli-node

# 2. Build du Bun binary (dist/cli/index.js)
bun build packages/omo-opencode/src/cli/index.ts --outdir dist/cli --target bun --format esm

# 3. Remplacer les binaires dans l'install globale
cp dist/cli/index.js ~/.bun/install/global/node_modules/oh-my-opencode/dist/cli/index.js
cp dist/cli-node/index.js ~/.bun/install/global/node_modules/oh-my-opencode/dist/cli-node/index.js
```

**⚠️ Les deux builds sont nécessaires.** Le Bun binary est le chemin par défaut
sur macOS (et Linux avec bun installé). Le Node fallback sert en environnement
Node-only.

---

## Résumé des fichiers modifiés

| Fichier | Correctifs |
|---------|-----------|
| `packages/omo-opencode/src/cli/run/runner.ts` | #1 (timeout 2s→10s), #2 (catch→log+flag), #3 (verbose logging) |
| `packages/omo-opencode/src/cli/run/completion.ts` | #4 (unknown child ≠ idle), #5 (null todo guard) |
| `packages/omo-opencode/src/cli/run/poll-for-completion.ts` | #6 (requiredConsecutive 1→3), #7 (eventProcessorDied guard) |
| `packages/omo-opencode/src/cli/run/event-stream-processor.ts` | #8 (session-filtered watchdog timestamp) |
| `packages/omo-opencode/src/cli/run/event-toast-handlers.ts` | #9 (session ID filtering for toasts) |
| `packages/omo-opencode/src/cli/run/event-state.ts` | #10 (eventProcessorDied field) |

---

## Tests effectués

| Test | Résultat |
|------|----------|
| `oh-my-opencode run --attach "..."` | ✅ Exit 0, réponse complète du modèle |
| `oh-my-opencode run "..."` (standalone, trivial) | ✅ Exit 0, "FIX_VERIFIED" |
| `oh-my-opencode run -a setbon --model big-pickle "analyse..."` (full cmd, --attach) | ✅ Exit 0, analyse MirorPay complète |
| `oh-my-opencode run -a setbon --model big-pickle "analyse..."` (full cmd, standalone) | ⏱️ Exit 124 (timeout 120s), session active jusqu'au bout — pas de crash |
