# Recherche Détaillée: OceanPayment & Uniq Payments

**Date**: 12 Mai 2026
**Contexte**: BEN-28 (Stripe fermé), BEN-31 (Uniq Payments), BEN-33 (OceanPayment)
**Client**: Cofibou Distribution LLC / Bene2Luxe

---

## 1. OceanPayment.com (BEN-33)

### Overview
| Détail | Info |
|--------|------|
| **Fondé** | 2014 (Hong Kong) |
| **Certification** | PCI DSS Level 1, Visa/Mastercard Principal Member |
| **Méthodes** | 500+ payment methods, 230+ pays, 140+ devises |
| **Documentation API** | https://dev.oceanpayment.com/en/ (V4.0) |
| **GitHub** | https://github.com/Oceanpayment (34 repos, PHP SDK) |
| **Node.js** | `npm i oceanpayment` (community, non-officiel) |

### Intégration Next.js/React
OceanPayment propose **5 méthodes d'intégration**: Embedded (JS SDK), Hosted Checkout, Server-to-Server, Payment Link, POS.

**Recommandé pour Bene2Luxe**: **Embedded JS SDK** (pas de redirection, carte + Google Pay + Apple Pay)
1. Charger jQuery + SDK JS sur la page checkout
2. Créer signature SHA-256 côté serveur (Next.js Route Handler)
3. Initialiser avec `Oceanpayment.init(true, '', '')`
4. Configurer webhook pour notifications `noticeUrl`

### Frais (estimation)
- **Transaction**: 3.0% - 5.0% + $0.30-$0.50 (cross-border, high-risk)
- **Réserve**: 5-10% pour 180 jours
- **Settlement initial**: T+10 (peut améliorer à T+3)
- **Frais mensuels**: Non publiés, à négocier

### Documentation requise (KYC lourd)
- Articles of Organization (Wyoming)
- EIN confirmation letter (IRS)
- Operating Agreement
- Passeport director/UBO
- Justificatif de domicile
- Compte bancaire professionnel
- Photos bureau (même home office)
- Facture domaine
- Info logistique

### Action requise
1. Contacter `globalsales@oceanpayment.com` pour un devis US
2. Collecter tous les docs KYC (1-2 semaines)
3. Budget 2-4 semaines pour approbation

---

## 2. Uniq Payments (BEN-31)

### Overview
| Détail | Info |
|--------|------|
| **Type** | Courtier en paiements high-risk (pas un gateway direct) |
| **Site** | https://uniqpayments.com / https://uniqpayments.net |
| **Contact** | @uniqpayments_new (Telegram, canal principal) |
| **Personne directe** | @michael_uniqpayment (Telegram) / `MichaelUniq.24` (Signal) |
| **Email** | support@uniqpayments.net |
| **Trustpilot** | 4.0/5 (positif) |
| **Actif depuis** | ~2018 (7+ ans) |

### Ce qu'ils offrent
Ils vendent des **packages clé en main** pour merchants high-risk:
- ✅ Compte Stripe/PayPal/Airwallex **pré-vérifié**
- ✅ Constitution de société (UK, HK, Estonie, Irlande, Singapour)
- ✅ Compte bancaire ou EMI (Payoneer, Wise, Airwallex)
- ✅ Directeur nominal (nominee director)
- ✅ Site web proxy + cloaking
- ✅ Garantie de remplacement si banni

### Prix
| Package | Prix | Délai |
|---------|------|-------|
| **UK LTD** | **$2,500 - $3,100** | 14-18 jours |
| **Hong Kong** | **$4,900** | 3-4 semaines |
| **Estonie** | **$3,900** | 14-18 jours |
| **Singapour** | **$7,900** | 2 mois |

### ⚠️ Points importants
Uniq Payments est un **revendeur de comptes Stripe** avec cloaking. Cela signifie:
- ✅ Solution rapide si tous les processeurs traditionnels refusent
- ✅ Garantie de remplacement si Stripe ferme le compte
- ⚠️ Contre les ToS de Stripe (risque de fermeture + fonds bloqués)
- ⚠️ Prix élevé ($2,500-$7,900 en une fois)
- ⚠️ Solution "grise" juridiquement

### Action requise
1. Contacter **@uniqpayments_new** sur Telegram
2. Dire: "Luxury fashion resale (bene2luxe.com), besoin package UK ou HK"
3. Attendre leur réponse pour un devis précis
4. Préparer budget $2,500-$4,900

---

## 3. Recommandation pour Bene2Luxe

### Hiérarchie des actions
1. **Priorité 1**: Contacter Uniq Payments (@uniqpayments_new) → solution la plus rapide
2. **Priorité 2**: Contacter OceanPayment (globalsales@oceanpayment.com) → solution légitime mais KYC lourd
3. **Alternative**: NexaPay (1-3% fees, crypto, pas de KYC) si urgence

### Étapes immédiates pour Wael
1. Envoyer message Telegram à @uniqpayments_new avec descriptif business
2. Rassembler documents Wyoming LLC pour OceanPayment (en parallèle)
3. Décider du budget ($2,500-$4,900 pour Uniq vs gratuit pour OceanPayment + frais)

---

**Documents préparés par Elia - 12 Mai 2026**
