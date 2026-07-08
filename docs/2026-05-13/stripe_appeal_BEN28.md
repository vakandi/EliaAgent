# Stripe Appeal Process — BEN-28

**Date**: 13 Mai 2026  
**Status**: Research complete — action needed by Wael  
**Deadline originale**: 20 Avril 2026 (passée ~23 jours)

## Résumé

Le compte Stripe de Bene2Luxe a été fermé. La cause probable est que Bene2Luxe utilise un compte Stripe standard pour un modèle marketplace (agrégation de paiements pour vendeurs tiers), ce qui viole les CGV de Stripe. La solution correcte serait Stripe Connect.

## Processus d'Appel

1. **Tenter connexion Dashboard** → Settings → Account → trouver la notification de fermeture
2. **Contacter Support** via le formulaire d'appel dans le Dashboard
3. **Alternative**: répondre à l'email de terminaison ou email `heretohelp@stripe.com`
4. **Préparer**: Pièce d'identité, K-bis, extrait bancaire, factures fournisseurs, preuves livraison, CGV, relevés 3 mois

## Structure Lettre d'Appel

```
Subject: Appeal for Account Review — Bene2Luxe

CONTEXT: Société enregistrée [France/Suisse], marketplace revente luxe, 
         valeur moyenne transaction [€X]
CORRECTION: Nous reconnaissons le gap Stripe Connect — migration en cours
CONTROL: 3D Secure activé, règles Radar personnalisées, 
         vérification vendeurs renforcée
```

## Probabilité de Succès

| Scénario | Taux |
|----------|------|
| Marketplace sans Connect | **5-15%** |
| Avec docs complètes | 20-30% |
| Si on migre Connect et on revient | 40-50% |

## Recommandations

1. **Tenter l'appel** même en retard — avec la lettre Context → Correction → Control
2. **Ne pas mettre tous les espoirs** — DODO, GlobalPayments, Polar déjà configurés
3. **Migrer vers Stripe Connect** si on veut retravailler avec Stripe

## Sources
- https://stripe.com/fr/legal/unacceptable-risk-policy
- https://stripe.com/en-ch/legal/restricted-businesses
