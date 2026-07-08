# [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] Reviews Setup Guide

**Date**: 1er Avril 2026
**[[../../wiki/businesses/B2LUXE-BUSINESS|Business]]**: [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]
**Status**: En préparation
**[[../../wiki/systems/Jira-Tickets-Index|Jira]]**: BEN-10

---

## 🎯 Objectif

Mettre en place un système de reviews pour [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] afin de:
- Augmenter la confiance des nouveaux clients
- Améliorer le SEO [[../../wiki/systems/Docker-Servers|Local]]
- Capitaliser sur les clients satisfaits

---

## 📋 Checklist Setup Reviews

### 1. [[../../wiki/channels/Google|Google]] [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] Profile (Priority)

**Pourquoi**: Améliore le SEO [[../../wiki/systems/Docker-Servers|Local]] et la visibilité dans [[../../wiki/channels/Google|Google]] Maps

#### Étapes:

1. **Créer/Claim le profil [[../../wiki/channels/Google|Google]] [[../../wiki/businesses/B2LUXE-BUSINESS|Business]]**
   - [[../../wiki/concepts/API-Integration|URL]]: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/businesses/B2LUXE-BUSINESS|Business]].[[../../wiki/channels/Google|Google]].com/[[../../wiki/concepts/File-Management|Create]]
   - Nom: [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]
   - Adresse: À remplir (France/Suisse)
   - Catégorie: Boutique de mode de luxe
   - Website: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]].com

2. **Vérification**
   - Code postal par courrier (2-3 semaines)
   - Option téléphone si disponible

3. **Optimisation du profil**
   - Photos de qualité (logo, storefront, produits)
   - Horaires d'ouverture
   - Numéro [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]: À ajouter
   - Description: "Boutique de luxe d'occasion - Sneakers, Casquettes, Vêtements premiums"

4. **Demander des reviews aux clients**
   - Lien direct: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://g.page/[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]/review
   - Template [[../../wiki/channels/Telegram|Message]] [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]:
     ```
     Salut ! Tu as commandé chez [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] récemment? 
     Si tu es satisfait(e), ça nous aiderait beaucoup si tu pouvais laisser un avis sur [[../../wiki/channels/Google|Google]] 🙏
     Voici le lien: [LIEN]
     Merci infiniment! 🙏✨
     ```

#### Ressources:
- [[../../wiki/channels/Google|Google]] [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] Profile: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/businesses/B2LUXE-BUSINESS|Business]].[[../../wiki/channels/Google|Google]].com
- Lien reviews direct: À créer après setup

---

### 2. Trustpilot (Priority)

**Pourquoi**: Plateforme de reviews reconnue internationalement

#### Étapes:

1. **Créer un compte [[../../wiki/businesses/B2LUXE-BUSINESS|Business]]**
   - [[../../wiki/concepts/API-Integration|URL]]: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/businesses/B2LUXE-BUSINESS|Business]].trustpilot.com
   - Email: contact@[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]].com

2. **Setup du profil entreprise**
   - Nom: [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]
   - Website: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]].com
   - Description: Boutique de luxe d'occasion

3. **Demander des reviews**
   - Email automatisé après commande
   - Lien personnalisé pour clients

4. **Intégration possible**
   - Si WooCommerce: [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Cursor-IDE|Cursor]]-IDE|Plugin]] Trustpilot
   - Manuel: Envoyer emails avec lien Trustpilot

#### Template email demande review:
```
Objet: Ton avis nous intéresse 🙏

Salut [NOM],

Merci pour ta commande chez [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]! 🙏

Si tu es satisfait(e) de ton achat, ça nous ferait super plaisir 
si tu pouvais partager ton expérience sur Trustpilot.

Ça prend 30 secondes et ça aide enormément les autres clients 
à nous découvrir: [LIEN TRUSTPILOT]

Merci encore! ✨

L'équipe [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]
```

---

### 3. Intégration Site Web

#### Option A: Badge Trustpilot (Widget)
```[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|HTML]]
<!-- À ajouter sur le site -->
<div id="trustpilot-widget"></div>
<[[../../wiki/concepts/Marketing-Concepts|Script]] src="//widget.trustpilot.com/bootstrap/v5/tp.widget.bootstrap.min.js"></[[../../wiki/concepts/Marketing-Concepts|Script]]>
```

#### Option B: [[../../wiki/channels/Google|Google]] Reviews Badge
```[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|HTML]]
<!-- [[../../wiki/channels/Google|Google]] Reviews Widget -->
<div class="[[../../wiki/channels/Google|Google]]-reviews">
  <a href="[[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://g.page/[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]/review" [[../../wiki/concepts/Ads-Funnel#targeting|Target]]="_blank">
    ⭐⭐⭐⭐⭐ Laisser un avis [[../../wiki/channels/Google|Google]]
  </a>
</div>
```

---

### 4. Stratégie Collection Reviews

#### Timing optimal:
- 24-48h après livraison
- Quand client a reçu et essayé les produits

#### Incentives (optionnel):
- 5% sur prochaine commande si review
- Entry into giveaway

#### À éviter:
- Acheter de faux reviews
- Solliciter des reviews uniquement positifs
- Supprimer les reviews négatifs (répondre!)

---

## 📱 Messages [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] Templates

### Template 1: Review [[../../wiki/channels/Google|Google]]
```
Salut! 👋

Tu as reçu ta commande [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]? J'espère que tu kiffes! 🙏

Si c'est le cas, ça nous aiderait enormément si tu pouvais 
laisser un petit avis sur [[../../wiki/channels/Google|Google]] ⭐⭐⭐⭐⭐

Ça prend 30 secondes et ça aide d'autres clients 
à nous découvrir: [LIEN [[../../wiki/channels/Google|Google]]]

Merci infiniment! ✨
```

### Template 2: Review Trustpilot
```
Salut! 👋

Commande bien reçue? J'espère que tu appréccies! 🙏

Si t'as 30 secondes, on serait super reconnaissants si tu pouvais 
partager ton expérience sur Trustpilot ⭐⭐⭐⭐⭐

Voici le lien: [LIEN TRUSTPILOT]

Merci! 🙏✨
```

### Template 3: Demande générale
```
Yo! On bosse dur pour offrir le meilleur [[../../wiki/concepts/AI-Automation|Service]] possible 🙏

Si t'es satisfait(e) de [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]], un petit review nous aiderait 
énormément à grandir et aider plus de clients à nous trouver ⭐

[[../../wiki/channels/Google|Google]]: [LIEN]
Trustpilot: [LIEN]

Merci à toi! ✨
```

---

## 📊 KPI à Tracker

| Métrique | Objectif |
|----------|----------|
| [[../../wiki/channels/Google|Google]] Reviews | 10 en 1 mois |
| Trustpilot Reviews | 15 en 1 mois |
| Note moyenne | 4.5+ étoiles |
| Response rate | 100% |

---

## 🚀 Prochaines Étapes (Action Required)

### IMMÉDIAT:
- [ ] [[../../wiki/people/Rida|Rida]]: Créer compte [[../../wiki/channels/Google|Google]] [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] Profile
- [ ] [[../../wiki/people/Rida|Rida]]: Créer compte Trustpilot [[../../wiki/businesses/B2LUXE-BUSINESS|Business]]
- [ ] [[../../wiki/people/Ali|Ali]]: Collecter les emails de clients satisfaits
- [ ] [[../../wiki/people/Thomas-Cogne|Thomas]]: Ajouter widget reviews sur site

### COURT TERME (1 semaine):
- [ ] Envoyer premier email demande review
- [ ] Configurer messages [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] templates
- [ ] Monitorer et répondre aux reviews

---

## 📞 Ressources

- [[../../wiki/channels/Google|Google]] [[../../wiki/businesses/B2LUXE-BUSINESS|Business]]: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/businesses/B2LUXE-BUSINESS|Business]].[[../../wiki/channels/Google|Google]].com
- Trustpilot [[../../wiki/businesses/B2LUXE-BUSINESS|Business]]: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/businesses/B2LUXE-BUSINESS|Business]].trustpilot.com
- Trustpilot Widget: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/businesses/B2LUXE-BUSINESS|Business]].trustpilot.com/widgets

---

**[[../../wiki/systems/Jira-Tickets-Index|Jira]] Ticket**: BEN-10
**Deadline**: Avril 2026
**Responsable**: [[../../wiki/people/Rida|Rida]] (selon [[../../wiki/businesses/B2LUXE-BUSINESS|Business]].md)
