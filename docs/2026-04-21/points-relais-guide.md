# 📦 Guide Complet - Comptes Points Relais France & Suisse

**Bene2Luxe** - Luxury Fashion Resale
**Date**: 21 Avril 2026
**Status**: Recherche terminée, inscription en cours

---

## 🇫🇷 1. MONDIAL RELAY (France)

### Site Web
- **Portail Pro**: https://www.mondialrelay.com/ww2/lg_fr/espaces/enseigne/h_identification.aspx
- **Contact**: offrestart@mondialrelay.fr
- **Téléphone**: 09 69 32 23 32 (option 5 pour e-commerce)

### Processus d'Inscription
1. Remplir le formulaire en ligne sur le portail
2. Soumettre les informations entreprise
3. Attendre validation (quelques jours)
4. Recevoir **Code Enseigne** + **Clé Privée** pour API

### Informations à Fournir
| Champ | Valeur |
|-------|-------|
| Nom société | COBOU AGENCY LLC |
| Personne à contacter | Bousfira Wael |
| Email | contact@cofibou-distribution.com |
| Adresse | 34 N Franklin Ave Ste 687 |
| Code postal | 82001 |
| Ville | Pinedale |
| Pays | États-Unis |
| Téléphone | +212 6XX XXX XXX |

### ⚠️ Note Importante
Pour une entreprise US (Wyoming LLC) qui expédie en France:
- Nécessite un **numéro de TVA intra-UE** pour les expéditions intra-UE
- Peut nécessiter un représentant fiscal en France
- Le formulaire a été soumis - en attente de confirmation

### Solutions API
| API | Version | Documentation |
|-----|---------|-------------|
| API V1 (SOAP) | V-5.12 | Recherche points relais, génération étiquettes |
| API V2 (REST) | 2024 | Création expéditions, livraison domicile |
| Module Shopify | Officiel | App Store Shopify |
| Module PrestaShop | Officiel | mondialrelay-wp.com |

---

## 🇫🇷 2. LA POSTE France (Points Relais + Colissimo)

### Site Web
- **Portail Pro**: https://www.laposte.fr/pro
- **Compte Pro**: https://www.laposte.fr/pro (Créer un compte Pro)
- **E-commerce**: https://www.laposte.fr/professionnel/envoi-colis/expeditions-e-commerce
- **Contact Email**: support.api@laposte.fr
- **Téléphone Pro**: 09 69 39 36 99

### Processus d'Inscription
1. Créer un Compte Pro sur laposte.fr/pro
2. Pour entreprises US (sans SIRET): demander un **Numéro Client (Coclico)**
3. Souscrire à Colissimo Business
4. Recevoir les identifiants API

### ⚠️ Note Importante - Entreprises Étrangères
Les entreprises US (non françaises) ne peuvent PAS utiliser de SIRET.
**Solution**: Demander un Numéro Client La Poste (Coclico):
- Email: via formulaire https://aide.laposte.fr/professionnel/email
- OU courrier: LA POSTE, St Brieuc ADV, 22035 ST BRIEUC CEDEX 1
- Délai: ~2 jours ouvrés

### Documents Requis (Entreprise US)
| Document | Notes |
|----------|-------|
| Certificat d'immatriculation | Wyoming Certificate of Incorporation |
| EIN (Tax ID US) | Federal Tax ID |
| Numéro TVA intra-UE | Requis pour expéditions intra-UE |
| Justificatif adresse | Registered agent address |

### Réseau Points Relais France
| Réseau | Points | Notes |
|--------|--------|-------|
| Bureaux de Poste | ~8,000 | Service complet |
| Pickup Relais | ~17,000 | Commerces partenaires |
| Consignes | ~4,000 | Pickup automatisés 24/7 |
| **Total France** | **~25,000** | Largest réseau |

### Options API La Poste
| API | Usage |
|-----|-------|
| Colissimo API | Étiquettes, suivi, tarifs |
| Point Retrait API | Affichage points relais |
| API Affranchissement | Lettres recommandées |
| Web Service Tracking | Suivi timeline |

---

## 🇨🇭 3. SWISS POST (La Poste Suisse)

### Site Web
- **Portail Business**: https://www.post.ch/en/business-solutions/become-a-business-customer
- **My Post Login**: https://account.post.ch/selfadmin/company-management/
- **SwissID Registration**: https://login.swissid.ch/login/registration/
- **Developer Portal**: https://developer.post.ch/en/digital-commerce-api
- **Contact**: sme@swisspost.ch
- **Téléphone SME**: +41 58 667 85 91

### Processus d'Inscription
1. Créer un compte **SwissID** (compte business)
2. Se connecter à My Post: https://account.post.ch
3. Demander une relation de facturation (Rechnungsbeziehung)
4. Obtenir une Frankierlizenz (licence d'affranchissement)

### ⚠️ Note Importante - Entreprises Étrangères
Pour une entreprise US vendant en Suisse:
- Peut nécessiter un **numéro d'entreprise suisse** (UID) si établissement permanent
- La TVA suisse peut s'appliquer
- Contactez le SME Contact Center pour guidance

### Réseau Pickup Suisse
| Service | Points | Notes |
|---------|--------|-------|
| PickPost | 2,700+ | Points dans agences + partenaires |
| My Post 24 | 320+ | Consignes 24/7 |
| Bureaux postaux | 760 | Service complet avec conseil |
| My Post Service | 2,500+ | Commerces, stations-service |
| **Total** | **5,000+** | Excellent couverture |

### Options API Swiss Post
| API | Usage |
|-----|-------|
| Address API | Validation adresses |
| Delivery API | Disponibilité livraison |
| PickPost API | Intégration points pickup |
| Barcode API | Génération étiquettes |
| Shipping Options API | Fenêtres de livraison |
| DataTransfer | Échange bulk via SFTP |

---

## 📋 Résumé - Action Items

| Prestataire | Status | Action Requise | Priorité |
|------------|--------|---------------|---------|
| **Mondial Relay** | ✅ Formulaire soumis | Attendre confirmation email | HAUTE |
| **La Poste France** | 🔄 À faire | Créer compte Pro + demander Coclico | MOYENNE |
| **Swiss Post** | 🔄 À faire | Contacter SME + créer SwissID | MOYENNE |

### Prochaines Étapes
1. ✅ **Mondial Relay**: Attendre email de confirmation (1-3 jours)
2. 🔄 **La Poste France**: Créer compte Pro + demander Numéro Client
3. 🔄 **Swiss Post**: Appeler SME (+41 58 667 85 91) pour guidance entreprise US
4. 📋 **TVA Intra-UE**: Vérifier si déjà possédé (requis pour tous)

---

## 📁 Documents de Référence

- Screenshots: `/Users/vakandi/EliaAI/docs/2026-04-21/mondialrelay_*.png`
- Source: Agents librarian (recherche complète)

---

**Mis à jour**: 21 Avril 2026
**Prochaine vérification**: 24 Avril 2026