# Bene2Luxe Reviews Setup Guide

**Date**: 1er Avril 2026
**Business**: Bene2Luxe
**Status**: En préparation
**Jira**: BEN-10

---

## 🎯 Objectif

Mettre en place un système de reviews pour Bene2Luxe afin de:
- Augmenter la confiance des nouveaux clients
- Améliorer le SEO local
- Capitaliser sur les clients satisfaits

---

## 📋 Checklist Setup Reviews

### 1. Google Business Profile (Priority)

**Pourquoi**: Améliore le SEO local et la visibilité dans Google Maps

#### Étapes:

1. **Créer/Claim le profil Google Business**
   - URL: https://business.google.com/create
   - Nom: Bene2Luxe
   - Adresse: À remplir (France/Suisse)
   - Catégorie: Boutique de mode de luxe
   - Website: https://bene2luxe.com

2. **Vérification**
   - Code postal par courrier (2-3 semaines)
   - Option téléphone si disponible

3. **Optimisation du profil**
   - Photos de qualité (logo, storefront, produits)
   - Horaires d'ouverture
   - Numéro WhatsApp: À ajouter
   - Description: "Boutique de luxe d'occasion - Sneakers, Casquettes, Vêtements premiums"

4. **Demander des reviews aux clients**
   - Lien direct: https://g.page/bene2luxe/review
   - Template message WhatsApp:
     ```
     Salut ! Tu as commandé chez Bene2Luxe récemment? 
     Si tu es satisfait(e), ça nous aiderait beaucoup si tu pouvais laisser un avis sur Google 🙏
     Voici le lien: [LIEN]
     Merci infiniment! 🙏✨
     ```

#### Ressources:
- Google Business Profile: https://business.google.com
- Lien reviews direct: À créer après setup

---

### 2. Trustpilot (Priority)

**Pourquoi**: Plateforme de reviews reconnue internationalement

#### Étapes:

1. **Créer un compte Business**
   - URL: https://business.trustpilot.com
   - Email: contact@bene2luxe.com

2. **Setup du profil entreprise**
   - Nom: Bene2Luxe
   - Website: https://bene2luxe.com
   - Description: Boutique de luxe d'occasion

3. **Demander des reviews**
   - Email automatisé après commande
   - Lien personnalisé pour clients

4. **Intégration possible**
   - Si WooCommerce: Plugin Trustpilot
   - Manuel: Envoyer emails avec lien Trustpilot

#### Template email demande review:
```
Objet: Ton avis nous intéresse 🙏

Salut [NOM],

Merci pour ta commande chez Bene2Luxe! 🙏

Si tu es satisfait(e) de ton achat, ça nous ferait super plaisir 
si tu pouvais partager ton expérience sur Trustpilot.

Ça prend 30 secondes et ça aide enormément les autres clients 
à nous découvrir: [LIEN TRUSTPILOT]

Merci encore! ✨

L'équipe Bene2Luxe
```

---

### 3. Intégration Site Web

#### Option A: Badge Trustpilot (Widget)
```html
<!-- À ajouter sur le site -->
<div id="trustpilot-widget"></div>
<script src="//widget.trustpilot.com/bootstrap/v5/tp.widget.bootstrap.min.js"></script>
```

#### Option B: Google Reviews Badge
```html
<!-- Google Reviews Widget -->
<div class="google-reviews">
  <a href="https://g.page/bene2luxe/review" target="_blank">
    ⭐⭐⭐⭐⭐ Laisser un avis Google
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

## 📱 Messages WhatsApp Templates

### Template 1: Review Google
```
Salut! 👋

Tu as reçu ta commande Bene2Luxe? J'espère que tu kiffes! 🙏

Si c'est le cas, ça nous aiderait enormément si tu pouvais 
laisser un petit avis sur Google ⭐⭐⭐⭐⭐

Ça prend 30 secondes et ça aide d'autres clients 
à nous découvrir: [LIEN GOOGLE]

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
Yo! On bosse dur pour offrir le meilleur service possible 🙏

Si t'es satisfait(e) de Bene2Luxe, un petit review nous aiderait 
énormément à grandir et aider plus de clients à nous trouver ⭐

Google: [LIEN]
Trustpilot: [LIEN]

Merci à toi! ✨
```

---

## 📊 KPI à Tracker

| Métrique | Objectif |
|----------|----------|
| Google Reviews | 10 en 1 mois |
| Trustpilot Reviews | 15 en 1 mois |
| Note moyenne | 4.5+ étoiles |
| Response rate | 100% |

---

## 🚀 Prochaines Étapes (Action Required)

### IMMÉDIAT:
- [ ] Rida: Créer compte Google Business Profile
- [ ] Rida: Créer compte Trustpilot Business
- [ ] Ali: Collecter les emails de clients satisfaits
- [ ] Thomas: Ajouter widget reviews sur site

### COURT TERME (1 semaine):
- [ ] Envoyer premier email demande review
- [ ] Configurer messages WhatsApp templates
- [ ] Monitorer et répondre aux reviews

---

## 📞 Ressources

- Google Business: https://business.google.com
- Trustpilot Business: https://business.trustpilot.com
- Trustpilot Widget: https://business.trustpilot.com/widgets

---

**Jira Ticket**: BEN-10
**Deadline**: Avril 2026
**Responsable**: Rida (selon business.md)
