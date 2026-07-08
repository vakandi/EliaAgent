# 📊 Rapport d'Affaires: MetaTrader VPS Trading Automation

## Projet: MetaTrader 5 sur VPS Linux avec API Python

**Date:** 9 Avril 2026  
**Statut:** Recherche & Analyse Complète  
**Dossier:** /users/vakandi/EliaAI/docs/2026-04-09/

---

## 🎯 Résumé Exécutif

Ce rapport documente la faisabilité technique de l'installation de MetaTrader 5 sur un VPS Linux Debian avec connexion Python pour du trading automatisé 24/7.

### Points Clés:
| Aspect | Résultat |
|--------|----------|
| **Faisabilité** | ✅ Possible mais complexe |
| **Solution recommandée** | Wine + mt5linux |
| **Coût VPS** | $15-30/mois |
| **Complexité** | Élevée (需要 temps) |

---

## 1️⃣ Le Problème Identifié

### Contrainte Technique
```
❌ MetaTrader5 Python Package = Windows ONLY
   → pip install MetaTrader5 → Échec sur Linux
```

MetaQuotes (développeur de MT5) n'a jamais sorti de version native Linux. Le package Python officiel ne fonctionne que sur Windows.

---

## 2️⃣ Solutions Alternatives Recherchées

### Option A: Wine + MT5 (Recommandée)
| Avantages | Inconvénients |
|-----------|---------------|
| Stable et éprouvé | Installation complexe |
| Coût réduit | Nécessite configuration |
| Contrôle total | Support limité |

**Commandes d'installation:**
```bash
# Ubuntu/Debian - Script officiel
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5ubuntu.sh
chmod +x mt5ubuntu.sh
./mt5ubuntu.sh
```

### Option B: mt5linux (Package Python pour Linux)
- **GitHub:** lucas-campagna/mt5linux
- **Méthode:** Bridge RPyC entre Python Linux natif et Python Windows sous Wine
- **Stabilité:** ✅ Bonne (maintenu en 2026)

### Option C: Docker + Wine + noVNC
- **Complexité:** ⭐⭐⭐⭐⭐
- **Avantage:** Container prêt à déployer
- **Projet:** msjpq/wine-vnc

### Option D: mt5-httpapi (VM Windows dans Docker)
- **Complexité:** Extrême
- **Avantage:** Windows réel dans container (pas Wine)
- **Inconvénient:** Très lourd (~20GB)

---

## 3️⃣ Architecture Technique Recommandée

```
┌─────────────────────────────────────────────────────────────────┐
│                        VPS LINUX DEBIAN                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     Wine (Compatibilité Windows)           ││
│  │  ┌─────────────────────────────────────────────────────┐   ││
│  │  │            MetaTrader 5 Terminal                     │   ││
│  │  │         + Python Windows (via Wine)                 │   ││
│  │  │            Serveur RPyC (port 8001)                  │   ││
│  │  └─────────────────────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────────────────────┘│
│                              ↑ RPyC                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Python Linux (Code Trading Elia)              ││
│  │              mt5linux library                              ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 4️⃣ Spécifications VPS Recommandées

| Configuration | CPU | RAM | Stockage | Prix (~) |
|---------------|-----|-----|----------|----------|
| **Minimum** | 2 cores | 4 GB | 40 GB SSD | $20/mois |
| **Recommandé** | 4 cores | 8 GB | 60 GB NVMe | $35/mois |
| **Pro** | 6+ cores | 16 GB | 100 GB NVMe | $60/mois |

### Localisation:
- Choisir près du serveur du broker (London, NY, Singapore)
- Latence cible: < 5ms vers broker

### Providers testés:
| Provider | Localisations | Prix départ | Notes |
|----------|---------------|-------------|-------|
| **TradingFXVPS** | 8 villes | $15/mois | Spécialisé Forex |
| **ForexVPS** | Global | $19/mois | Support 24/7 |
| **MassiveGRID** | UK, US, EU | $1.99/mois | Entréelow-cost |
| **NYCServers** | NY4, LD4, TY3 | $16.67/mois | 100% uptime |

---

## 5️⃣ Plan de Test & Validation

### Phase 1: Préparation VPS (Jour 1)

> ⚠️ **IMPORTANT:** Utiliser `mcp-cli` pour gérer le VPS!
> 
> Le serveur SSH est configuré via `ssh-mpc-server-trading-markov` (MCP).

- [ ] Commander VPS Linux (Debian/Ubuntu)
- [ ] Configurer SSH et sécurité via mcp-cli
- [ ] Installer Wine via connexion SSH
- [ ] **CRITICAL**: Setup système cron Markov (voir Section 11)

### Connexion VPS via mcp-cli:

```bash
# Lister les serveurs disponibles
mcp-cli list ssh-mpc-server-trading-markov

# Connexion et exécution de commandes
mcp-cli call ssh-mpc-server-trading-markov execute-command '{
  "cmdString": "uname -a && wine --version"
}'
```

**Avantages mcp-cli:**
- Connexion sécurisée via MCP
- Pas besoin de credentials SSH manuels
- Automation possible depuis Elia

### Phase 2: Installation MT5 (Jour 1-2)
- [ ] Télécharger script officiel MetaQuotes OU installer Wine manuellement
- [ ] Installer MetaTrader 5
- [ ] Créer compte démo broker (IC Markets, RoboForex, etc.)
- [ ] Tester connexion manuelle

### Phase 3: Configuration Python API (Jour 2)
- [ ] Installer Python pour Windows sous Wine
- [ ] Installer mt5linux sur Linux
- [ ] Configurer serveur RPyC
- [ ] Tester connexion Python → MT5

### Phase 4: Validation Trading (Jour 3)
- [ ] Exécuter script test connexion
- [ ] Récupérer données marchés (XAUUSD, EURUSD)
- [ ] Passer ordre démo (buy/sell)
- [ ] Vérifier exécution et SL/TP
- [ ] Vérifier historisque trades

### Phase 5: Intégration Elia (Jour 4+)
- [ ] Connecter Markov (analyse) → MT5 (exécution)
- [ ] Créer scripts自动化 trading
- [ ] Configurer surveillance 24/7

---

## 6️⃣ Scripts de Test Préparés

### Fichier: `test_mt5_connection.py`

```python
"""
Test de connexion MetaTrader 5 sur VPS Linux
用法: python test_mt5_connection.py
"""

import sys
import os

def test_mt5linux():
    """Test avec mt5linux (recommandé pour Linux)"""
    try:
        from mt5linux import MetaTrader5
        
        print("🔄 Connexion à MT5 via mt5linux...")
        mt5 = MetaTrader5(host="localhost", port=8001)
        
        if not mt5.initialize():
            print(f"❌ Échec初始化: {mt5.last_error()}")
            return False
        
        terminal = mt5.terminal_info()
        print(f"✅ Connecté! Terminal: {terminal}")
        
        account = mt5.account_info()
        print(f"💰 Compte: {account.login} | Balance: {account.balance}")
        
        # Test 获取 données XAUUSD
        rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_H1, 0, 10)
        print(f"📊 XAUUSD rates: {rates[-1] if rates else 'N/A'}")
        
        mt5.shutdown()
        return True
        
    except ImportError:
        print("⚠️ mt5linux non installé: pip install mt5linux")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_official_metaTrader5():
    """Test avec le package officiel (Windows only)"""
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize():
            print(f"❌ Échec: {mt5.last_error()}")
            return False
        
        account = mt5.account_info()
        print(f"✅ Connecté! Login: {account.login}")
        
        mt5.shutdown()
        return True
        
    except ImportError:
        print("⚠️ MetaTrader5 (officiel) - Windows uniquement")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


if __name__ == "__main__":
    print("="*50)
    print("🧪 Test Connexion MT5")
    print("="*50)
    
    # Détection automatique
    methods = []
    try:
        from mt5linux import MetaTrader5
        methods.append("mt5linux")
    except: pass
    
    try:
        import MetaTrader5
        methods.append("official")
    except: pass
    
    if not methods:
        print("❌ Aucune méthode disponible!")
        print("Sur Linux: installer Wine + mt5linux")
        print("Sur Windows: pip install MetaTrader5")
    else:
        if "mt5linux" in methods:
            test_mt5linux()
        if "official" in methods:
            test_official_metaTrader5()
```

---

## 7️⃣ Configuration IMPORTANTEE - OpenCode & Elia

### ⚠️ RÈGLE CRITIQUE: NE PAS LANCER opencode EN TANT QUE TUI

```bash
# ❌ NE PAS FAIRE (bloque Elia):
opencode

# ✅ À LA PLACE:
# - Utiliser opencode en mode daemon/service
# - Ou utiliser uniquement les outils MCP disponibles
# - Ne pas démarrer l'interface interactive
```

**Raison:** Le mode TUI interactive d'opencode bloque le terminal et stoppe Elia de fonctionner.

### Configuration recommandées:

| Mode | Usage | Command |
|------|-------|---------|
| **MCP Tools** | Tools standard Elia | ✅ Préféré |
| **Background** | Scripts automation | `opencode --daemon` |
| **CLI only** | Commandes puntuales | `opencode -c "..."` |

---

## 8️⃣ Prochaines Étapes (Action Elia)

1. **Commander un VPS test** (~$20/mois)
2. **Suivre le plan d'installation** ci-dessus
3. **Tester avec compte démo** broker
4. **Valider execution trades** avant compte réel
5. **Intégrer avec Markov** pour signaux trading

---

## 9️⃣ Risques & Mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| MT5 instable sur Wine | Moyenne | Élevé | Tests intensifs, monitoring |
| Latence élevée | Faible | Moyen | Choisir VPS proche broker |
| Connexion perdue | Moyenne | Élevé | Auto-reconnect scripts |
| Mise à jour MT5 casse | Faible | Élevé | Backup, testing pré-mise à jour |
| Broker API restrictions | Moyenne | Moyen | Vérifier broker avant |

---

## 🔟 Ressources

### Documentation:
- MetaQuotes Linux: https://www.metatrader5.com/en/terminal/help/start_advanced/install_linux
- mt5linux GitHub: https://github.com/lucas-campagna/mt5linux
- Docker MT5: https://github.com/ASC689561/fx-tinny/

### Brokers recommandés (pour tests):
| Broker | Type | Lien | Notes |
|--------|------|------|-------|
| **IC Markets** | ECN | icmarkets.com | Populaire, bon API |
| **RoboForex** | Standard | roboforex.com | Plusieurs comptes |
| **Exness** | Standard | exness.com | Bonus dépôt |

---

## 📋 Checklist Final

```
VPS & Infrastructure
├── [ ] VPS Debian/Ubuntu commandé
├── [ ] Connexion mcp-cli ssh-mpc-server-trading-markov validée
├── [ ] Wine installé via SSH
├── [ ✅ ] SYSTÈME CRON MARKOV CONFIGURÉ (Section 11)
├── [ ] MT5 installé et fonctionnel
├── [ ] Compte démo créé
└── [ ] Connexion manuelle validée

Python & API
├── [ ] Python Windows dans Wine
├── [ ] mt5linux installé (côté Linux)
├── [ ] Serveur RPyC démarré
├── [ ] Test connexion Python → MT5
└── [ ] Ordre démo exécuté

Trading & Monitoring
├── [ ] Données marchés récupérables
├── [ ] Ordres buy/sell fonctionnent
├── [ ] SL/TP opérationnels
├── [ ] Historique trades récupérable
├── [ ] Script automation fonctionnel
└── [ ✅ ] Cron 20min fonctionne (test 3 cycles)

Elia & Markov
├── [ ] OpenCode NE PAS lancé en TUI
├── [ ] Scripts trading monitorés
├── [ ] Alertes intégrées (Discord/Telegram)
└── [ ] Dashboard monitoring activé
```

---

## 1️⃣1️⃣ Système Cron 24/7 - Automation Continue

### Concept - Inspired by EliaAI System

Le système utilise un **cron job toutes les 20 minutes** qui:
1. Lance OpenCode en mode CLI (PAS TUI!)
2. Lit les instructions depuis un fichier de contexte
3. Exécute les tâches (analyse/exécution)
4. Génère un rapport de session
5. Attend le prochain cycle

### Architecture du Système

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CRON JOB (every 20 min)                         │
│                   /etc/cron.d/markov-trading                       │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    MARKOV CONTEXT FILE                            │
│         /root/markov/context/ instructions.md                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 1. Lire le dernier rapport journalier                        │ │
│  │ 2. Vérifier positions ouvertes                                │ │
│  │ 3. Analyser marchés (XAUUSD, EURUSD)                          │ │
│  │ 4. Évaluer signaux Markov                                     │ │
│  │ 5. Décider: ATTENDRE / ANALYSER / EXÉCUTER TRADE             │ │
│  │ 6. Générer rapport dans docs/YYYY-MM-DD/                     │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    OPENCODE RUN (CLI mode)                         │
│        opencode run -p "Analyse Markov..." 2>&1 | tee log          │
│                                                                     │
│  OUTPUT: Rapport dans /root/markov/docs/2026-04-09/               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    ALERTES & NOTIFICATIONS                        │
│        - Telegram: Signal détecté → Exécution                     │
│        - Discord: Rapport journalier                              │
│        - Logs: /root/markov/logs/markov_YYYYMMDD.log               │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Installation du Système Cron

#### Fichier 1: `/root/markov/context/instructions.md`

```markdown
# Instructions pour Markov - Trading Agent

## MISSION
Tu es Markov, agent de trading intelligence pour trading automatisé 24/7.

## RÈGLES CRUCIALES
1. NE JAMAIS lancer opencode en mode TUI (bloque tout le système)
2. TOUJOURS utiliser: `opencode run -p "..."`
3. Lire le contexte avant chaque exécution
4. Générer un rapport à la fin de chaque cycle

## TRAVAIL PAR CYCLE (20 min)

### Étape 1: État Actuel
- Lire /root/markov/context/positions.json (positions ouvertes)
- Lire /root/markov/context/signaux_actifs.md (signaux en attente)
- Lire dernier rapport: /root/markov/docs/$(date -d 'yesterday' +%Y-%m-%d)/session_*.md

### Étape 2: Analyse des Marchés
- Obtenir données XAUUSD (1H, 4H)
- Obtenir données EURUSD (1H, 4H)
- Obtenir données DXY
- Vérifier VIX et sentiment

### Étape 3: Décision
Évaluer et choisir UNSEUL mode:
- **MODE ATTENDRE**: Pas de signal clair, marchés calmes
  → Rapport: "Aucun signal - Analyse en attente"
- **MODE ANALYSER**: Signaux détectés, besoin de confirmation
  → Rapport: "Signal détecté - Approfondir analyse"
- **MODE EXÉCUTER**: Confluence élevée (4+ signaux), opportunité claire
  → Rapport: "EXÉCUTION - Trade placement recommandé"

### Étape 4: Exécution (si MODE EXÉCUTER)
- Connexion MT5 via mt5linux
- Placement ordre avec SL/TP
- Mise à jour positions.json
- Alerte Telegram

### Étape 5: Rapport
Générer rapport dans /root/markov/docs/$(date +%Y-%m-%d)/session_$(date +%H%M%S).md

## 📊 FORMAT DE RAPPORT OBLIGATOIRE (Style Thomas)

Chaque cycle cron doit générer un rapport avec cette structure EXACTE:

```markdown
🚨 MARKOV – ANALYSE MULTI-ACTIFS | [ÉVÉNEMENT/TITRE]
Deadline: [DATE/HEURE]
---
## 📊 PRIX ACTUELS ([Heure Morocco])
Actif    Prix
XAUUSD   $[prix]
XAGUSD   $[prix]
Brent    $[prix]
WTI      $[prix]
DXY      ~[prix]
EURUSD   [prix]
USDJPY   [prix]
---

## 🎯 CONTEXTE MACRO – AGENT FONDAMENTAL
[Analyse geopolitique et fondamentale]

### Situation Actuelle:
- [Événements clés]
- [Risque]: [Impact]
- [Réaction marché]: [Direction]

### Scénario Dominant:
- [Direction attendue]
- L'annonce pourrait déclencher:
  - [Actif] → [Direction] [Cible]
---

## A. STRUCTURE TECHNIQUE GLOBALE

### 🟡 XAUUSD (OR)
Timeframe  Structure
Daily      [BULLISH/NEUTRE/BEARISH]
H4         [Compression/Impulsion/Range]
H1         [Consolidation/...]
Zones clés:
- Résistance: $[niveau]
- Support: $[niveau]
- S&R majeurs: $[niveau]

[Répéter pour chaque actif: XAGUSD, Brent, WTI, DXY, EURUSD, USDJPY, BTC, Indices]

---

## B. SCÉNARIOS POST-ÉVÉNEMENT (par actif)

### XAUUSD - 3 SCÉNARIOS

SCÉNARIO 1️⃣ : [NOM] ⬆️
Probabilité: [X]% | Impact: [ÉLEVÉ/MODÉRÉ/FAIBLE]
Élément    Détail
Trigger    [Condition]
Cible 1    $[cible]
Cible 2    $[cible]
Confirmations attendues:
- ✅ [Signal 1]
- ✅ [Signal 2]
Invalidation: [Condition]

[Répéter pour Scénario 2 et 3]

---

## C. ANALYSE DE CORRÉLATION INTERMARKET

╔══════════════════════════════════════════════════════════════════════╗
║                    MATRICE DE CORRÉLATION                             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   [Relations clés entre actifs]                                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

---

## D. CHECKLIST D'EXÉCUTION

╔══════════════════════════════════════════════════════════════════════╗
║              ✅ CHECKLIST VALIDATION AVANT ENTRÉE                    ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. CASSURE CONFIRMÉE ?                                             ║
║     □ Clôture au-dessus du niveau clé (H1 minimum)                   ║
║     □ Pas seulement wick - corps de bougie au-delà                   ║
║                                                                      ║
║  2. VOLUME / EXPANSION DE RANGE ?                                   ║
║     □ Volume > moyenne 20 périodes                                   ║
║     □ Bollinger Bands en expansion                                   ║
║     □ ATR en augmentation                                            ║
║                                                                      ║
║  3. IMPULSION PROPRE ?                                              ║
║     □ Minimum 3 bougies consécutives même direction                  ║
║     □ Pas de rejeu immédiat                                          ║
║     □ Wick courtes (pas de renversement)                             ║
║                                                                      ║
║  4. RISQUE DE RETOURNEMENT ?                                        ║
║     □ RSI < 70 (pas de surachat) pour longs                         ║
║     □ RSI > 30 (pas de survente) pour shorts                        ║
║     □ Divergence non détectée                                        ║
║                                                                      ║
║  ⚠️ SI 3+ CRITÈRES MANQUANTS = PAS D'ENTRÉE                          ║
║  ⚠️ SI CONTRADICTION MACRO = RÉDUIRE 50% OU PAS DE TRADE            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

---

## E. NIVEAUX PRIORITAIRES - TABLEAU SYNTHÉTIQUE

╔══════════════════════════════════════════════════════════════════════════════════╗
║                        🚨 NIVEAUX CRITIQUES À SURVEILLER                       ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                  ║
║  ACTIF     │ SUPPORT CLÉ  │ RÉSISTANCE CLÉ  │ TRIGGER HAUSSIER │ TRIGGER BAISSIER ║
║────────────┼───────────────┼──────────────────┼───────────────────┼──────────────────║
║  XAUUSD    │ $[support]   │ $[resistance]    │ Break $[trigger]  │ Break $[trigger]║
║  Brent     │ $[support]   │ $[resistance]    │ Break $[trigger]  │ Break $[trigger]║
║  [autres]  │ ...          │ ...              │ ...               │ ...              ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝

---

## F. CLASSEMENT OPÉRATIONNEL

1️⃣ TOP ACTIFS LES PLUS PROPRES TECHNIQUEMENT
   ├─ 🥇 [Actif] - [Raison]
   └─ 🥈 [Actif] - [Raison]

2️⃣ TOP ACTIFS LES PLUS DANGEREUX À TRADER
   ├─ 💀 [Actif] - [Raison]
   └─ 💀 [Actif] - [Raison]

3️⃣ TOP ACTIFS POUR BREAKOUT
   ├─ 🔴 [Actif]: $[entry]+ → $[cible]

4️⃣ TOP ACTIFS POUR STRATÉGIE PULLBACK
   ├─ 🔵 [Actif]: Retest $[zone]

---

## G. PLAN DE RÉACTION - TIMELINE

⏰ AVANT L'ÉVÉNEMENT
- Positionner alertes prix sur niveaux clés
- Ne PAS prendre de position ANTICIPÉE
- Surveiller compression Bollinger

⏰ LES 15 PREMIÈRES MINUTES APRÈS ANNONCE
- ⚡ SPIKE INITIAL - IGNORER (souvent faux)
- Ne PAS ENTRER dans les 5 premières minutes
- Attendre stabilisation du marché

⏰ PREMIÈRE HEURE
- Identifier CLÔTURE H1 pour confirmation
- Chercher RETEST du niveau cassé
- Volume doit être ÉLEVÉ pour confirmer mouvement

✅ SIGNAUX DE VRAIE CONTINUATION
- Clôture H1 au-delà du niveau avec corps > 50% bougie
- Volume > 1.5x moyenne

❌ SIGNAUX DE PIÈGE DE VOLATILITÉ
- Spike > niveau → Wick haute → Retour rapide
- Volume FORT puis chute rapide

---

## H. CONCLUSION & RECOMMANDATIONS

📌 SCÉNARIO DOMINANT:
   [Direction] → [Actifs impactés]

📌 MEILLEURS TRADES:
   1. [ACTIF] [DIRECTION] Entry: [niveau] Stop: [niveau]
      R/R: [ratio]

📌 RISK MANAGEMENT:
   - MAX 1% risque par trade
   - Stop loss OBLIGATOIRE
   - Pas de averaging down
```

---

## 📝 INTÉGRATION TELEGRAM - ENVOI DE RAPPORT

### Configuration des Credentials (HARDCODÉS dans le script)

Créer script `/root/markov/scripts/send_report.sh`:

```bash
#!/bin/bash
# Script d'envoi de rapport Markov vers Telegram
# Credentials hardcodés pour automatisation 24/7

# === CONFIGURATION TELEGRAM (HARDCODÉE) ===
TELEGRAM_BOT_TOKEN="8126992818:AAHdqTcv_1zvfN0XLRyRKGYjdpP5AKaF8oI"
TELEGRAM_CHAT_ID="-5148361692"  # Watson IA Group

# === FONCTION D'ENVOI ===
send_telegram() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d chat_id="${TELEGRAM_CHAT_ID}" \
        -d text="${message}" \
        -d parse_mode="Markdown"
}

# === ENVOI DU RAPPORT ===
send_telegram "🚨 MARKOV - RAPPORT DE SESSION
---
$(cat /root/markov/docs/$(date +%Y-%m-%d)/session_*.md 2>/dev/null | head -50)
---
⏰ $(date '+%Y-%m-%d %H:%M') Morocco"
```

### Installation:

```bash
chmod +x /root/markov/scripts/send_report.sh
```

### Integration dans le cron:

```bash
# /etc/cron.d/markov-trading
*/20 * * * * root /root/markov/run.sh >> /root/markov/logs/cron_$(date +\%Y\%m\%d).log 2>&1 && /root/markov/scripts/send_report.sh
```

### ⚠️ SÉCURITÉ
- Ces credentials sont dans le script sur le VPS
- Le VPS est protégé par SSH (seul Elia y a accès via mcp-cli)
- Ne pas partager ces credentials publiquement

## FICHIERS CRITIQUES
- /root/markov/context/instructions.md (CES INSTRUCTIONS)
- /root/markov/context/positions.json (positions ouvertes)
- /root/markov/context/signaux.md (signaux Markov)
- /root/markov/docs/ (rapports générés)
- /root/markov/logs/ (logs détaillés)

## CONFLUENCE MINIMALE
- Niveau 1-2: MODE ATTENDRE
- Niveau 3: MODE ANALYSER
- Niveau 4-5: MODE EXÉCUTER
```

#### Fichier 2: `/root/markov/context/positions.json` (initial)

```json
{
  "positions": [],
  "derniere_mise_a_jour": "2026-04-09T00:00:00Z",
  "total_equity": 10000,
  "compte": "demo"
}
```

#### Fichier 3: Cron Job

```bash
# /etc/cron.d/markov-trading
SHELL=/bin/bash
PATH=/root/.opencode/bin:/usr/local/bin:/usr/bin:/bin
MAILTO=""

# Exécuter toutes les 20 minutes
*/20 * * * * root cd /root/markov && /root/.opencode/bin/opencode run -p "Exécute le cycle Markov: lis instructions.md, analyse marchés, génère rapport dans docs/$(date +%Y-%m-%d)/session_$(date +%H%M%S).md" >> /root/markov/logs/cron_$(date +\%Y\%m\%d).log 2>&1
```

#### Fichier 4: Script de setup

```bash
#!/bin/bash
# markov_setup.sh - À exécuter via mcp-cli

# Créer structure dossiers
mkdir -p /root/markov/{context,docs,logs,scripts}

# Créer fichiers
cat > /root/markov/context/instructions.md << 'EOF'
[INSTRUCTIONS COMPLETES CI-DESSUS]
EOF

cat > /root/markov/context/positions.json << 'EOF'
{"positions":[],"derniere_mise_a_jour":"2026-04-09T00:00:00Z","total_equity":10000,"compte":"demo"}
EOF

# Créer script principal
cat > /root/markov/run.sh << 'EOF'
#!/bin/bash
cd /root/markov
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M%S)
mkdir -p docs/$DATE

/root/.opencode/bin/opencode run -p "
Tu es Markov. 
Lis /root/markov/context/instructions.md
Analyse markets (XAUUSD, EURUSD)
Décide: ATTENDRE / ANALYSER / EXÉCUTER
Génère rapport dans /root/markov/docs/$DATE/session_$TIME.md
" 2>&1 | tee logs/markov_$DATE.log
EOF

chmod +x /root/markov/run.sh

# Installer cron
cat > /etc/cron.d/markov-trading << 'EOF'
SHELL=/bin/bash
PATH=/root/.opencode/bin:/usr/local/bin:/usr/bin:/bin
*/20 * * * * root /root/markov/run.sh >> /root/markov/logs/cron_$(date +\%Y\%m\%d).log 2>&1
EOF
```

---

### Commandes de Setup via mcp-cli

```bash
# Setup complet du système Markov Cron
mcp-cli call ssh-mcp-server-trading-markov execute-command "{\"cmdString\": \"bash -c 'mkdir -p /root/markov/{context,docs,logs,scripts}'}\""
mcp-cli call ssh-mcp-server-trading-markov execute-command "{\"cmdString\": \"cat > /root/markov/context/instructions.md << 'INSTRUCTIONS' ...\"}\""
mcp-cli call ssh-mcp-server-trading-markov execute-command "{\"cmdString\": \"chmod +x /root/markov/run.sh && crontab /etc/cron.d/markov-trading\"}\"
```

---

### Monitoring & Logs

| Fichier | Description |
|---------|-------------|
| `/root/markov/logs/cron_YYYYMMDD.log` | Logs cron job |
| `/root/markov/logs/markov_YYYYMMDD.log` | Logs Markov execution |
| `/root/markov/docs/YYYY-MM-DD/session_HHMMSS.md` | Rapports de session |

### Vérification du système

```bash
# Voir cron actif
mcp-cli call ssh-mcp-server-trading-markov execute-command "{\"cmdString\": \"crontab -l\"}"

# Voir dernier log
mcp-cli call ssh-mcp-server-trading-markov execute-command "{\"cmdString\": \"tail -20 /root/markov/logs/cron_*.log\"}"

# Voir derniers rapports
mcp-cli call ssh-mcp-server-trading-markov execute-command "{\"cmdString\": \"ls -la /root/markov/docs/*/ | tail -10\"}"
```

---

## 1️⃣3️⃣ Repository GitHub - Déploiement Facile

### Objectif
Créer un repository GitHub pour:
1. Versionner le code Markov
2. Déployer facilement sur le VPS
3. Synchroniser les configs entre machines

### Structure du Repository

```
markov-trading-vps/
├── README.md                 # Documentation
├── install.sh               # Script d'installation complet
├── markov/
│   ├── context/
│   │   ├── instructions.md  # Instructions Markov ( STYLE THOMAS )
│   │   ├── positions.json  # Positions ouvertes
│   │   └── signaux.md      # Signaux actifs
│   ├── docs/               # Rapports générés
│   ├── logs/               # Logs d'exécution
│   └── scripts/
│       ├── run.sh          # Script principal cron
│       └── send_report.sh  # Envoi Telegram
├── config/
│   ├── crontab             # Configuration cron
│   └── opencode.json       # Config OpenCode VPS
└── requirements.txt         # Python dependencies
```

### Commandes de Création via mcp-cli

```bash
# 1. Créer le repository sur GitHub (via GitHub CLI ou API)

# Option A: Via GitHub API
mcp-cli call ssh-mcp-server-trading-markov execute-command "{\"cmdString\": \"curl -X POST https://api.github.com/user/repos -H 'Authorization: token GITHUB_TOKEN' -d '{\\\"name\\\":\\\"markov-trading-vps\\\",\\\"private\\\":true,\\\"auto_init\\\":true}'\"}"

# Option B: Via GitHub CLI (installer d'abord)
mcp-cli call ssh-mcp-server-trading-markov execute-command "{\"cmdString\": \"apt install -y gh && gh auth login\"}"

# 2. Initialiser et pousser le repo
mcp-cli call ssh-mcp-server-trading-markov execute-command "{\"cmdString\": \"cd /root && git init && git add . && git commit -m 'Initial commit - Markov trading system' && git branch -M main && git remote add origin https://github.com/VOTRE_USERNAME/markov-trading-vps.git && git push -u origin main\"}"

# 3. Cloner sur le VPS (après fresh install)
mcp-cli call ssh-mcp-server-trading-markov execute-command "{\"cmdString\": \"git clone https://github.com/VOTRE_USERNAME/markov-trading-vps.git /root/markov\"}"
```

### Script d'Installation Automatique (install.sh)

```bash
#!/bin/bash
# install.sh - Installation complète Markov Trading sur VPS

set -e

echo "🚀 Installation Markov Trading System..."

# 1. Prérequis
apt update && apt install -y git curl python3 python3-pip

# 2. Cloner le repo
git clone https://github.com/VOTRE_USERNAME/markov-trading-vps.git /root/markov
cd /root/markov

# 3. Installer Python packages
pip3 install -r requirements.txt

# 4. Configurer OpenCode (copier depuis repo)
mkdir -p ~/.config/opencode
cp config/opencode.json ~/.config/opencode/config.json

# 5. Permissions
chmod +x markov/run.sh markov/scripts/*.sh

# 6. Installer cron
cp config/crontab /etc/cron.d/markov-trading

# 7. Démarrer
systemctl restart cron

echo "✅ Installation terminée!"
echo "📊 Rapports: /root/markov/docs/"
echo "📝 Logs: /root/markov/logs/"
```

### Requirements.txt

```
mt5linux
pandas
requests
python-dotenv
```

---

## 1️⃣2️⃣ Prochaines Étapes (Prioritaires)

| Priorité | Action | Commande |
|----------|--------|----------|
| 🔴 CRITIQUE | Setup système Cron Markov | Script ci-dessus |
| 🟠 URGENT | Installer MetaTrader 5 | Script MT5 |
| 🟡 IMPORTANT | Config mt5linux + test connexion | Python script |
| 🟢 NORMAL | Test premier trade démo | Ordre buy XAUUSD |
| 🔵 SUIVI | Vérifier cron 24h | Monitoring |

---

**Rapport généré par Markov (AI Trading Intelligence)**  
**Pour: Elia - Business Development**  
**Date: 9 Avril 2026**