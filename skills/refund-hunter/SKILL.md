---
name: refund-hunter
description: >
  Chasse de sites e-commerce vendant des produits physiques, analyse approfondie des politiques
  de remboursement (CGV, retours, transporteur), vérification des avis clients sur l'expérience
  remboursement, et évaluation du potentiel de revente sur les marketplaces.
  Use this skill whenever the user asks to: "chasse de remboursement", "refund hunting",
  "trouver des sites e-commerce", "analyser une politique de remboursement", "refund policy",
  "CGV e-commerce", "retour gratuit", "remboursement facile", "revendre sur eBay",
  "revendre sur Amazon", "LeBonCoin", "potentiel de revente", "refund-hunter", "refund hunter",
  or any request to find e-commerce sites with favorable refund policies for resale.
compatibility:
  - websearch
  - webfetch
  - gws-workspace (Google Doc append)
---

# RefundHunter — Skill

Chasse de sites e-commerce vendant des produits physiques, analyse approfondie des politiques de remboursement (CGV, retours, transporteur), vérification des avis clients sur l'expérience remboursement, et évaluation du potentiel de revente sur les marketplaces.

## Triggers

- "chasse de remboursement", "refund hunting", "trouver des sites e-commerce", "analyser une politique de remboursement"
- "refund policy", "CGV e-commerce", "retour gratuit", "remboursement facile"
- "revendre sur eBay", "revendre sur Amazon", "LeBonCoin", "potentiel de revente"
- "refund-hunter", "refund hunter"
- Toute demande de recherche de sites e-commerce avec politique de remboursement favorable

## Workflow

### Phase 1 — Découverte

1. Lire `workspace/HANDOFF_NEXT_SESSION.md` si présent (mémoire entre runs)
2. Lister les sites déjà analysés depuis le Google Doc pour éviter les doublons
3. Lancer des recherches web avec des requêtes variées :
   - "boutique en ligne vêtements retour gratuit"
   - "e-commerce produits physiques politique remboursement"
   - "boutique française livraison gratuite retour facile"
   - "shop en ligne PayPal retour 30 jours"
   - Variantes selon les niches (électronique, maison, sport, beauté, etc.)

### Phase 2 — Analyse approfondie (par site)

Pour chaque site trouvé, vérifier en profondeur :

1. **Page d'accueil** — identifier le type de produits physiques vendus
2. **CGV / Conditions de vente** —chercher les clauses de remboursement, délais, conditions
3. **Page Retours** — vérifier si les retours sont gratuits, délais (14j, 28j, 30j), conditions
4. **Page Livraison** — transporteur utilisé, livraison FR, frais de port
5. **Mentions légales** — siège social, pays d'expédition

### Phase 3 — Filtres de qualité

Un site ne passe que s'il coche **tous** ces critères :

| Critère | Détail |
|---------|--------|
| **PayPal** | Paiement possible via PayPal (remboursement facile) |
| **Livraison FR** | Livraison en France disponible |
| **Remboursement non-reçu** | Politique de remboursement si colis non reçu |
| **Remboursement endommagé** | Politique de remboursement si produit endommagé |
| **Retour gratuit** | Les frais de retour sont à la charge du vendeur |
| **Délai retour** | 14 jours (légal) ou 28-30 jours (confort) |

### Phase 3.2 — Avis clients (Expérience réelle remboursement)

**AVANT de valider un site**, vérifier les avis clients sur les plateformes tierces :

1. **Trustpilot** — chercher "[nom du site] Trustpilot" et analyser les avis mentionnant remboursement, retour, remboursement
2. **Reddit** — chercher "[nom du site] refund" ou "[nom du site] retour" ou "[nom du site] remboursement"
3. **Forums spécialisés** — forums e-commerce, forums consommateurs
4. **SignalConso** — vérifier les signalements sur SignalConso.gouv.fr
5. **Twitter/X** — chercher "[nom du site] refund" ou "[nom du site] remboursement"
6. **Avis Google** — vérifier les avis mentionnant retours/remboursement

**Filtrer les avis** :
- Ignorer les avis génériques (trop bon/vraiment nul)
- Se concentrer sur les avis décrivant une expérience concrète de remboursement/retour
- Noter les patterns récurrents (ex: "jamais remboursé", "retour payant", "pas de réponse")

### Phase 4 — Évaluation revente

Pour chaque site validé, évaluer le potentiel de revente :

| Critère | Note |
|---------|------|
| **Prix d'achat** | Prix sur le site e-commerce |
| **Prix de revente** | Prix moyen sur eBay/Amazon/LeBonCoin |
| **Marge potentielle** | Différence brute (revente - achat) |
| **Frais de port FR** | Coût livraison France |
| **Note moyenne** | Qualité du produit (avis) |
| **Délai livraison** | Rapidité de réception |
| **Potentiel** | Faible / Moyen / Fort |

### Phase 5 — Enregistrement

Pour chaque site validé, créer une entrée structurée :

```markdown
## [Date] — [Nom du site]

**URL :** [url]
**Catégorie :** [vêtements/électronique/maison/etc.]
**Prix moyen :** [montant]
**PayPal :** ✅/❌
**Livraison FR :** ✅/❌ (gratuite/payante : [montant])
**Retour gratuit :** ✅/❌
**Délai retour :** [14j/28j/30j]
**Remboursement non-reçu :** ✅/❌
**Remboursement endommagé :** ✅/❌
**Transporteur :** [nom si identifié]
**Avis Trustpilot :** [note]/5 ([nb] avis)
**Avis remboursement :** [résumé des avis clients sur remboursement]
**Expérience réelle :** [résumé de l'expérience remboursement vérifiée]
**Potentiel revente :** [évaluation détaillée]
**Marché cible :** [eBay/Amazon/LeBonCoin]
**Marge estimée :** [montant ou fourchette]
**Statut :** 🟢 REFUND-FRIENDLY / 🟡 PARTIAL / 🔴 NON
**Notes :** [informations complémentaires]
```

### Phase 6 — Import dans Google Doc (format DOCX)

Le workflow standard est `gws-workspace import-md` qui convertit automatiquement le Markdown en DOCX via le convertisseur local (`md_to_docx.js`) avant import :

1. Écrire le contenu du run dans un fichier `.md` dans `workspace/YYYY-MM-DD/append_run.md`
2. Lancer l'import :
   ```bash
   gws-workspace import-md "workspace/YYYY-MM-DD/append_run.md" "RefundHunter — <HH:MM>"
   ```
   → Convertisseur local MD → DOCX (tables DXA, headers blancs, zebra striping, formatting préservé)
   → Le DOCX est importé dans Google Docs
   → Retourne l'URL du document créé

**Pour les rapports quotidiens (run de fin de journée)** : utiliser `gws-workspace import-md` avec un fichier `.md` complet contenant le tableau de synthèse + sections. Le formatage Markdown (titres, listes, tableaux) est converti en DOCX natif avec mise en forme professionnelle.

### Phase 7 — Handoff

Mettre à jour `workspace/HANDOFF_NEXT_SESSION.md` avec :
- Sites analysés dans cette session
- Sites à analyzer dans la prochaine session
- Patterns identifiés (niches prometteuses, transporteurs fréquents, etc.)
- Erreurs ou difficultés rencontrées

## Anti-Patterns

- ❌ Ne pas se contenter d'un simple "le site existe" — toujours creuser CGV/retours/transporteur
- ❌ Ne pas utiliser `append-doc` pour le contenu brut — toujours passer par `import-md` qui convertit en DOCX via le convertisseur local
- ❌ Ne pas valider un site sans avoir vérifié les avis clients (Phase 3.2)
- ❌ Ne pas dupliquer des sites déjà analysés (consulter l'historique)
- ❌ Ne pas ignorer les retours payants — c'est un filtre critique
- ❌ Ne pas se fier uniquement à la politique affichée — vérifier les avis réels

## Outils disponibles

- `websearch` — Recherche web pour découvrir des sites
- `webfetch` — Récupérer le contenu des pages (CGV, retours, etc.)
- `gws-workspace import-md` — Convertir MD → DOCX (convertisseur local `md_to_docx.js`) et importer dans Google Doc (outil principal)
- `gws-workspace import-docx` — Importer directement un .docx dans Google Doc
- `gws-workspace search-doc` — Anti-doublon : chercher un domaine dans le Google Doc
- `gws-workspace read-doc` — Lire le Google Doc pour voir l'historique
- `bash` — Exécuter des commandes si nécessaire

## Notes importantes

- **Retour payant = mauvais filtre** — Si le client doit payer les frais de retour, c'est quasi un NO-GO sauf cas exceptionnels
- **Avis Trustpilot** — Se méfier des avis très anciens ou très récents, privilégier les patterns
- **Reddit** — Source fiable pour les expériences réelles de remboursement
- **SignalConso** — Vérifier les signalements officiels
- **Patterns à surveiller** — Si plusieurs avis mentionnent le même problème (ex: "pas de réponse", "remboursement refusé"), c'est un signal d'alarme

## Exemple de trigger

```
/refund-hunter
"Trouve-moi des boutiques de vêtements avec retour gratuit et remboursement facile"
"Analyse la politique de remboursement de [site]"
"Vérifie les avis clients sur le remboursement pour [site]"
```
