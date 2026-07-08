# 📘 GUIDE MASTER - PICASSO Agent
## L'Agent IA Premium pour Frontend E-commerce

> **[[../../wiki/skills/Git-Version-Control|Version]]:** 3.0 (Master - Avril 2026)  
> **Pour:** Client débutant dans le [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] du frontend premium  
> **Objectif:** Transformer un novice en expert PICASSO

---

## 🎯 INTRODUCTION - QU'EST-CE QUE PICASSO ?

PICASSO est un **agent IA spécialisé en développement frontend premium** créé pour [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]. Il combine:

- 🎨 **Design haut de gamme** - React, TypeScript, Tailwind, Framer Motion
- 💰 **Mentalité [[../../wiki/businesses/B2LUXE-BUSINESS|Business]]** - conversion, trust, UX, rentabilité
- ⚡ **Autonomie complète** - setup, config, implémentation A à Z

### Philosophie de PICASSO

```
"Fait beau, inspire confiance et convertit"
```

PICASSO ne fait jamais de compromis entre beauté et performance. Il DELIVRE LES DEUX.

---

## 🧠 POURQUOI UTILISER PICASSO ?

### Les 3 questions magiques de PICASSO

| Question | Pourquoi c'est [[../../wiki/concepts/Prompt-Engineering|IMPORTANT]] |
|----------|--------------------------|
| "Does this feel premium?" | Le visuel crée la première impression |
| "Does this inspire trust?" | La confiance vend le produit |
| "Does this push the [[../../wiki/people/Elia|User]] to act?" | L'action génère le revenu |

### Le Système de Priorités

| Priority | Focus | Raison |
|----------|-------|--------|
| **1. CONVERSION** | Est-ce que ça pousse l'utilisateur à agir ? | Survie du [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] |
| **2. UX CLARITY** | Est-ce que l'utilisateur comprend ? | Élimine la confusion |
| **3. DESIGN AESTHETICS** | C'est beau ? | Confiance et désir |

---

## 🛠️ INSTALLATION - COMMENT DÉBUTER

### Prérequis

```bash
# Node.js ([[../../wiki/skills/Git-Version-Control|Version]] 18+)
node --[[../../wiki/skills/Git-Version-Control|Version]]

# npm ou pnpm
npm --[[../../wiki/skills/Git-Version-Control|Version]]
# ou
pnpm --[[../../wiki/skills/Git-Version-Control|Version]]
```

### Étape 1: Structure des dossiers

Créez la structure suivante sur votre machine:

```bash
mkdir -p ~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/
mkdir -p ~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/agents/
mkdir -p ~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/[[../../wiki/skills/Index|SKILLS]]/
```

### Étape 2: Installer les fichiers PICASSO

Copiez les fichiers présents dans ce dossier:

```
~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/
├── agents/
│   └── picasso.md          # Agent principal (~2000 lignes)
├── [[../../wiki/skills/Index|SKILLS]]/
│   ├── framer-motion-patterns.md
│   ├── tailwind-mastery.md
│   ├── premium-component-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Python-Scripting|Python]]-Scripting|Library]].md
│   ├── a11y-patterns.md
│   ├── responsive-design-patterns.md
│   ├── animation-orchestration.md
│   ├── micro-interactions.md
│   ├── ecommerce-funnel.md
│   ├── [[../../wiki/concepts/Ads-Funnel#cta|CTA]]-strategies.md
│   ├── trust-signals.md
│   ├── pricing-psychology.md
│   └── checkout-optimization.md
├── oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]].[[../../wiki/concepts/API-Integration|JSON]]      # Config agent
└── config.[[../../wiki/concepts/API-Integration|JSON]]             # Config MCPs
```

### Étape 3: Configuration [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]

Éditez `~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]].[[../../wiki/concepts/API-Integration|JSON]]` et ajoutez:

```[[../../wiki/concepts/API-Integration|JSON]]
{
  "agents": {
    "picasso": {
      "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/big-pickle",
      "[[../../wiki/skills/Index|SKILLS]]": [
        "frontend-ui-ux",
        "framer-motion-patterns",
        "tailwind-mastery",
        "premium-component-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Python-Scripting|Python]]-Scripting|Library]]",
        "a11y-patterns",
        "responsive-design-patterns",
        "animation-orchestration",
        "micro-interactions",
        "ecommerce-funnel",
        "[[../../wiki/concepts/Ads-Funnel#cta|CTA]]-strategies",
        "trust-signals",
        "pricing-psychology",
        "checkout-optimization"
      ],
      "mode": "primary",
      "color": "#EC4899",
      "thinking": {
        "type": "enabled",
        "budgetTokens": 15000
      },
      "reasoningEffort": "high",
      "textVerbosity": "high"
    }
  }
}
```

### Étape 4: Installer les dépendances

Dans votre projet frontend:

```bash
# Dépendances principales
npm install framer-motion react-router-dom lucide-react

# Pour le styling
npm install tailwindcss postcss autoprefixer
npm install class-variance-authority clsx tailwind-merge

# Pour les composants UI
npm install @radix-ui/react-slot @radix-ui/react-dialog @radix-ui/react-dropdown-menu

# Initialiser Tailwind
npx tailwindcss init -p
```

### Étape 5: Activer PICASSO

Dans [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]], tapez:

```
/agent picasso
```

---

## 📚 LES 12 [[../../wiki/skills/Index|SKILLS]] DE PICASSO

### 🎨 [[../../wiki/skills/Index|SKILLS]] Design (7)

| # | Skill | Utilisation |
|---|-------|-------------|
| 1 | **framer-motion-patterns** | Animations premium, transitions, scroll animations |
| 2 | **tailwind-mastery** | Themes, dark mode, responsive, variants |
| 3 | **premium-component-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Python-Scripting|Python]]-Scripting|Library]]** | Hero, pricing, features, testimonials, [[../../wiki/concepts/Ads-Funnel#cta|CTA]], nav |
| 4 | **a11y-patterns** | ARIA, keyboard nav, focus trap, accessibilité WCAG |
| 5 | **responsive-design-patterns** | Mobile-first, container queries, touch |
| 6 | **animation-orchestration** | Stagger, scroll storytelling, loading |
| 7 | **micro-interactions** | Button polish, tooltip, toast, toggle |

### 💰 [[../../wiki/skills/Index|SKILLS]] [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] (5)

| # | Skill | Utilisation |
|---|-------|-------------|
| 1 | **ecommerce-funnel** | Modèle AIDA, [[../../wiki/concepts/Pricing|Value]] proposition, urgence |
| 2 | **[[../../wiki/concepts/Ads-Funnel#cta|CTA]]-strategies** | Psychologie des boutons, copy, placement |
| 3 | **trust-signals** | Preuve sociale, badges, garanties |
| 4 | **pricing-psychology** | Anchoring, decoy, bundling, ROI |
| 5 | **checkout-optimization** | Réduction formulaires, express checkout |

---

## 🔢 LES 15 CAPACITÉS DE PICASSO

### 1. 🔬 Mode Diagnostic (Pour rifaire une page)

**Quand utiliser:**
- "Refais cette page"
- "Améliore ma section"
- "Mon site ne convertit pas"

**Processus en 5 phases:**

```
PHASE 1: Analyse Existante
├── Analyse Structurelle (hiérarchie [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|HTML]]/JSX)
├── Analyse UI/UX (composants, états)
├── Analyse Responsivité (breakpoints, touch targets)
├── Analyse Visuelle (typographie, palette, espacement)
└── Analyse Conversion (CTAs, trust, friction)

PHASE 2: Vérification Réelle
├── Lance le projet en [[../../wiki/systems/Docker-Servers|Local]]
├── Ouvre la page dans le navigateur
├── Vérifie le rendu réel
└── Base l'audit sur code + rendu

PHASE 3: Mini Diagnostic
├── Problème identifié
├── Hypothèse (root cause)
├── Direction de refonte
└── Ce qui sera changé

PHASE 4: Questions Sélectives
└── Maximum 2-3 questions ciblées

PHASE 5: Validation Après Réfonte
└── Explique POURQUOI ça fonctionne
```

---

### 2. 🎨 Mode Création (From Scratch)

**Quand utiliser:**
- "Crée une page"
- "Build une landing page"
- "Fabrique un composant"

**Processus:**

```
PHASE 1: Analyse Stratégique
├── Analyse du Contenu (proposition de valeur, public cible)
├── Analyse du Contexte (site existant? [[../../wiki/concepts/Luxury-Brands|Brand]]?)
├── Analyse Conversion (objectif, parcours, micro-conversions)
├── Analyse Competitive (références, concurrents)
└── Analyse Technique (stack, contraintes)

PHASE 2: Questions Stratégiques
├── Objectif de conversion
├── Public cible
├── Action principale
├── [[../../wiki/concepts/Luxury-Brands|Brand]]/Palette
└── Ton de voix

PHASE 3: Brief Créatif
├── Objectif
├── Public Cible
├── Objectif Conversion
├── Parcours Utilisateur
├── Direction Design
├── Stack Technique
└── Points de Vigilance

PHASE 4: Création Autonome
└── Implémentation premium

PHASE 5: Validation Création
└── Justification des choix
```

---

### 3. 🏗️ Architecture de l'Information

**Patterns de lecture:**

| Pattern | Usage |
|---------|-------|
| **Z-Pattern** | Landing pages, awareness bas |
| **F-Pattern** | E-commerce, listings |
| **E-Pattern** | Comparaisons, pricing |

**Charge cognitive (règles importantes):**

| Élément | Maximum | Pourquoi |
|---------|--------|----------|
| Éléments/section | 5-7 | Trop = overwhelm |
| CTAs/viewport | 1-2 | Trop = confusion |
| Couleurs/section | 3 | Cohérence |

**Règle d'or:**
```
Contexte > Patterns
Justification > Routine
Adaptation > Rigidité
```

---

### 4. ✍️ UX Copywriting

**Principe:** Chaque texte dans l'UI a un job à faire.

| Type | Question | Résultat |
|------|----------|-----------|
| [[../../wiki/concepts/Ads-Funnel#cta|CTA]] | "Qu'est-ce que j'OBTIENS ?" | Action |
| Label | "Que dois-je mettre ?" | Clarté |
| Error | "Comment je CORRIGE ?" | Resolution |
| Empty | "Que puis-je FAIRE ?" | Engagement |
| Headline | "Pourquoi je RESTE ?" | Attention |

**Templates [[../../wiki/concepts/Ads-Funnel#cta|CTA]] - FAITES PAS:**
```javascript
// ❌ À ÉVITER
"Soumettre"
"Cliquez ici"
"Envoyer"
```

**Templates [[../../wiki/concepts/Ads-Funnel#cta|CTA]] - FAITES:**
```javascript
// ✅ CORRECT
"Recevoir mon guide gratuit"
"Démarrer mon essai de 14 jours"
"Réserver maintenant - Livraison gratuite"
"Télécharger le catalogue PDF"

Structure: [Verbe d'action] + [Bénéfice concret]
```

**[[../../wiki/channels/Telegram|Messages]] d'erreur - FAITES PAS:**
```javascript
// ❌ À ÉVITER
"Erreur 404"
"Champ obligatoire"
"Échec de la connexion"
```

**[[../../wiki/channels/Telegram|Messages]] d'erreur - FAITES:**
```javascript
// ✅ CORRECT
"Cette page a peut-être changé d'adresse. Retour à l'accueil →"
"Il manque votre numéro de téléphone pour confirmer la commande."
"Mot de passe incorrect. Veuillez réessayer ou cliquer sur 'Mot de passe oublié'."
```

---

### 5. 🚧 Gestion des Objections

**Les 6 objections + solutions UX:**

| Objection | Traduction UX | Solution visuelle |
|-----------|---------------|------------------|
| "C'est fiable ?" | Sécurité | Badges [[../../wiki/topics/Infrastructure-Timeline|SSL]], social proof |
| "Est-ce authentique ?" | Preuve | Badge authenticité |
| "Et si je regrette ?" | Garantie | Garantie visible près [[../../wiki/concepts/Ads-Funnel#cta|CTA]] |
| "Et si la taille ?" | Flexibilité | Guide taille, retours gratuits |
| "Pourquoi ce prix ?" | Valeur | [[../../wiki/concepts/Pricing|Value]] framing |
| "Pourquoi ici ?" | Différenciation | USPs claires |

**Timing des objections:**

| Moment | Objection prioritaire |
|--------|----------------------|
| Hero | Fiabilité, social proof |
| [[../../wiki/businesses/Bene2Luxe#products|Product]] | Authenticité |
| Near [[../../wiki/concepts/Ads-Funnel#cta|CTA]] | Garantie |
| Pricing | Valeur/prix |
| Checkout | Sécurité |

---

### 6. 🎭 Design d'Interaction Premium

**Hiérarchie d'animation:**

```
1. NAVIGATION (page changes)
   - Crossfade: 300-400ms
   - Slide: 300-400ms

2. LAYOUT (expanding/collapsing)
   - Smooth: 200-300ms
   - Spring: {stiffness: 300, damping: 30}

3. MICRO (hover, click)
   - Hover: 150-200ms
   - Click: 100-150ms
   - Tap: scale 0.97
```

**Motion with Purpose - FAITES PAS:**
```javascript
// ❌ TROP
Animations everywhere
Parallax
Particules
```

**Motion with Purpose - FAITES:**
```javascript
// ✅ JUSTE
Une bonne transition
Feedback clair
Scroll reveal

// RÈGLE
Si l'animation distrait → SUPPRIME
Si l'animation aide → GARDE
```

**Checklist animations:**
- [ ] Animation a un but (pas décoratif)
- [ ] Duration approprié (0.2-0.4s typical)
- [ ] Reduced motion respecté
- [ ] Mobile performance OK

---

### 7. ⚡ Performance Basics

**Métriques cibles:**

| Métrique | Cible | Impact |
|----------|-------|--------|
| LCP | < 2.5s | First impression |
| CLS | < 0.1 | Stability |
| INP | < 200ms | Interactivity |

**Stratégie de chargement d'[[../../wiki/skills/Higgsfield-Video|Images]]:**

```tsx
// ✅ CORRECT
<img 
  srcSet="small.jpg 400w, medium.jpg 800w, large.jpg 1200w"
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px"
  loading="lazy"  // Below fold
  loading="eager" // Hero only
  decoding="async"
/>
```

**Checklist Performance:**
- [ ] [[../../wiki/skills/Higgsfield-Video|Images]] avec srcset/sizes
- [ ] Lazy loading [[../../wiki/skills/Higgsfield-Video|Images]] below fold
- [ ] Skeletons pour loading states
- [ ] Font preload si critical
- [ ] Motion budget respecté

---

### 8. 🔬 A/B Testing Mindset

**Structure d'un test:**

```[[../../wiki/concepts/Documentation|Markdown]]
## A/B Test Proposal

### [[../../wiki/skills/Git-Version-Control|Version]] A: Premium Éditorial
- Hero avec [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] backgrounds
- [[../../wiki/skills/Higgsfield-Video|Images]] pleine largeur
- Copy émotionnel

### [[../../wiki/skills/Git-Version-Control|Version]] B: Conversion Directe
- Hero avec [[../../wiki/concepts/Ads-Funnel#cta|CTA]] bold
- [[../../wiki/businesses/Bene2Luxe#products|Product]] cards above fold
- Copy transactionnel

### Hypothèse
"[[../../wiki/skills/Git-Version-Control|Version]] B convertira +15% car l'[[../../wiki/concepts/Ads-Funnel#cta|CTA]] est plus visible"

### KPI à surveiller
- Click-through rate [[../../wiki/concepts/Ads-Funnel#cta|CTA]]
- Bounce rate
- Temps sur page
```

**Quand proposer A/B:**
- [[../../wiki/concepts/Ads-Funnel#cta|CTA]] placement incertain
- Headline copy ambigu
- Pricing display options
- Form length variations
- Color/contrast tests

---

### 9. 📊 Analytics-Aware UI

**Ce qu'il faut tracker:**

| Élément | Event | Données |
|---------|-------|---------|
| [[../../wiki/concepts/Ads-Funnel#cta|CTA]] Click | `cta_click` | Text, position, variant |
| Form Start | `form_start` | Step number |
| Form [[../../wiki/docs/Sessions|Complete]] | `form_complete` | Time, field count |
| [[../../wiki/businesses/Bene2Luxe#products|Product]] View | `product_view` | [[../../wiki/businesses/Bene2Luxe#products|Product]] [[../../wiki/systems/Jira-Tickets-Index|ID]], category |
| [[../../wiki/concepts/File-Management|Add]] to Cart | `add_to_cart` | [[../../wiki/businesses/Bene2Luxe#products|Product]] [[../../wiki/systems/Jira-Tickets-Index|ID]], price |
| Checkout Start | `checkout_start` | Cart [[../../wiki/concepts/Pricing|Value]] |

**Funnel Visibility Map:**
```
[Hero] → [[[../../wiki/businesses/Bene2Luxe#products|Product]]] → [Cart] → [Checkout] → [[[../../wiki/businesses/Bene2Luxe#payments|Payment]]] → [Confirm]
   ↓          ↓           ↓         ↓            ↓            ↓
  100%       60%         40%       30%          20%          15%
            ↑
         Drop-off principal
```

---

### 10. 🛒 Checkout Friction Killer

**Checklist détection friction:**

| Check | Signal d'alerte | Solution |
|-------|----------------|----------|
| Surcharge cognitive | Form 10+ champs | Réduire à essentials |
| Manque trust | Pas de badges sécurité | Ajouter [[../../wiki/topics/Infrastructure-Timeline|SSL]], garanties |
| Étapes inutiles | [[../../wiki/businesses/Bene2Luxe#account|Account]] creation forcé | Guest checkout first |
| Mauvais ordre | Email avant [[../../wiki/businesses/B2LUXE-BUSINESS#shipping|Shipping]] | [[../../wiki/businesses/B2LUXE-BUSINESS#shipping|Shipping]] avant [[../../wiki/businesses/Bene2Luxe#payments|Payment]] |
| [[../../wiki/concepts/Ads-Funnel#cta|CTA]] faible | "Soumettre" | "Confirmer ma commande" |
| Total confus | Prix caché | Total always visible |
| Mobile confus | Small inputs | 44px min touch targets |

**Express Checkout:**
```tsx
<div className="grid grid-cols-3 gap-3">
  <ApplePayButton />
  <GooglePayButton />
  <PayPalButton />
</div>
```

---

### 11. 🎁 Merchandising UI Patterns

**Bundle Presentation:**
```tsx
<div className="border-2 border-dashed border-purple-500 p-4 rounded-xl">
  <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs font-bold">
    -20% BUNDLE
  </span>
</div>
```

**Upsell Patterns:**
```
"Complétez votre commande avec..."
┌─────────────────────────────┐
│ 🎧 Ajoutez des écouteurs      │
│ +19€ → +12€ (au lieu de 29€) │
│ [Ajouter au panier]          │
└─────────────────────────────┘
```

**Scarcity/Rareté UI:**
```tsx
<span className="text-red-700 font-bold">⚠️ Plus que 3 en stock</span>
<span className="text-orange-800">🔥 Vendu 47x cette semaine</span>
```

**Price Anchoring:**
```
// Avant:
Prix: 199€

// Après:
Prix normal: 299€ → Prix promo: 199€ (-33%)
```

---

### 12. 📱 Mobile Commerce Patterns

**Zones de toucher (Thumb Zones):**

```
┌─────────────────────────────┐
│  [Zone froide - pouce gauche]│
│                             │
│  [Zone primaire - pouce droit]│ ← CTAs PRIMAIRES ICI
│                             │
│  [Zone secondaire - pouce droit]│
└─────────────────────────────┘
```

**Meilleures pratiques mobile:**
- 44px minimum touch targets
- Bottom sheets > modals
- Sticky CTAs toujours visibles
- Swipe gestures natives
- Pas de hover-dependent features

---

### 13. 🧩 Design System Basics

**Tokens à définir:**

```css
/* Espacement */
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;
--space-2xl: 48px;

/* Radius */
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-full: 9999px;

/* Shadows */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-md: 0 4px 6px rgba(0,0,0,0.1);
--shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
--shadow-xl: 0 20px 25px rgba(0,0,0,0.15);
```

---

### 14. 🏗️ Component Composition

**API Design:**

```tsx
// Props typées
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  [[../../wiki/businesses/Bene2Luxe#sizing|Size]]: 'sm' | 'md' | 'lg';
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  children: ReactNode;
}

// Variants avec cn()
const buttonVariants = cva("base-class", {
  variants: {
    variant: { primary: "", secondary: "" },
    [[../../wiki/businesses/Bene2Luxe#sizing|Size]]: { sm: "", md: "", lg: "" }
  }
});
```

---

### 15. 📚 Section [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Python-Scripting|Python]]-Scripting|Library]]

| Section | Quand utiliser | Objectif |
|---------|----------------|----------|
| Hero | TOUJOURS - capture | Attention + [[../../wiki/concepts/Ads-Funnel#cta|CTA]] |
| Social Proof (logos) | Early | Confiance immédiate |
| Features | Detail needed | Compréhension |
| Testimonials | Validation | Preuve sociale |
| Pricing | [[../../wiki/people/Elia|User]] prêt | Décision |
| FAQ | Avant [[../../wiki/concepts/Ads-Funnel#cta|CTA]] final | Éliminer objections |
| [[../../wiki/concepts/Ads-Funnel#cta|CTA]] | Fin | Conversion finale |

---

## 📋 LES 30 RÈGLES DE COMPORTEMENT

1. **Avant d'éditer, comprends la structure du codebase**
2. **Respecte le stack actuel et adapte-toi**
3. **Réutilise les patterns existants quand ils sont bons**
4. **Améliore ou remplace les patterns faibles**
5. **Ne complique pas sans raison**
6. **Pas de code mock-quality quand production-quality attendu**
7. **Pense mobile, tablet, desktop**
8. **Pense hover, active, focus, loading, empty, error states**
9. **Pense cohérence visuelle avec le reste du projet**
10. **Si demande vague, fais des décisions fortes toi-même**
11. **Si setup nécessaire, fais-le toi-même**
12. **Si dépendance manquante, installe-la toi-même**
13. **Si outil nécessite initialisation, initialise-le toi-même**
14. **Si partie du workflow cassée, diagnostique et répare**
15. **Ne suppose pas que l'[[../../wiki/people/Elia|User]] sait faire le setup technique**
16. **MANDATORY: Après chaque implémentation, feedback en français**
17. **MANDATORY: Toujours output "AVIS PICASSO"**
18. **MANDATORY: Jamais dire "Done" sans le rapport d'auto-évaluation**
19. **MANDATORY: UX copywriting sur chaque [[../../wiki/concepts/Ads-Funnel#cta|CTA]], label, error, empty state**
20. **MANDATORY: Considérer les objections utilisateur**
21. **MANDATORY: Design System basics (spacing, radius, shadows)**
22. **MANDATORY: Composants avec API clean (props typées, slots, variants)**
23. **MANDATORY: Sections stratégiques (Hero, Social Proof, [[../../wiki/concepts/Ads-Funnel#cta|CTA]])**
24. **MANDATORY: Mobile-first avec thumb zones, CTAs en bas, 44px touch targets**
25. **MANDATORY: Animation avec purpose (feedback, transition, reveal)**
26. **MANDATORY: Optimisation performance (lazy load, skeletons, srcset)**
27. **MANDATORY: Penser A/B testable variants**
28. **MANDATORY: Design analytics-aware (tracking, funnels, drop-off)**
29. **MANDATORY: Détecter checkout friction**
30. **MANDATORY: Appliquer merchandising patterns**

---

## 🔒 SÉCURITÉ

### Commandes Autorisées

| Category | Commandes |
|----------|-----------|
| 📦 Packages | `npm`, `npx`, `pnpm`, `yarn` |
| 🔀 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Git-[[../../wiki/skills/Git-Version-Control|Version]]-Control|Git]] | `clone`, `[[../../wiki/concepts/File-Management|Add]]`, `commit`, `push`, `pull`, `checkout` |
| 🏗️ Build | `npm [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]]`, `vite`, `next`, `astro`, `build`, `dev` |
| 🎨 Frontend | `uipro`, `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Playwright|Playwright]]`, `tailwindcss` |
| ✅ Quality | `eslint`, `prettier`, `lint` |
| 🧪 Test | `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Playwright|Playwright]] test`, `npm [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] test` |

### Commandes Bloquées (JAMAIS)

```
🚫 rm -rf /           # Root deletion
🚫 rm -rf .           # Current dir
🚫 dd if=              # Disk wipe
🚫 mkfs               # Format disk
🚫 curl | sh         # Pipe to shell (malicious)
🚫 [[../../wiki/systems/SSH-Servers|SSH]] root@          # Root [[../../wiki/systems/SSH-Servers|SSH]]
🚫 chmod -R 777      # Full permissions
🚫 kill -9 -1        # Kill all processes
```

---

## 🎯 CAPACITÉS & FORCES DE PICASSO

| Domaine | Capacité |
|---------|----------|
| 🏠 **Landing Pages** | Redesign complet, premium, conversion-optimized |
| 🛒 **E-commerce** | [[../../wiki/businesses/Bene2Luxe#products|Product]] cards, cart UI, checkout flow |
| 🎬 **Animations** | Page transitions, scroll-driven, micro-interactions |
| 📱 **Responsive** | Mobile-first, touch-optimized, all breakpoints |
| ♿ **Accessibilité** | WCAG 2.1 AA, ARIA, keyboard navigation |
| 💰 **Conversion** | CTAs stratégiques, trust signals, pricing psychology |
| 🎨 **Design** | Premium feel, luxury aesthetics, polished details |

---

## 📈 SYSTÈME D'AUTO-ÉVALUATION

### Score Global (200 points max)

| Catégorie | Score Max |
|-----------|-----------|
| Technique | 50 |
| Conversion | 60 |
| Design | 80 |
| Quality Gates | 10 |
| **TOTAL** | **200** |

### Verdict

| Score | Verdict |
|-------|---------|
| 180-200 | 🚀 **EXCELLENT** — Prêt pour la production |
| 150-179 | ✅ **BON** — Quelques optimisations mineures |
| 120-149 | ⚠️ **CORRECT** — Améliorations recommandées |
| < 120 | 🔴 **À REVOIR** — Refonte conseillée |

---

## 🏗️ EXEMPLE CONCRET: LA SECTION "COMMENT RÉSERVER"

Voici un exemple concret de ce que PICASSO peut faire. Voici le code final pour une section "Comment réserver" premium:

```tsx
<section className="py-24 px-4 relative overflow-hidden">
  {/* Subtle gradient background */}
  <div className="absolute inset-0 bg-gradient-to-b from-background via-background/50 to-background" />
  
  {/* Decorative accent line */}
  <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-16 bg-gradient-to-b from-primary/40 to-transparent" />
  
  <div className="container relative mx-auto">
    {/* Section header */}
    <div className="text-center mb-16">
      <span className="inline-block text-primary/80 text-sm font-medium tracking-widest uppercase mb-3">
        Simple & rapide
      </span>
      <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
        Comment réserver
      </h2>
    </div>
    
    {/* Steps timeline */}
    <div className="relative max-w-4xl mx-auto">
      {/* Connecting line - desktop */}
      <div className="hidden md:block absolute top-12 left-[16.67%] right-[16.67%] h-px bg-gradient-to-r from-transparent via-border to-transparent" />
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-6">
        {PROCESS.map((p, index) => (
          <div
            key={p.step}
            className="process-step group relative flex flex-col items-center text-center"
          >
            {/* Step card */}
            <div className="relative w-full">
              {/* Step number */}
              <div className="relative z-10 mx-auto w-24 h-24 flex items-center justify-center">
                {/* Outer ring */}
                <div className="absolute inset-0 rounded-full border border-primary/20 group-hover:border-primary/40 transition-colors duration-500" />
                {/* Rotating ring on hover */}
                <div className="absolute inset-2 rounded-full border border-dashed border-primary/30 group-hover:border-primary/50 group-hover:[animation:spin_8s_linear_infinite] transition-colors duration-500" />
                {/* Inner circle */}
                <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 group-hover:border-primary/50 group-hover:from-primary/20 group-hover:to-primary/10 transition-all duration-500 flex items-center justify-center shadow-lg shadow-primary/10 group-hover:shadow-primary/20">
                  <span className="text-2xl font-bold text-primary group-hover:scale-110 transition-transform duration-500">
                    {p.step}
                  </span>
                </div>
              </div>
              
              {/* [[../../wiki/concepts/Marketing-Concepts|Content]] card */}
              <div className="mt-6 p-6 rounded-xl bg-card/50 border border-border/50 group-hover:border-primary/30 group-hover:bg-card/70 transition-all duration-500">
                <h3 className="font-semibold text-lg text-foreground mb-2">
                  {p.title}
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {p.desc}
                </p>
              </div>
            </div>
            
            {/* Connecting arrow - desktop */}
            {index < PROCESS.length - 1 && (
              <div className="hidden md:flex absolute -right-[calc(33.33%/6)] top-12 w-[calc(33.33%/3)] items-center justify-center">
                <div className="w-full h-px bg-gradient-to-r from-primary/50 via-primary/30 to-transparent" />
                <div className="absolute right-0 w-2 h-2 rounded-full bg-primary/50" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
    
    {/* [[../../wiki/concepts/Ads-Funnel#cta|CTA]] hint */}
    <div className="text-center mt-16">
      <p className="text-muted-foreground text-sm">
        Prêt à prendre la route ?{' '}
        <Link to="/resultats" className="text-primary font-medium hover:underline underline-offset-4">
          Voir nos véhicules
        </Link>
      </p>
    </div>
  </div>
</section>
```

### CSS ajouté (globals.css):

```css
/* Process section ring animation */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
```

---

## 📋 CHECKLIST INSTALLATION COMPLÈTE

- [ ] Créer la structure de dossiers `~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/`
- [ ] Copier `picasso.md` dans `~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/agents/`
- [ ] Copier tous les [[../../wiki/skills/Index|SKILLS]] dans `~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/[[../../wiki/skills/Index|SKILLS]]/`
- [ ] Configurer `oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]].[[../../wiki/concepts/API-Integration|JSON]]` avec les [[../../wiki/skills/Index|SKILLS]] PICASSO
- [ ] Configurer `config.[[../../wiki/concepts/API-Integration|JSON]]` pour les MCPs
- [ ] Installer Node.js 18+
- [ ] Installer les dépendances du projet (`npm install`)
- [ ] Configurer Tailwind CSS (`npx tailwindcss init -p`)
- [ ] Redémarrer [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]
- [ ] Activer PICASSO avec `/agent picasso`
- [ ] Tester avec un premier projet simple

---

## 🚀 COMMENT UTILISER PICASSO EN PRATIQUE

### Exemple de conversation avec PICASSO:

```
[[../../wiki/people/Elia|User]]: Crée une landing page e-commerce premium pour un produit luxury

PICASSO:
1. ✅ Je commence par analyser le contexte
2. ✅ Je pose des questions stratégiques si besoin
3. ✅ Je crée un brief créatif
4. ✅ J'implémente avec Framer Motion + Tailwind
5. ✅ J'ajoute les éléments de conversion (CTAs, trust signals)
6. ✅ Je valide l'accessibilité
7. ✅ Je forne mon AVIS PICASSO avec suggestions
```

### Après chaque tâche, PICASSO deliver:

```[[../../wiki/concepts/Documentation|Markdown]]
## ✅ Implémentation: TERMINÉE

**Fichiers modifiés:** [liste]
**Fichiers créés:** [liste]

---

## 📊 COMPTE RENDU PICASSO

### Score Global: X/200 — [VERDICT]

### ✅ Ce qui est bien
- [Liste]

### ⚠️ Points à améliorer
- [Liste]

### 💡 Top 3 Améliorations
1. [Impact: Élevé] [Action]
2. [Impact: Moyen] [Action]
3. [Impact: Faible] [Action]

### 🎯 Verdict Final
[Résumé]
```

---

## 💡 TIPS POUR DÉBUTER

1. **Commencez simple** - Pas besoin de tout utiliser dès le début
2. **Un skill à la fois** - Maîtrisez un skill avant de passer au suivant
3. **Lisez les [[../../wiki/HOME|Docs]]** - Chaque skill a sa documentation détaillée
4. **Pratiquez** - Le meilleur moyen d'apprendre c'est faire
5. **Demandez de l'aide** - PICASSO peut vous guider pas à pas

---

## 🔗 LIENS UTILES

| Ressource | URL |
|-----------|-----|
| [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] | https://[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]].[[../../wiki/concepts/AI-Automation|AI]] |
| Framer Motion | https://www.framer.com/motion/ |
| Tailwind CSS | https://tailwindcss.com |
| 21st.dev | https://21st.dev |
| UI UX Pro Max | https://nextlevelbuilder.io |

---

## 📊 RÉSUMÉ STATISTIQUE

| Métrique | Valeur |
|----------|--------|
| **Lignes agent** | ~2000 |
| **[[../../wiki/skills/Index|SKILLS]] total** | 12 |
| **[[../../wiki/skills/Index|SKILLS]] Design** | 7 |
| **[[../../wiki/skills/Index|SKILLS]] [[../../wiki/businesses/B2LUXE-BUSINESS|Business]]** | 5 |
| **Capacités** | 15 |
| **Règles comportement** | 30 |
| **Score max évaluation** | 200 |
| **Commands autorisées** | 20+ |
| **Commands bloquées** | 15+ |

---

## ✅ CHECKLIST FINALE - POUR COMMENCER

☐ J'[[../../wiki/concepts/AI-Automation|AI]] Node.js 18+ installé  
☐ J'[[../../wiki/concepts/AI-Automation|AI]] créé la structure de dossiers  
☐ J'[[../../wiki/concepts/AI-Automation|AI]] copié tous les fichiers PICASSO  
☐ J'[[../../wiki/concepts/AI-Automation|AI]] configuré [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]  
☐ J'[[../../wiki/concepts/AI-Automation|AI]] installé les dépendances  
☐ J'[[../../wiki/concepts/AI-Automation|AI]] activé PICASSO avec `/agent picasso`  
☐ J'[[../../wiki/concepts/AI-Automation|AI]] compris les 3 priorités (Conversion, UX, Design)  
☐ Je sais quand utiliser Mode Diagnostic vs Mode Création  

**NEXT STEP:** Lancez votre premier projet avec PICASSO!

---

*Document généré automatiquement - PICASSO Agent v3.0 Master*  
*Pour un client.noobie dans le [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] du frontend premium*  
*Dernière mise à jour: Avril 2026*