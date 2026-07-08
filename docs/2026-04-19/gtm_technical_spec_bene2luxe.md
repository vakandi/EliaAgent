# GTM Technical Specification - Bene2Luxe

**Source**: B2LUXE BUSINESS WhatsApp (19 Avril 2026, 04:40)
**Status**: ACTION REQUIRED

---

## Base technique à mettre en place

### 1. Conteneur Google Tag Manager pour le site
- 1 Google tag central relié à la propriété GA4
- Le tag/GTM doit être présent sur toutes les pages, y compris le checkout et la thank-you page
- Il ne faut pas multiplier les Google tags sur une même page

### 2. dataLayer
- Il faut une dataLayer propre et stable pour pousser les données produit, panier, checkout et achat

### 3. Consentement / conformité
- Mettre une CMP / bannière cookie propre
- Configurer Consent Mode dès le début
- Le tag de consentement doit partir sur Consent Initialization – All Pages
- Les signaux à gérer sont au minimum : ad_storage, analytics_storage, ad_user_data et ad_personalization

### 4. Tags indispensables dans GTM

| Tag | Description |
|-----|-------------|
| Google tag / GA4 | Sur toutes les pages |
| Conversion Linker | Sur toutes les pages |
| Google Ads Conversion | Pour l'achat |
| Enhanced Conversions |	User-Provided Data si on veut améliorer la mesure Google Ads |
| Enhanced Measurement | Activer côté GA4 pour récupérer automatiquement certains événements de base |

### 5. Événements e-commerce GA4 à avoir

```
view_item_list
select_item
view_item
add_to_cart
remove_from_cart
view_cart
begin_checkout
add_shipping_info
add_payment_info
purchase
refund
view_promotion
select_promotion
```

### 6. Ce qu'il faut envoyer dans les events e-commerce

- Un tableau items dans les événements e-commerce
- Un item_id cohérent du listing jusqu'à l'achat
- item_name, item_brand, item_category, item_variant, price, quantity, discount/coupon, currency, value

### 7. Le purchase doit être nickel

- Il doit se déclencher une seule fois
- Il doit contenir un transaction_id unique
- Il doit contenir : value, currency, tax, shipping, coupon, items
- Le plus propre est de le déclencher sur la page de confirmation de commande

### 8. Mapping simple par type de page

| Page Type | Event |
|----------|-------|
| Home / catégories / liste / recherche | view_item_list |
| Clic sur un produit depuis une liste | select_item |
| Page produit | view_item |
| Ajout panier | add_to_cart |
| Panier | view_cart |
| Suppression panier | remove_from_cart |
| Début checkout | begin_checkout |
| Choix livraison | add_shipping_info |
| Choix paiement | add_payment_info |
| Commande validée | purchase |
| Remboursement | refund |
| Bannières / promos internes | view_promotion et select_promotion |

### 9. Google Ads

- Créer la conversion achat dans Google Ads
- La relier au tag GTM avec le bon Conversion ID et Conversion Label
- Garder le Conversion Linker actif sur toutes les pages
- Mettre Enhanced Conversions si possible pour fiabiliser la mesure
- Remarketing dynamique si prévu

### 10. Cas particulier : checkout sur un autre domaine

- Si le checkout est séparé du domaine principal, il faut configurer le cross-domain measurement côté GA4
- Côté Ads, il faut s'assurer que le passage du GCLID / linker soit bien géré entre les domaines

### 11. Tests obligatoires avant mise en prod

- Vérifier dans GTM Preview / Tag Assistant
- Vérifier dans GA4 DebugView
- Contrôler que les événements remontent avec les bons paramètres
- Vérifier qu'il n'y a aucun doublon sur purchase
- Publier le conteneur seulement après validation complète

### 12. À éviter

- Éviter les custom dimensions inutiles
- Éviter les dimensions à forte cardinalité
- Ne pas enregistrer des valeurs trop uniques en custom dimension

### 13. Le minimum vital pour Bene2Luxe

- GTM installé partout
- Consent Mode propre
- GA4 propre
- Conversion Linker
- view_item_list
- select_item
- view_item
- add_to_cart
- begin_checkout
- add_shipping_info
- add_payment_info
- purchase
- refund
- Google Ads purchase conversion
- Enhanced Conversions
- Tests DebugView + Tag Assistant avant publication

---

## Action Required

1. Créer un conteneur GTM pour bene2luxe.com
2. Configurer Consent Mode
3. Implémenter les événements e-commerce GA4 listés ci-dessus
4. Configurer Google Ads conversion
5. Tester avec DebugView + Tag Assistant

---

**Status**: Documenté - Priorité HAUTE pour conversion tracking