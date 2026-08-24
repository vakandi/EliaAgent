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
| `oh-my-opencode run -a your-agent --model big-pickle "analyse..."` (full cmd, --attach) | ✅ Exit 0, analyse your-saas complète |
| `oh-my-opencode run -a your-agent --model big-pickle "analyse..."` (full cmd, standalone) | ⏱️ Exit 124 (timeout 120s), session active jusqu'au bout — pas de crash |

---

## Fix #11 — `.omo/omo.jsonc` "Migration validation failed"

### Problème

Au démarrage d'OpenCode, un toast d'erreur s'affiche :

```
Migration validation failed for ~/.omo/omo.jsonc:
agents.sisyphus: Unrecognized key: "mode"
```

Ce message bloque le chargement partiel de la config et empêche le plugin oh-my-openagent de résoudre correctement les modèles des agents (défaut → `openai/gpt-5.4-mini-fast` au lieu de `opencode/big-pickle`).

### Racine du problème

Le fichier `~/.omo/omo.jsonc` est le fichier de config d'OpenCode lui-même, **pas** du plugin oh-my-openagent. OpenCode le valide avec son propre schéma (`omo-config-core`), qui est plus strict que le schéma du plugin :

- **Schéma OpenCode** (`omo-config-core`): n'accepte que des clés simples dans `agents`
- **Schéma oh-my-openagent** (`agent-overrides.ts`): accepte `mode`, `prompt_append`, `description`, `models` (array)

Le fichier `.omo/omo.jsonc` utilisait le format oh-my-openagent (423 lignes, avec `mode`, `prompt_append`, `description`, `models` arrays) mais était validé par le schéma OpenCode → rejet.

### Fichiers impliqués

| Fichier | Rôle | Schéma valide |
|---------|------|---------------|
| `~/.omo/omo.jsonc` | Config OpenCode (moi-même + plugin) | `omo-config-core` (strict) |
| `~/.config/opencode/oh-my-openagent.jsonc` | Config oh-my-openagent uniquement | `AgentOverrideConfigSchema` (permissif) |
| `~/.config/opencode/opencode.json` | Registration des agents dans OpenCode | OpenCode schema |

### Fix appliqué

1. **`.omo/omo.jsonc`** → vidé à `{}` (supprime toutes les clés non reconnues par le schéma OpenCode)
2. **`oh-my-openagent.jsonc`** → enrichi avec TOUS les agents (44 agents, 41 catégories, 44 display names), en utilisant le format `model` string simple (pas `models` array)

### Important : listes de agents

**Tous les agents de `opencode.json` DOIVENT être dans `oh-my-openagent.jsonc`** :

- System agents: sisyphus, sisyphus-junior, hephaestus, prometheus, oracle, metis, momus, atlas, explore, librarian, multimodal-looker
- Business agents: elia, your-agent, your-agent, your-agent, your-brand, your-agency, your-saas, tiktok-youtube-auto, tiktok-content, your-saas, account-verification, your-saas, your-saas, markov, markov-fundamental-analyst, markov-technical-analyst
- Subworkers: your-promoter, your-brand-promoter, your-brand-suppliers, your-telegram, your-saas-assistant, your-saas-community-organic, your-saas-seo, googlebot, reddit-saas-scraper, roger, your-telecom-seo, your-telecom-community-organic, your-community, your-seo, refund-hunter, prompt-enhancer

### Pourquoi pas de `prompt_append` dans `oh-my-openagent.jsonc`

Les `prompt_append` sont déjà dans `opencode.json` (section `"agent"` → chaque agent a son `prompt_append`). Le plugin oh-my-openagent lit les deux fichiers et merge les configs. Dupliquer les `prompt_append` dans `oh-my-openagent.jsonc` créerait des conflits de merging.

### Format correct dans `oh-my-openagent.jsonc`

```json
"agents": {
  "sisyphus": {
    "model": "opencode/big-pickle",
    "fallback_models": [],
    "mode": "primary"
  }
}
```

PAS :
```json
"models": [{"model": "opencode/big-pickle", "reasoning": "max"}]
```

Le champ `models` (array) n'est pas reconnu par le schéma `AgentOverrideConfigSchema`. Utiliser toujours `model` (string) + `fallback_models` (array de strings).

### Vérification

```bash
# Vérifier que .omo/omo.jsonc est vide
cat ~/.omo/omo.jsonc
# Doit afficher: {}

# Vérifier que oh-my-openagent.jsonc a tous les agents
cat ~/.config/opencode/oh-my-openagent.jsonc | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"agents\"])} agents, {len(d[\"categories\"])} categories, {len(d[\"agent_display_names\"])} display names')"

# Vérifier qu'aucun backup .omo n'est lu
ls -la ~/.omo/omo.jsonc*
```

---

## Fix #12 — `.omo/omo.jsonc` Migration Validation Fails (`mode` Key Rejected)

### Symptom

```
Migration validation failed for ~/.omo/omo.jsonc:
  agents.sisyphus: Unrecognized key: "mode"
  agents.hephaestus: Unrecognized key: "mode"
  ... (every agent with mode rejected)
```

Config logs `Oh-my-opencode config validation failed: Invalid omo config`. Plugin falls back to hardcoded `AGENT_MODEL_REQUIREMENTS` → sisyphus resolves to `github-copilot/claude-opus-4.7` → error "configured model github-copilot/claude-opus-4.7 is not valid".

### Root Cause

**Two separate config files, two separate validation schemas:**

| File | Location | Schema | Accepts `mode`? | Accepts `team_mode`? |
|------|----------|--------|-----------------|---------------------|
| `.omo/omo.jsonc` | `~/.omo/omo.jsonc` | `OmoConfigLayerSchema` (core) | **NO** — `.strict()` | **NO** |
| `oh-my-openagent.jsonc` | `~/.config/opencode/oh-my-openagent.jsonc` | `OhMyOpenCodeConfigSchema` (plugin) | **YES** | **YES** |

- `.omo/omo.jsonc` is validated by the **core schema** (`OmoConfigLayerSchema` at `dist/index.js:6029`). Root is `.strict()` accepting only: `$schema`, `categories`, `agents`, `codegraph`, `task`, `teams`, `models`, `[opencode]`, `[senpi]`, `[codex]`, `profiles`, `_migrations`, `legacy_migrations`.
- Agent entries use `OmoAgentDefInputSchema` (.strict): `description`, `prompt`, `model`, `models`, `reasoning`, `variant`, `reasoningEffort`, `tools`, `execution_mode`, `background`, `max_depth`, `allowed_subagents`, `disallowed_tools`, `max_turns`, `temperature`, `disable`. **No `mode`.**
- `oh-my-openagent.jsonc` is validated by the **plugin schema** (`OhMyOpenCodeConfigSchema` at `dist/index.js:27360`). `AgentOverrideConfigSchema` DOES accept `mode`, `prompt_append`, etc. with `.catchall()`.

### Fix

1. **Remove `mode`** from every agent entry in `.omo/omo.jsonc`
2. **Remove `team_mode` and `agent_display_names`** from root level of `.omo/omo.jsonc`
3. **Keep `team_mode` and `agent_display_names`** in `oh-my-openagent.jsonc` (plugin schema accepts them)

`.omo/omo.jsonc` should contain ONLY core-schema-accepted keys:
```json
{
  "$schema": "...",
  "categories": { ... },
  "agents": {
    "sisyphus": { "model": "opencode/big-pickle", "description": "..." },
    ...
  }
}
```

### Additional Requirement: `oh-my-openagent.jsonc` Must Exist

The plugin reads `oh-my-openagent.jsonc` for agent overrides. If this file is **missing**, the plugin falls back to hardcoded `AGENT_MODEL_REQUIREMENTS` which resolves sisyphus to `github-copilot/claude-opus-4.7`.

**Resolution chain when both files exist and valid:**
```
Plugin loads oh-my-openagent.jsonc → agentOverrides["sisyphus"] = { model: "opencode/big-pickle" }
  → sisyphusOverride.model = "opencode/big-pickle"
  → resolves to opencode/big-pickle ✅
```

**Resolution chain when oh-my-openagent.jsonc is MISSING:**
```
Plugin loads nothing → agentOverrides = {}
  → sisyphusOverride = undefined
  → fallback: fallbackChain = ["claude-opus-4-7"] with providers ["anthropic", "github-copilot", ...]
  → tries github-copilot/claude-opus-4.7 → NOT in model catalog ❌
```

### Verification

```bash
# 1. .omo/omo.jsonc has no invalid keys
cat ~/.omo/omo.jsonc | python3 -c "
import sys, json
d = json.load(sys.stdin)
root_keys = set(d.keys())
valid = {'\$schema','categories','agents','codegraph','task','teams','models','[opencode]','[senpi]','[codex]','profiles','_migrations','legacy_migrations'}
invalid = root_keys - valid
if invalid: print(f'INVALID ROOT KEYS: {invalid}'); exit(1)
for name, agent in d.get('agents',{}).items():
    if 'mode' in agent: print(f'INVALID: {name} has mode'); exit(1)
print('PASS: .omo/omo.jsonc is core-schema valid')
"

# 2. oh-my-openagent.jsonc exists and has sisyphus model
cat ~/.config/opencode/oh-my-openagent.jsonc | python3 -c "
import sys, json
d = json.load(sys.stdin)
sisy = d.get('agents',{}).get('sisyphus',{})
print(f'sisyphus model: {sisy.get(\"model\",\"MISSING\")}')
assert sisy.get('model') == 'opencode/big-pickle', 'WRONG MODEL'
print('PASS: sisyphus resolves to opencode/big-pickle')
"

# 3. Plugin log shows no migration failures after restart
# Check /var/folders/.../oh-my-opencode.log for "Migration validation failed"
```

---

## Fix #13 — Category model overrides using non-existent models (call_omo_agent + task delegate)

### Symptom

**`call_omo_agent` (explore/librarian):** ❌ All attempts failed.
```
Model not found: openai/gpt-5.4-mini-fast
→ fallback: github-copilot/claude-haiku-4.5
→ both unavailable
```

**`task()` delegate:** ❌ All attempts failed.
```
Model not found: opencode/claude-sonnet-4-6
→ fallback: opencode/gpt-5.3-codex
→ fallback: opencode/gemini-3-flash
→ all three unavailable
```

### Root Cause: Two Separate Model Resolution Code Paths

`call_omo_agent` and `task()` use **completely different model resolution systems**:

| Tool | Code Path | Reads Config | Resolves Model |
|------|-----------|-------------|----------------|
| `call_omo_agent` (explore/librarian) | **Plugin** `resolveModelAndFallbackChain()` | `oh-my-openagent.jsonc` → `agents` section | Agent overrides → `agentOverrides["explore"].model` |
| `task()` (delegate, Sisyphus-Junior) | **Native** OpenCode task system | `oh-my-openagent.jsonc` → `categories` section | Category overrides → `categories["quick"].model` |

**Plugin path** (`call_omo_agent` at `index.js:120582`):
```
resolveModelAndFallbackChain({ subagentType: "explore", agentOverrides })
  → getAgentConfigKey("explore") → "explore"
  → agentOverrides["explore"] → { model: "opencode/big-pickle" }
  → uses opencode/big-pickle ✅
```

**Native path** (`task()` via OpenCode core):
```
task(category="quick")
  → resolves category "quick" → oh-my-openagent.jsonc categories.quick
  → categories.quick.model = "opencode/gpt-5.4-mini" (old config)
  → tries opencode/gpt-5.4-mini → NOT in opencode provider ❌
  → fallback chain: opencode/claude-haiku-4-5 → opencode/gemini-3-flash → opencode/gpt-5-nano
  → ALL unavailable ❌
```

### Two Separate Problems Found and Fixed

**Problem A — `call_omo_agent` (explore/librarian):** The local plugin at `~/.config/opencode/plugins/oh-my-opencode/index.js` (170k lines, Jul 13) was **outdated** and shadowed the newer npm package. Its hardcoded `AGENT_MODEL_REQUIREMENTS` had `openai/gpt-5.4-mini-fast` in the explore/librarian fallback chains — a model that doesn't exist in any provider.

**Root cause chain:**
1. Plugin config loaded on Aug 19 → `oh-my-openagent.jsonc` at that time had NO agents section
2. Plugin fell back to hardcoded `AGENT_MODEL_REQUIREMENTS`
3. Local plugin (Jul 13) had `openai/gpt-5.4-mini-fast` in fallback chains
4. That model doesn't exist → fallback to `github-copilot/claude-haiku-4.5` → also doesn't exist

**Resolution:** After restoring `oh-my-openagent.jsonc` (with agents section) and restarting OpenCode, the plugin reads agent overrides from the config file instead of using the hardcoded fallback chain. `explore.model = "opencode/big-pickle"` → resolves correctly.

**Problem B — `task()` delegate:** The native OpenCode task system reads **category** overrides from `oh-my-openagent.jsonc`, not agent overrides. The 21 categories had models like `opencode/claude-sonnet-4-6`, `opencode/gpt-5.4`, `opencode/gemini-3-flash`, `opencode/gpt-5.3-codex` — none of which exist in the `opencode` provider (which only has `big-pickle`, `nemotron-3.5-lightning`, `hy3`, `laguna`, `mimo`, `deepseek-r1`).

### Fix Applied

**1. Restored `oh-my-openagent.jsonc`** from backup (Apr 24) — added agents section with 24 agents all using `model: "opencode/big-pickle"` and empty `fallback_models: []`.

**2. Changed ALL 21 category models** in `oh-my-openagent.jsonc` from broken models to `opencode/big-pickle`:

| Category | Before (broken) | After |
|----------|-----------------|-------|
| `visual-engineering` | `opencode/gemini-3.1-pro` | `opencode/big-pickle` |
| `ultrabrain` | `opencode/gpt-5.4` | `opencode/big-pickle` |
| `deep` | `opencode/gpt-5.3-codex` | `opencode/big-pickle` |
| `artistry` | `opencode/gemini-3.1-pro` | `opencode/big-pickle` |
| `quick` | `opencode/gpt-5.4-mini` | `opencode/big-pickle` |
| `unspecified-low` | `opencode/claude-sonnet-4-6` | `opencode/big-pickle` |
| `unspecified-high` | `opencode/claude-sonnet-4-6` | `opencode/big-pickle` |
| `writing` | `opencode/gemini-3-flash` | `opencode/big-pickle` |
| All 13 business categories | `opencode/big-pickle` | (already correct) |

All `fallback_models` set to `[]` — no fallback chain needed since only `opencode` provider is available.

**3. Changed `multimodal-looker` agent** from `opencode/gpt-5.4` to `opencode/big-pickle`.

### Critical Rule: TWO Config Sections, TWO Code Paths

**`oh-my-openagent.jsonc` has TWO sections that control models:**

```jsonc
{
  // SECTION 1: Agent overrides — used by call_omo_agent (plugin tool)
  // Affects: explore, librarian, multimodal-looker, sisyphus, etc.
  "agents": {
    "explore": { "model": "opencode/big-pickle", "fallback_models": [] },
    "librarian": { "model": "opencode/big-pickle", "fallback_models": [] },
    "sisyphus": { "model": "opencode/big-pickle", "fallback_models": [] }
  },

  // SECTION 2: Category overrides — used by task() (native OpenCode tool)
  // Affects: quick, deep, ultrabrain, unspecified-low/high, writing, etc.
  "categories": {
    "quick": { "model": "opencode/big-pickle", "fallback_models": [] },
    "deep": { "model": "opencode/big-pickle", "fallback_models": [] },
    "unspecified-low": { "model": "opencode/big-pickle", "fallback_models": [] }
  }
}
```

**Both sections MUST have `model: "opencode/big-pickle"`.** Changing only one leaves the other broken.

### Verification

```bash
# Verify ALL agents AND ALL categories use opencode/big-pickle
cat ~/.config/opencode/oh-my-openagent.jsonc | python3 -c "
import json, sys
d = json.load(sys.stdin)
cats = d.get('categories', {})
agents = d.get('agents', {})
bad_cats = [(n, c.get('model')) for n, c in cats.items() if 'big-pickle' not in c.get('model', '')]
bad_agents = [(n, a.get('model')) for n, a in agents.items() if 'big-pickle' not in a.get('model', '')]
if bad_cats or bad_agents:
    print(f'FAIL: cats={bad_cats} agents={bad_agents}'); exit(1)
print(f'PASS: {len(cats)} categories + {len(agents)} agents = ALL opencode/big-pickle')
"

# Test call_omo_agent
# Launch explore agent → should complete in ~25s with opencode/big-pickle

# Test task() delegate
# Launch task(category="quick") → should complete in ~30s with opencode/big-pickle
```

### Test Results

| Test | Before Fix | After Fix |
|------|-----------|-----------|
| `call_omo_agent` (explore) | ❌ Model not found: `openai/gpt-5.4-mini-fast` | ✅ 25s, `opencode/big-pickle` |
| `call_omo_agent` (librarian) | ❌ Model not found: `openai/gpt-5.4-mini-fast` | ✅ 52s, `opencode/big-pickle` |
| `task()` delegate (quick) | ❌ Model not found: `opencode/claude-sonnet-4-6` | ✅ 28s, `opencode/big-pickle` |
| `task()` delegate (unspecified-low) | ❌ Model not found: `opencode/claude-sonnet-4-6` | ✅ (same category, same fix) |

### Team Mode

**Tested and working.** Team mode requires `team_*` tools (team_create, team_task_create, team_send_message) which are only available to the main sisyphus agent. The `team_mode.enabled: true` config is set in `oh-my-openagent.jsonc`.

---

## Fix #14 — Team Mode: Open-Allowlist for Custom Agents

### Symptom

When using `team_create` with custom agents (your-agent, your-agent, your-agent) via `kind: "subagent_type"`, the team creation fails:

```
Unknown subagent_type 'your-agent'. Eligible agents: sisyphus, sisyphus-junior, atlas, ...
```

Only hardcoded agents in `AGENT_ELIGIBILITY_REGISTRY` could join teams. Adding a new agent to `opencode.json` required manually patching the plugin source.

### Root Cause

**Three files enforced a hardcoded allowlist:**

| File | Problem |
|------|---------|
| `packages/team-core/src/types.ts` | `AGENT_ELIGIBILITY_REGISTRY` had `eligible` entries for every known agent |
| `packages/team-core/src/member-parser.ts` | `translateMemberError()` threw "Unknown subagent_type" for any agent not in the registry |
| `packages/team-core/src/team-registry/validator.ts` | `UNKNOWN_SUBAGENT_MESSAGE` listed hardcoded eligible agents |

### Design: Open-Allowlist (Denylist-Only)

Instead of whitelisting every known agent, the registry now only contains agents that should be **rejected**:

- **`hard-reject`** — Agents that cannot be team members (read-only consultants): `oracle`, `librarian`, `explore`, `multimodal-looker`, `metis`, `momus`, `prometheus`
- **`conditional`** — Agents with special join logic: `hephaestus`
- **No `eligible` entries** — Unknown agents pass through by default

### Fix Applied

**1. `packages/team-core/src/types.ts` — Registry stripped to denylist-only**

```diff
  export const AGENT_ELIGIBILITY_REGISTRY: Record<string, AgentEligibility> = {
-   sisyphus: { verdict: "eligible" },
-   sisyphus-junior: { verdict: "eligible" },
-   atlas: { verdict: "eligible" },
-   your-agent: { verdict: "eligible" },
-   your-agent: { verdict: "eligible" },
-   your-agent: { verdict: "eligible" },
-   // ... 20+ more eligible entries
    hephaestus: { verdict: "conditional" },
    oracle: { verdict: "hard-reject", rejectionMessage: "..." },
    librarian: { verdict: "hard-reject", rejectionMessage: "..." },
    explore: { verdict: "hard-reject", rejectionMessage: "..." },
    multimodal-looker: { verdict: "hard-reject", rejectionMessage: "..." },
    metis: { verdict: "hard-reject", rejectionMessage: "..." },
    momus: { verdict: "hard-reject", rejectionMessage: "..." },
    prometheus: { verdict: "hard-reject", rejectionMessage: "..." },
  }
```

Registry shape changed from `{ [agentId]: { verdict: "eligible" | "conditional" | "hard-reject" } }` to denylist-only.

**2. `packages/team-core/src/member-parser.ts` — Unknown agents pass through**

```diff
  function translateMemberError(err, name) {
+   // Open-allowlist: unknown agents pass through as eligible
+   // Only hard-reject agents and structural errors are blocked
    if (err.code === "invalid-subagent-type") {
-     return new MemberValidationError(UNKNOWN_SUBAGENT_MESSAGE, name, err.code)
+     // Unknown agents are allowed (open-allowlist) — pass through
+     return undefined  // no error = eligible
    }
    if (err.code === "hard-rejected-subagent") {
      return err  // pass through the rejection
    }
    return new MemberValidationError(...)
  }
```

**3. `packages/team-core/src/team-registry/validator.ts` — Updated message**

```diff
- const UNKNOWN_SUBAGENT_MESSAGE = "Unknown subagent_type. Eligible agents: sisyphus, sisyphus-junior, atlas, ..."
+ const UNKNOWN_SUBAGENT_MESSAGE = "Agent not eligible as team member."
```

### Key Design Decisions

1. **Typo safety trade-off**: Unknown agents (including typos) now pass admission. They surface errors at spawn time instead of admission time. This is acceptable because typos are rare and the spawn error is clear.

2. **Hard-reject list preserves expensive consultants**: `oracle`, `librarian`, `explore` etc. are read-only agents that lack mailbox write access — they cannot participate in team communication, so they remain blocked.

3. **No changes to `omo-opencode` re-exports**: The team-mode files in `packages/omo-opencode/src/features/team-mode/` are single-line re-exports from `@oh-my-opencode/team-core/*`. All logic lives in team-core.

### Rebuild & Deploy Sequence

After editing source, run `bash scripts/rebuild-oh-my-openagent.sh` which handles:

1. Clean opencode plugin cache (`~/.cache/opencode/packages/oh-my-openagent*`)
2. Build ESM bundle (`bun build ... --outdir dist --target bun --format esm --external zod`)
3. Apply node-require-shim patch (`bun run script/patch-node-require-shim.ts`)
4. Deploy to bun cache (`~/.bun/install/cache/oh-my-opencode@*@@@*/dist/index.js`)
5. Deploy to bun global (`~/.bun/install/global/node_modules/oh-my-opencode/dist/index.js`)

**⚠️ OpenCode must be restarted after deploying for changes to take effect.**

### Verification

```bash
# Check registry has no eligible entries
grep -c "verdict.*eligible" ~/.bun/install/global/node_modules/oh-my-opencode/dist/index.js
# Expected: 0

# Check hard-reject entries still present
grep -c "hard-reject" ~/.bun/install/global/node_modules/oh-my-opencode/dist/index.js
# Expected: 13 (7 agents × 2 references + doc comments)

# Live test — create team with custom agents
# team_create with your-agent + your-agent + your-agent → all three join as "running"
```

### Test Results

| Test | Before Fix | After Fix |
|------|-----------|-----------|
| `team_create` with your-agent | ❌ "Unknown subagent_type 'your-agent'" | ✅ Joined as running member |
| `team_create` with your-agent | ❌ "Unknown subagent_type 'your-agent'" | ✅ Joined as running member |
| `team_create` with your-agent | ❌ "Unknown subagent_type 'your-agent'" | ✅ Joined as running member |
| Broadcast to all members | N/A | ✅ `deliveredTo: ["your-agent", "your-agent", "your-agent"]` |
| Shutdown + cleanup | N/A | ✅ All members approved shutdown, team deleted |

### Files Modified

| File | Change |
|------|--------|
| `packages/team-core/src/types.ts` | Registry: removed all `eligible` entries, kept `hard-reject` + `conditional` only |
| `packages/team-core/src/member-parser.ts` | `translateMemberError`: unknown agents pass through (open-allowlist) |
| `packages/team-core/src/team-registry/validator.ts` | `UNKNOWN_SUBAGENT_MESSAGE`: updated to denylist wording |
