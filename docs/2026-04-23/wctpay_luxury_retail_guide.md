# Guide WCT Pay pour la Profession du Luxe
## Solution de Paiement Cryptomonnaie pour la Mode et la Joaillerie de Prestige

*Document de recherche — 23 avril 2026*  
*Contexte: Bene2Luxe (CoFibou Distribution LLC) — France/Suisse — Clientèle fortunée*

---

## 1. Présentation de WCT Pay

**WCT Pay** est un processeur de paiements en cryptomonnaie spécialisé dans les transactions à forte valeur, notamment pour le secteur du luxe. Basé à Brisbane (Australie) et fondé en 2008, WCT Pay permet aux commerces de luxe d'accepter les paiements en cryptomonnaie tout en recevant des fonds en fiat (EUR, USD, GBP, AUD) avec un règlement rapide et une conformité complète KYC/AML.

### Avantages clés pour le luxe

- **Règlement le jour même** (same-day settlement)
- **Pas de chargebacks** — protection thérapeutistique
- **Conformité KYC/AML intégrée**
- **Support OTC pour grosses transactions** (private jet, immobiler, artistiques)
- **Exposition réduite au risque de change**grâce à la conversion automatique

---

## 2. URL d'Application pour le Luxe

| Ressource | URL |
|----------|-----|
| Page principale luxe | https://wctpay.com/luxury-retail |
| Inscription dashboard | https://dashboard.wctpay.com/en/register |
| API & intégration | https://wctpay.com/api-solutions |
| FAQ | https://wctpay.com/faq |
| Blog &actualités | https://wctpay.com/blog |

---

## 3. Cryptomonnaies Supportées

WCT Pay supporte un éventail large d'actifs numériques, incluant:

| Catégorie | Actifs supportés |
|-----------|-----------------|
| **Stablescoins** | USDT, USDC |
| **Crypto principales** | BTC (Bitcoin), ETH (Ethereum) |
| **Altcoins** | SOL, TRX (TRON), XRP, DOGE, LTC |
| **Memes/tokens** | PEPE, SHIB, TRUMP |

> **Note**: D'autres actifs peuvent être activés au cas par cas,取决于 de lajuridiction et du profil KYC/AML du marchand.

---

## 4. Devises de Conversion Automatique

Les paiements en cryptomonnaie sont automatiquement convertis en:

- **USD** (Dollar américain)
- **EUR** (Euro)
- **GBP** (Livre sterling)
- **AUD** (Dollar australien)

Pour Bene2Luxe ciblant la France et la Suisse, **EUR** est la devise de règlement recommandée.

---

## 5. Délais de Règlement (Settlement Timeline)

| Étape | Délai |
|------|-------|
| **Confirmation blockchain** | Temps réel (selon actif) |
| **Conversion crypto→fiat** | Instantanée à confirmation |
| **Virement bancaire** | **Même jour** (same-day) ou 1-2 jours ouvrés |

> **Important**: Le règlement same-day nécessite que l'onboarding soit thérapeutistiquement complété et que le virement respecte les cutoff times bancaires.

---

## 6. Documents Requis pour l'Inscription

### Pour les personnes physiques (individus)

1. **Pièce d'identité valide**:
   - Passeport, carte d'identité nationale, ou permis de conduire
   - Photo claire et valide

2. **Preuve de domicile**:
   - Facture de services publics, relevé bancaire
   - Émise il y a moins de 3 mois
   - Doit correspondre à l'adresse sur la pièce d'identité

3. **Vérification selfie/vidéo** (liveness check) peut être requise

### Pour les personnes morales (entreprises)

Pour CoFibou Distribution LLC, documents supplémentaires:

- **Certificat d'enregistrement de l'entreprise**
- **Statuts de la société**
- **Documents KYC des administrateurs/directeurs** (piece d'identité + preuve de domicile)
- **Relevé bancaire d'entreprise** (pour vérification du compte de règlement)

### Délai d'approbation

- **24 à 48 heures** en moyenne
-varie selon la juridiction et la complétude des documents

---

## 7. Exigences KYC/AML

WCT Pay intègre nativement la conformité KYC/AML:

| Exigence | Description |
|----------|-------------|
| **KYC marchand** | Vérification'identité et adresse lors de l'onboarding |
| **AML screening** | Vérification anti-blanchiment sur les transactions |
| **Liste de sanctions** | Contrôle des dresseers contre les listes OFAC, UE, etc. |
| **Limites par transaction** | Configurables selon le profil du marchand |
| **Approbation pour gros montants** | Ex: > 250 000 $ nécessite double approbation |

- **Juridictions supportées**: UE, Australie, Royaume-Uni, Asie
- **Conformité GDPR**: Protection des données personnelles incluse

---

## 8. Frais et Tarification

> **Note**: WCT Pay ne publie pas de grile de tarifs publics. Les frais varient selon:

- **Actif crypto utilisé** (frais de réseau blockchain)
- **Volume de transactions**
- **Devise de règlement**
- **Type d'intégration** (API, invoicing, OTC)

### Structure habituelle (renseignements à confirmer avec l'équipe commerciale)

| Composante | Description |
|-----------|-------------|
| **Frais par transaction** | Pourcentage sur le montant (varie) |
| **Frais de réseau** | Frais blockchain (gas fees) |
| **Spread FX** | Marge sur le taux de change crypto→fiat |
| **Frais de retrait** | Variables selon la méthode |

### Devis personnalisé

Pour obtenir un devis adapté au volume estimé de Bene2Luxe:

> **Contact commercial**: info@wctpay.com

---

## 9. Coordonnées de l'Équipe Commerciale

| Service | Contact |
|---------|---------|
| **Commercial / Nouveau client** | info@wctpay.com |
| **Support existant** | support@wctpay.com |
| **Formulaire de contact** | https://wctpay.com/#contact |

### Processus de contact recommandé

1. Envoyer un email à **info@wctpay.com** avec:
   - Nom de l'entreprise: **CoFibou Distribution LLC**
   - Secteur: **Luxury Fashion Resale (luxe/mode)**
   - Volume mensuel estimé (CHF/EUR)
   - Devise de règlement souhaitée: **EUR**
   - Besoins d'intégration: **WooCommerce / API**

2. Demander un **demo account** et la **documentation API**

3. Obtenir une **proposition tarifaire personnalisée**

---

## 10. Options d'Intégration WooCommerce/Plugin

### WooCommerce

WCT Pay **ne propose pas de plugin WooCommerce officiel** prêt-à-installer. L'intégration s'effectue via:

| Option | Description |
|--------|-------------|
| **API Checkout** | Intégration via API REST — nécessite的开发 |
| **Hosted Checkout** | Redirection vers la page de paiement WCT Pay |
| **Invoicing** | Génération de factures crypto (liens partagés) |

> **Alternative WooCommerce**: Pour une solution plugin prête, voir CryptAPIpayment gateway (https://wordpress.org/plugins/cryptapi-payment-gateway-for-woocommerce/) — à titre comparatif.

### Shopify

Shopify ne propose pas d'intégration directe WCT Pay. Les options:

1. **API Shopify** + **API WCT Pay** → développement custom
2. **Application middle-tier** (zapier, make.com) pour automate
3. **BitPay ou Crypto.com** — alternatives avec plugins Shopify

### Recommandation technique

Pour Bene2Luxe, l'approche recommandée:

```
WooCommerce → Plugin personnalisé (API WCT Pay) → Auto-conversion EUR → Compte bancaire
```

ou

```
WooCommerce → API WCT Pay (Hosted Checkout) → Redirection client
```

---

## 11. Récapitulatif pour Bene2Luxe

| Élément | Recommandation |
|--------|---------------|
| **Inscription** | https://dashboard.wctpay.com/en/register |
| **Devise de règlement** | EUR (cible France/Suisse) |
| **Cryptomonnaies à activer** | USDT, USDC, BTC, ETH (priorité) |
| **Intégration** | API checkout + WooCommerce custom |
| **Contact commercial** | info@wctpay.com |
| **Onboarding attendu** | 3-5 jours avec documents complets |
| **Frais** | Sur devis — contacter le commercial |

---

## 12. Prochaines Étapes Suggérées

1. **Préparer les documents CoFibou Distribution LLC**:
   - Certificat d'enregistrement (TRN UAE / RCS France)
   - Pièces d'identité des directeurs
   - Relevé bancaire d'entreprise

2. **Contacter WCT Pay**:
   - Email: info@wctpay.com
   - Objet: "Demande de devis — CoFibou Distribution LLC (Luxury Fashion)"

3. **Demander**:
   - Accès sandbox/démo
   - Documentation technique API
   - Grile tarifaire personnalisée

4. **Tester l'intégration**:
   - Mode sandbox
   - Paiement test en USDT → conversion EUR

---

*Document généré le 23 avril 2026 — Recherche: wctpay.com*
*Langue: Français*
*Usage interne — Bene2Luxe (CoFibou Distribution LLC)*
