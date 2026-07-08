# FreeKassa - Guide d'Intégration COMPLET pour Bene2Luxe

**Date:** 2026-04-25  
**Contexte:** Stripe banni → Alternative: FreeKassa acceptée

---

## 📋 Résumé

FreeKassa est un provider de paiement russe qui accepte:
- ✅ Cartes Visa/MasterCard
- ✅ Apple Pay (ID: 38)
- ✅ Google Pay (ID: 37)
- ✅ Cryptos (USDT, BTC, ETH)
- ✅ Qiwi, Yoomoney, etc.

**Devises supportées:** RUB, USD, EUR, UAH, KZT

---

## 🗂️ Implémentation Bene2Luxe - Chemins de Fichiers

### Structure du Projet

```
/Users/vakandi/DultiSaasDeploy/bene2luxe/
├── backend/
│   ├── routers/
│   │   ├── payments_dodo.py      ← Dodo (carte)
│   │   ├── payments_cryptomus.py ← Crypto
│   │   └── core/payments.py       ← Router principal
│   ├── services/
│   │   └── core/
│   │       ├── payment_providers.py  ← Abstraction providers
│   │       └── payment_service.py  ← Logique paiement
│   └── main.py                   ← Enregistrement routes
│
├── frontend_build/
│   └── src/
│       ├── components/
│       │   └── PaymentMethodSelector.tsx  ← Choix paiement
│       ├── pages/
│       │   ├── Checkout.tsx              ← Page checkout
│       │   ├── PaymentSuccess.tsx         ← Success
│       │   └── PaymentFailed.tsx          ← Fail
│       └── lib/
│           ├── paymentHandlers.ts      ← Logique paiement
│           └── paymentOpen.ts       ← Ouverture paiement
```

---

## 🔧 Étapes d'Implémentation

### Étape 1: Ajouter les nouvelles méthodes de paiement

**Fichier:** `frontend_build/src/components/PaymentMethodSelector.tsx`

**Ligne 5:** Ajouter les types:
```typescript
export type PaymentMethod = 'balance' | 'dodo' | 'freekassa_card' | 'freekassa_apple_pay' | 'freekassa_google_pay' | 'cryptomus' | 'bank_transfer' | 'wise_manual' | 'revolut_manual'
```

**Ligne 34-70:** Ajouter les options (aprèdodo, avant cryptomus):
```typescript
{
  id: 'freekassa_card',
  label: 'Carte Bancaire',
  description: lang === 'fr' ? 'Visa, Mastercard' : 'Visa, Mastercard',
  icon: <CreditCard className="h-5 w-5" />,
  accent: 'from-blue-500 to-blue-600',
  requiresAuth: false
},
{
  id: 'freekassa_apple_pay',
  label: 'Apple Pay',
  description: lang === 'fr' ? 'Paiement rapide' : 'Fast payment',
  icon: <CreditCard className="h-5 w-5" />,
  accent: 'from-gray-500 to-gray-600',
  badge: lang === 'fr' ? 'Instantané' : 'Instant',
  requiresAuth: false
},
{
  id: 'freekassa_google_pay',
  label: 'Google Pay',
  description: lang === 'fr' ? 'Paiement rapide' : 'Fast payment',
  icon: <CreditCard className="h-5 w-5" />,
  accent: 'from-green-500 to-blue-500',
  badge: lang === 'fr' ? 'Instantané' : 'Instant',
  requiresAuth: false
},
```

### Étape 2: Modifier le Backend - Nouveau Router

**Fichier:** `backend/routers/payments_freekassa.py`

Créer nouveau fichier (inspiré de payments_dodo.py):
- Route `/api/payments/freekassa/create-session` - Crée lien paiement FreeKassa
- Route `/api/payments/freekassa/webhook` - Callback FreeKassa
- Route `/api/payments/freekassa/success` - Page success
- Route `/api/payments/freekassa/failed` - Page failed

**Configuration .env:**
```bash
FREEKASSA_MERCHANT_ID=12345
FREEKASSA_SECRET_WORD_1=secret1
FREEKASSA_SECRET_WORD_2=secret2
FREEKASSA_API_KEY=api_key
FREEKASSA_RETURN_URL=https://bene2luxe.com/payment/success
FREEKASSA_CANCEL_URL=https://bene2luxe.com/payment/failed
```

### Étape 3: Enregistrer la Route

**Fichier:** `backend/main.py`

Ajouter l'enregistrement:
```python
from routers.payments_freekassa import router as frekassa_router
app.include_router(freekassa_router, prefix="/api/payments/freekassa", tags=["payments-freekassa"])
```

### Étape 4: Mettre à jour le Provider Abstraction

**Fichier:** `backend/services/core/payment_providers.py`

Ajouter:
```python
class FreeKassaPaymentProvider(PaymentProvider):
    """FreeKassa implementation"""
    
    def __init__(self, merchant_id, secret_word, api_key):
        self.merchant_id = merchant_id
        self.secret_word = secret_word
        self.api_key = api_key
    
    async def create_payment_session(self, amount, currency, order_reference, payment_method='card', **kwargs):
        """Créer session FreeKassa"""
        import httpx
        import hashlib
        
        # Mapper payment_method vers ID FreeKassa
        method_ids = {'card': '36', 'apple_pay': '38', 'google_pay': '37'}
        method_id = method_ids.get(payment_method, '36')
        
        # Signature MD5
        sign_str = f"{self.merchant_id}:{amount}:{self.secret_word}:{currency}:{order_reference}"
        signature = hashlib.md5(sign_str.encode()).hexdigest()
        
        # URL paiement
        payment_url = (
            f"https://pay.fk.money/?"
            f"m={self.merchant_id}&"
            f"oa={amount}&"
            f"o={order_reference}&"
            f"s={signature}&"
            f"currency={currency}&"
            f"i={method_id}&"
            f"em={kwargs.get('email', '')}&"
            f"lang=en"
        )
        
        return {
            'payment_url': payment_url,
            'provider_reference': order_reference,
            'provider': 'freekassa'
        }
```

### Étape 5: Mettre à jour paymentHandlers.ts

**Fichier:** `frontend_build/src/lib/paymentHandlers.ts`

Ajouter le handler pour les nouvelles méthodes:
```typescript
case 'freekassa_card':
case 'freekassa_apple_pay':
case 'freekassa_google_pay':
  method = method.replace('freekassa_', '') // card, apple_pay, google_pay
  // Appeler API backend
  const response = await fetch('/api/payments/freekassa/create-session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      amount: total,
      order_id: orderId,
      email: customerEmail,
      payment_method: method // 'card', 'apple_pay', 'google_pay'
    })
  });
  const { url } = await response.json();
  window.location.href = url;
  break;
```

### Étape 6: Configurer Apache

**Fichier:** Config Apache e-probook.site ou bene2luxe

Ajouter:
```apache
# FreeKassa callback et pages
ProxyPass /payment/notification http://b2l-backend:8000/api/payments/freekassa/webhook
ProxyPassReverse /payment/notification http://b2l-backend:8000/api/payments/freekassa/webhook

ProxyPass /payment/success http://b2l-frontend:3000/payment/success
ProxyPassReverse /payment/success http://b2l-frontend:3000/payment/success

ProxyPass /payment/failed http://b2l-frontend:3000/payment/failed
ProxyPassReverse /payment/failed http://b2l-frontend:3000/payment/failed
```

### Étape 7: Configurer Dashboard FreeKassa

Dans https://merchant.freekassa.net/:

| URL | Valeur |
|-----|-------|
| URL Notification | `https://e-probook.site/freekassa/payment/notification` |
| URL Success | `https://e-probook.site/freekassa/payment/success` |
| URL Failed | `https://e-probook.site/freekassa/payment/failed` |
| Méthode notification | POST |

⚠️ Cocher "Подтверждение платежа" pour recevoir "YES" en réponse.

## ⚠️ Conflit avec Chemins Existants - Solution

### Chemins Actuels (DODO)

DansApache config:
- `/payment` → frontend
- `/dodo/payment/success` → redirect
- `/premium/payment-success` → frontend

**RISQUE:** Conflit avec FreeKassa!

### ✅ Solution: Chemins avec Préfixe `/freekassa/`

Pour éviter le conflit, utiliser ces chemins spécifiques FreeKassa:

| Service | Chemin e-probook | Backend |
|--------|-----------------|---------|
| Webhook | `/freekassa/payment/notification` | `/api/payments/freekassa/webhook` |
| Success | `/freekassa/payment/success` | Frontend /payment-success |
| Failed | `/freekassa/payment/failed` | Frontend /payment-failed |

### Configuration Apache (AVEC préfixe)

```apache
# FreeKassa - AVEC préfixe pour éviter conflit
ProxyPass /freekassa/payment/notification http://backend:5000/api/payments/freekassa/webhook
ProxyPassReverse /freekassa/payment/notification http://backend:5000/api/payments/freekassa/webhook

ProxyPass /freekassa/payment/success http://frontend:8000/payment-success
ProxyPassReverse /freekassa/payment/success http://frontend:8000/payment-success

ProxyPass /freekassa/payment/failed http://frontend:8000/payment-failed
ProxyPassReverse /freekassa/payment/failed http://frontend:8000/payment-failed
```

### Configuration Dashboard FreeKassa (AVEC préfixe)

| URL | Valeur |
|-----|-------|
| URL Notification | `https://e-probook.site/freekassa/payment/notification` |
| URL Success | `https://e-probook.site/freekassa/payment/success` |
| URL Failed | `https://e-probook.site/freekassa/payment/failed` |

---

## 🎯 Ordre d'Affichage Checkout

**Page:** `bene2luxe.com/checkout`

Ordre actuel (dans PaymentMethodSelector.tsx ligne 34-70):

1. **Solde** (authentifié)
2. **Carte Bancaire** (dodo)
3. **Bitcoin** (cryptomus)
4. **Virement Bancaire**

NOUVEL ORDRE avec FreeKassa:

1. **Solde** (authentifié)
2. **Carte Bancaire** (freekassa_card)
3. **Apple Pay** (freekassa_apple_pay) ← NOUVEAU
4. **Google Pay** (freekassa_google_pay) ← NOUVEAU
5. **Bitcoin** (cryptomus)
6. **Virement Bancaire**

---

## 📝 Checklist Implémentation

- [ ] **Frontend** - Ajouter 3 nouvelles options dans PaymentMethodSelector.tsx
- [ ] **Backend** - Créer payments_freekassa.py avec routes
- [ ] **Backend** - Ajouter FreeKassaPaymentProvider dans payment_providers.py
- [ ] **Backend** - Enregistrer route dans main.py
- [ ] **Config** - Ajouter variables .env
- [ ] **Apache** - Configurer proxy /payment/*
- [ ] **Dashboard** - Configurer URLs FreeKassa
- [ ] **Test** - Mode sandbox

---

## 🔧 Paramètres du Compte

Dans le dashboard FreeKassa (https://merchant.freekassa.net/):

| Paramètre | Description |
|-----------|-------------|
| Merchant ID | ID de votre boutique |
| Secret Word 1 | Pour signature du formulaire |
| Secret Word 2 | Pour vérification callback |
| API Key | Pour les appels API |
| URL Notification | Callback pour confirmer paiement |
| URL Success | Page après paiement réussi |
| URL Fail | Page après échec |

**IPs autorisées pour callbacks:** 168.119.157.136, 168.119.60.227, 178.154.197.79, 51.250.54.238

---

## 🏗️ Architecture e-probook.site (Site Miroir)

**Contexte:** e-probook.site = site miroir avec Apache → Bene2Luxe (vrai site)

### URLs FreeKassa dans le dashboard:

| URL | Purpose | Direction |
|-----|---------|------------|
| `https://e-probook.site/payment/notification` | **Webhook** - POST de FreeKassa quand paiement validé | Machine → Backend |
| `https://e-probook.site/payment/success` | Client redirigé après paiement OK | Client → Frontend |
| `https://e-probook.site/payment/failed` | Client redirigé si échec paiement | Client → Frontend |

### ⚠️ Configuration Apache REQUISE

Il faut que Apache redirige `/payment/*` vers le backend B2L. Dans la config Apache d'e-probook.site:

```apache
# FreeKassa callback - vers API backend
ProxyPass /payment/notification http://b2l-backend:8000/api/freekassa/callback
ProxyPassReverse /payment/notification http://b2l-backend:8000/api/freekassa/callback

# Pages success/fail - vers frontend
ProxyPass /payment/success http://b2l-frontend:3000/payment/success
ProxyPassReverse /payment/success http://b2l-frontend:3000/payment/success

ProxyPass /payment/failed http://b2l-frontend:3000/payment/failed
ProxyPassReverse /payment/failed http://b2l-frontend:3000/payment/failed
```

**OU** si tout passe par l'API:
```apache
# Tout /payment/* vers le backend
ProxyPass /payment/ http://b2l-backend:8000/payment/
ProxyPassReverse /payment/ http://b2l-backend:8000/payment/
```

**Ordre IMPORTANT:** `/payment/` doit être défini AVANT `/api/` sinon `/` capture tout.

### Flux:

1. Client clique "Payer" → Backend génère lien FreeKassa
2. Client redirect vers `https://pay.fk.money/...`
3. Client paie → FreeKassa POST vers `/payment/notification` (Apache proxy vers B2L API)
4. B2L API valide → met à jour commande dans BDD → répond "YES"
5. Client redirect vers `/payment/success` ou `/payment/failed`

---

## 💳 Méthode 1: Formulaire SCI (Simple)

Rediriger le client vers:
```
https://pay.fk.money/?m={MERCHANT_ID}&oa={AMOUNT}&o={ORDER_ID}&s={SIGNATURE}&currency={EUR|USD}
```

### Signature (MD5):
```php
$sign = md5($merchant_id . ':' . $amount . ':' . $secret_word . ':' . $currency . ':' . $order_id);
```

### Paramètres:

| Param | Obligatoire | Description |
|-------|-------------|-------------|
| m | ✅ | Merchant ID |
| oa | ✅ | Montant |
| o | ✅ | Numéro commande |
| s | ✅ | Signature |
| currency | ✅ | EUR/USD/RUB |
| em | ❌ | Email client |
| phone | ❌ | Téléphone |
| lang | ❌ | Langue (en/ru) |

### 💳 Pré-sélectionner Apple Pay ou Google Pay

Pour afficher directement Apple Pay ou Google Pay sur la page de paiement, utiliser le paramètre `i`:

| Valeur `i` | Méthode affichée |
|-------------|-----------------|
| `i=36` | Carte bancaire (Card) |
| `i=37` | Google Pay |
| `i=38` | Apple Pay |
| `i=4` | VISA RUB |
| `i=32` | VISA USD |

**Exemple avec Apple Pay:**
```php
$payment_url = "https://pay.fk.money/?m={$MERCHANT_ID}&oa={$amount}&o={$order_id}&s={$sign}&currency=EUR&i=38&em={$email}";
// URL: https://pay.fk.money/?m=123&oa=99.99&o=ORD-123&s=abc...&currency=EUR&i=38&em=client@email.com
// → Affiche directement Apple Pay
```

**Exemple avec Google Pay:**
```php
$payment_url = "https://pay.fk.money/?m={$MERCHANT_ID}&oa={$amount}&o={$order_id}&s={$sign}&currency=EUR&i=37&em={$email}";
// → Affiche directement Google Pay
```

**Sans pré-selection (choix client):**
```php
$payment_url = "https://pay.fk.money/?m={$MERCHANT_ID}&oa={$amount}&o={$order_id}&s={$sign}&currency=EUR&em={$email}";
// → Page avec tous les moyens de paiement disponibles
```

---

## 🔌 Méthode 2: API REST (Avancée)

**Base URL:** `https://api.fk.life/v1/`

### Signature (HMAC SHA256):
```php
$data = [
    'shopId' => $shop_id,
    'nonce' => time(),
];
ksort($data);
$sign = hash_hmac('sha256', implode('|', $data), $api_key);
$data['signature'] = $sign;
```

### Endpoints:

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/orders/create` | Créer commande → obtenir lien paiement |
| POST | `/orders` | Liste commandes |
| POST | `/orders/refund` | Effectuer remboursement |
| POST | `/balance` | Voir balance |
| POST | `/currencies` | Méthodes disponibles |

### Créer une commande (exemple):
```bash
curl -X POST https://api.fk.life/v1/orders/create \
  -H "Content-Type: application/json" \
  -d '{
    "shopId": 12345,
    "nonce": 1700000000,
    "signature": "abc123...",
    "paymentId": "ORDER-123",
    "i": 36,
    "email": "client@email.com",
    "ip": "1.2.3.4",
    "amount": 99.99,
    "currency": "EUR"
  }'
```

### Réponse:
```json
{
  "type": "success",
  "orderId": 123,
  "orderHash": "abc123...",
  "location": "https://pay.freekassa.net/form/123/abc123..."
}
```

---

## 🎯 IDs Méthodes de Paiement

| ID | Méthode |
|----|---------|
| 36 | Card RUB API |
| 37 | Google Pay |
| 38 | Apple Pay |
| 4 | VISA RUB |
| 8 | MasterCard RUB |
| 32 | VISA USD |
| 41 | VISA/MasterCard KZT |

---

## 🔔 Callback (Webhook)

### URL appelée après paiement:
```
POST https://tonsite.com/api/freekassa/callback
```

### Données reçues:
```
MERCHANT_ID=123
AMOUNT=99.99
intid=456789
MERCHANT_ORDER_ID=ORDER-123
P_EMAIL=client@email.com
SIGN=md5_hash
```

### Vérification signature:
```php
$sign = md5($merchant_id . ':' . $amount . ':' . $secret_word_2 . ':' . $order_id);
if ($sign !== $_REQUEST['SIGN']) {
    die('Wrong signature');
}
// Confirmer le paiement dans ton système
die('YES');
```

### Statuts commandes:
| Code | Statut |
|------|--------|
| 0 | Nouveau |
| 1 | Payé ✅ |
| 6 | Remboursement |
| 8 | Erreur |
| 9 | Annulé |

---

## 🔨 Implémentation Bene2Luxe (FastAPI)

### Architecture comme Stripe/Dodo/Cryptomus existants

Le webhook FreeKassa doit fonctionner COMME leswebhooks existants - même logique:

1. Route FastAPI reçoit POST
2. Valide signature
3. Met à jour commande dans BDD (Directus)
4. Répond "YES" à FreeKassa

### Backend (FastAPI - même pattern que Stripe):

```python
from fastapi import APIRouter, Request, HTTPException, Response
from directus import directus_client
import hashlib
import os

router = APIRouter(prefix="/api/freekassa", tags=["payments"])

# Config depuis .env
MERCHANT_ID = os.getenv("FREEKASSA_MERCHANT_ID")
SECRET_WORD_1 = os.getenv("FREEKASSA_SECRET_WORD_1")  # Pour form
SECRET_WORD_2 = os.getenv("FREERKASSA_SECRET_WORD_2")  # Pour callback
FREEKASSA_IP_WHITELIST = ["168.119.157.136", "168.119.60.227", "178.154.197.79", "51.250.54.238"]


def verify_freekassa_ip(client_ip: str) -> bool:
    """Vérifie IP auteur du webhook (comme Stripe)"""
    return client_ip in FREEKASSA_IP_WHITELIST


def verify_signature(merchant_id: str, amount: str, order_id: str, signature: str, secret: str) -> bool:
    """
    Vérifie signature MD5
    Format: MD5(merchant_id:amount:secret:currency:order_id)
    Pour EUR: MD5(123:99.99:secret:EUR:order-123)
    """
    sign_str = f"{merchant_id}:{amount}:{secret}:EUR:{order_id}"
    expected = hashlib.md5(sign_str.encode()).hexdigest()
    return expected == signature


async def update_order_status(order_id: str, status: str = "paid"):
    """Met à jour commande dans Directus (même logique que Stripe)"""
    async with directus_client() as dc:
        await dc.update_item("orders", order_id, {
            "status": status,
            "payment_status": "paid",
            "paid_at": "now()"
        })


@router.post("/create-order")
async def create_freekassa_order(
    amount: float,
    email: str,
    order_id: str,
    currency: str = "EUR",
    payment_method: str = "card"  # "card", "apple_pay", "google_pay"
):
    """
    Crée commande et retourne URL de paiement FreeKassa
    
    payment_method options:
    - "card" → i=36 (défaut)
    - "apple_pay" → i=38
    - "google_pay" → i=37
    """
    # Mapper payment_method vers ID FreeKassa
    method_ids = {
        "card": "36",
        "apple_pay": "38",
        "google_pay": "37"
    }
    method_id = method_ids.get(payment_method, "36")
    
    # Signature pour le formulaire
    sign_str = f"{MERCHANT_ID}:{amount}:{SECRET_WORD_1}:{currency}:{order_id}"
    signature = hashlib.md5(sign_str.encode()).hexdigest()
    
    # URL FreeKassa avec méthode pré-sélectionnée
    payment_url = (
        f"https://pay.fk.money/?"
        f"m={MERCHANT_ID}&"
        f"oa={amount}&"
        f"o={order_id}&"
        f"s={signature}&"
        f"currency={currency}&"
        f"i={method_id}&"
        f"em={email}&"
        f"lang=en"
    )
    Body: {"amount": 99.99, "email": "client@email.com", "order_id": "ORD-123"}
    """
    # Signature pour le formulaire
    sign_str = f"{MERCHANT_ID}:{amount}:{SECRET_WORD_1}:{currency}:{order_id}"
    signature = hashlib.md5(sign_str.encode()).hexdigest()
    
    # URL FreeKassa
    payment_url = (
        f"https://pay.fk.money/?"
        f"m={MERCHANT_ID}&"
        f"oa={amount}&"
        f"o={order_id}&"
        f"s={signature}&"
        f"currency={currency}&"
        f"i=36&"  # Card RUB - changer selon méthode
        f"em={email}&"
        f"lang=en"
    )
    
    # Créer command dans Directus avec status "pending"
    async with directus_client() as dc:
        await dc.update_item("orders", order_id, {
            "status": "pending_payment",
            "payment_method": "freekassa",
            "payment_url": payment_url
        })
    
    return {"url": payment_url}


@router.post("/callback")
async def frekassa_webhook(request: Request):
    """
    Webhook FreeKassa - appelé après paiement
    URLs dans dashboard FreeKassa:
    - notification: https://e-probook.site/payment/notification
    - Apache proxy vers: https://b2l-backend:8000/api/freekassa/callback
    """
    # 1. Vérifier IP auteur (sécurité)
    client_ip = request.client.host
    if not verify_freekassa_ip(client_ip):
        print(f"[FreeKassa] IP non autorisée: {client_ip}")
        return Response(content="NO", status_code=403)
    
    # 2. Parse form data
    form = await request.form()
    merchant_id = form.get("MERCHANT_ID")
    amount = form.get("AMOUNT")
    order_id = form.get("MERCHANT_ORDER_ID")
    signature = form.get("SIGN")
    intid = form.get("intid")  # ID transaction FreeKassa
    
    # 3. Vérifier signature
    if not verify_signature(merchant_id, amount, order_id, signature, SECRET_WORD_2):
        print(f"[FreeKassa] Signature invalide pour commande: {order_id}")
        return Response(content="NO", status_code=400)
    
    # 4. Valider montant commande dans BDD (anti-fraude)
    # async with directus_client() as dc:
    #     order = await dc.get_item("orders", order_id)
    #     if float(amount) < float(order.get("total", 0)):
    #         return Response(content="NO", status_code=400)
    
    # 5. Mettre à jour commande dans BDD
    await update_order_status(order_id, "paid")
    
    print(f"[FreeKassa] Paiement réussi: {order_id}, montant: {amount}, trans: {intid}")
    
    # 6. Répondre "YES" à FreeKassa (IMPORTANT!)
    return Response(content="YES")


# Routes pour pages success/fail (Apache proxy /payment/success et /payment/failed)
@router.get("/success")
async def payment_success(order_id: str):
    """Page après paiement réussi"""
    return {
        "status": "success",
        "message": "Paiement confirmé!",
        "order_id": order_id
    }


@router.get("/failed")
async def payment_failed(order_id: str):
    """Page après échec paiement"""
    return {
        "status": "failed",
        "message": "Paiement échoué. Veuillez réessayer.",
        "order_id": order_id
    }
```

### Configuration .env:

```bash
# FreeKassa
FREEKASSA_MERCHANT_ID=12345
FREEKASSA_SECRET_WORD_1=votre_secret_word_1
FREEKASSA_SECRET_WORD_2=votre_secret_word_2
```

### Checklist intégration:

- [ ] Endpoint `/api/freekassa/create-order` ajouté → même pattern que Stripe/Dodo
- [ ] Endpoint `/api/freekassa/callback` ajouté (webhook)
- [ ] Pages `/api/freekassa/success` et `/api/freekassa/failed`
- [ ] Apache proxy vers `/payment/*` → backend
- [ ] URLs dans dashboard FreeKassa configurées

### Frontend (Redirect):
```javascript
// Bouton "Payer"
const handlePayment = async () => {
  const response = await fetch('/api/freekassa/create-order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      amount: total, 
      email: customerEmail,
      orderId: orderId 
    })
  });
  
  const { url } = await response.json();
  window.location.href = url;
};
```

---

## ✅ Checklist Activation

- [ ] Créer compte sur https://freekassa.ru
- [ ] Configurer la boutique dans le dashboard
- [ ] Récupérer Merchant ID, Secret Words, API Key
- [ ] Configurer URLs (notification, success, fail)
- [ ] **Configurer Apache** pour proxy /payment/* vers backend B2L
- [ ] Activer les méthodes de paiement (Card, Apple Pay, Google Pay)
- [ ] Implémenter endpoint callback backend
- [ ] Tester en mode sandbox (test mode dans settings)
- [ ] Passer en mode production

---

## 📞 Support

- **Email:** support@freekassa.ru
- **Phone:** +7 499 686 0324
- **Site:** https://freekassa.ru

---

*Document généré par Elia - 2026-04-25*

---

# 📖 DOCUMENTATION TECHNIQUE - INTÉGRATION COMPLETE

## 🎯 Contexte: Checkout Bene2Luxe.com

### Checkout Actuel (Options de paiement)

**Ordre affiché actuellement sur `/checkout`:**

1. **Solde** (authentifié)
2. **Carte Bancaire** (Dodo) ← Stripe banni → FreeKassa va remplacer
3. **Bitcoin** (Cryptomus)
4. **Virement Bancaire** (SEPA)

**BUT:** Ajouter Apple Pay et Google Pay APRÈS "Carte Bancaire" et AVANT "Bitcoin"

---

## 🗂️ Chemins des Fichiers à Modifier

### Frontend (bene2luxe/frontend_build/src/)

| Fichier | Purpose | Changement |
|---------|---------|----------|
| `src/components/PaymentMethodSelector.tsx` | **UI: Liste des méthodes de paiement** | Ajouter `freekassa_apple_pay` et `freekassa_google_pay` |
| `src/components/PaymentProcessingModal.tsx` | **UI: Modal de traitement paiement** | Gérer les nouvelles méthodes |
| `src/lib/paymentHandlers.ts` | **Logique: Handler paiement** | Ajouter handler pour FreeKassa |
| `src/api/cryptomus/webhook.ts` | (référence pour webhook) | Template similaire |
| `src/pages/Checkout.tsx` | **Page checkout** | Utilise PaymentMethodSelector |

### Backend (bene2luxe/backend/)

| Fichier | Purpose | Changement |
|---------|---------|----------|
| `routers/payments_dodo.py` | (référence) - paiement carte | Template pour créer nouveau router |
| `routers/payments_cryptomus.py` | (référence) - paiement crypto | Template pour webhook |
| `services/core/payment_providers.py` | **Abstraction: Providers** | Ajouter `FreeKassaPaymentProvider` |
| `services/core/payment_service.py` | **Service: Orchestration** | Ajouter FreeKassa au switch |
| `services/core/checkout_service.py` | **Service: Checkout** | Mapper nouvelles méthodes |
| `.env` (root backend) | Config | Ajouter `FREEKASSA_*` |

### Infrastructure (bene2luxe/)

| Fichier | Purpose | Changement |
|---------|---------|----------|
| `apache-config/e-probook.site-ssl.conf` | **Apache: Reverse proxy** | Ajouter `/payment/*` → backend |
| `docker-compose.yaml` | Services | (pas de changement) |

---

## 🔧 Implémentation Détaillée

### 1. FRONTEND - PaymentMethodSelector.tsx

**Chemin:** `bene2luxe/frontend_build/src/components/PaymentMethodSelector.tsx`

**Type actuel:**
```typescript
export type PaymentMethod = 'balance' | 'dodo' | 'cryptomus' | 'bank_transfer' | 'wise_manual' | 'revolut_manual'
```

**Type après modification:**
```typescript
export type PaymentMethod = 'balance' | 'dodo' | 'freekassa_card' | 'freekassa_apple_pay' | 'freekassa_google_pay' | 'cryptomus' | 'bank_transfer' | 'wise_manual' | 'revolut_manual'
```

**Options à ajouter (APRÈS dodo, AVANT cryptomus):**
```typescript
{
  id: 'freekassa_card',
  label: 'Carte Bancaire',
  description: 'Visa, Mastercard, Amex',
  icon: <CreditCard className="h-5 w-5" />,
  accent: 'from-gray-500 to-gray-600',
  badge: 'Nouveau',
  requiresAuth: false
},
{
  id: 'freekassa_apple_pay',
  label: 'Apple Pay',
  description: 'Paiement rapide',
  icon: <CreditCard className="h-5 w-5" />,  // ou icône Apple
  accent: 'from-gray-400 to-gray-500',
  badge: 'Rapide',
  requiresAuth: false
},
{
  id: 'freekassa_google_pay',
  label: 'Google Pay',
  description: 'Paiement rapide',
  icon: <CreditCard className="h-5 w-5" />,  // ou icône Google
  accent: 'from-blue-400 to-blue-500',
  badge: 'Rapide',
  requiresAuth: false
},
```

### 2. BACKEND - Nouveau Router

**Créer:** `bene2luxe/backend/routers/payments_freekassa.py`

Basé sur `payments_dodo.py`:

```python
# Extrait clé - router à créer
router = APIRouter(prefix="/api/payments/freekassa", tags=["payments-freekassa"])

# Configuration depuis .env
FREEKASSA_MERCHANT_ID = os.getenv("FREEKASSA_MERCHANT_ID")
FREEKASSA_SECRET_WORD_1 = os.getenv("FREEKASSA_SECRET_WORD_1")
FREEKASSA_SECRET_WORD_2 = os.getenv("FREEKASSA_SECRET_WORD_2")

@router.post("/create-order")
async def create_order(
    amount: float,
    email: str,
    order_id: str,
    payment_method: str = "card"  # "card", "apple_pay", "google_pay"
):
    """Crée session paiement FreeKassa"""
    # Mapper payment_method → ID FreeKassa
    method_ids = {"card": "36", "apple_pay": "38", "google_pay": "37"}
    method_id = method_ids.get(payment_method, "36")
    
    # Signature MD5
    sign_str = f"{MERCHANT_ID}:{amount}:{SECRET_WORD_1}:EUR:{order_id}"
    signature = hashlib.md5(sign_str.encode()).hexdigest()
    
    # URL paiement
    payment_url = f"https://pay.fk.money/?m={MERCHANT_ID}&oa={amount}&o={order_id}&s={signature}&currency=EUR&i={method_id}&em={email}&lang=en"
    
    return {"url": payment_url, "order_id": order_id}

@router.post("/webhook")
async def webhook(request: Request):
    """Webhook FreeKassa - callback après paiement"""
    # [Même logique que payments_dodo.py et payments_cryptomus.py]
    # 1. Vérifier IP
    # 2. Vérifier signature
    # 3. Mettre à jour commande
    # 4. Répondre "YES"
```

### 3. BACKEND - Enregistrer le router

**Fichier:** `bene2luxe/backend/main.py`

```python
# Ajouter après les autres routers de paiement
from routers import payments_freekassa
app.include_router(payments_freekassa.router)
```

### 4. BACKEND - Configuration .env

**Fichier:** `bene2luxe/backend/.env`

```bash
# FreeKassa (APRÈS Stripe banni)
FREEKASSA_MERCHANT_ID=votre_merchant_id
FREEKASSA_SECRET_WORD_1=votre_secret_word_1
FREEKASSA_SECRET_WORD_2=votre_secret_word_2
```

### 5. APACHE - Proxy /payment/*

**Fichier:** `bene2luxe/apache-config/e-probook.site-ssl.conf`

```apache
# FreeKassa callback - AVANT /api/ sinon / capture tout
ProxyPass /payment/notification http://b2l-backend:8000/api/payments/freekassa/webhook
ProxyPassReverse /payment/notification http://b2l-backend:8000/api/payments/freekassa/webhook

ProxyPass /payment/success http://b2l-frontend:3000/payment-success
ProxyPassReverse /payment/success http://b2l-frontend:3000/payment-success

ProxyPass /payment/failed http://b2l-frontend:3000/payment-failed
ProxyPassReverse /payment/failed http://b2l-frontend:3000/payment-failed
```

### 6. FREEKASSA - Dashboard

| Setting | Valeur |
|---------|-------|
| URL Notification | `https://e-probook.site/freekassa/payment/notification` |
| URL Success | `https://e-probook.site/freekassa/payment/success` |
| URL Fail | `https://e-probook.site/freekassa/payment/failed` |

---

## 📋 Checklist Implémentation

### Phase 1: Backend
- [ ] Créer `routers/payments_freekassa.py` basée sur `payments_dodo.py`
- [ ] Ajouter config FreeKassa dans `.env`
- [ ] Enregistrer router dans `main.py`

### Phase 2: Frontend
- [ ] Ajouter types `freekassa_card`, `freekassa_apple_pay`, `freekassa_google_pay` dans PaymentMethodSelector.tsx
- [ ] Ajouter icons/labels dans le array paymentMethods
- [ ] Mettre à jour PaymentProcessingModal si nécessaire

### Phase 3: Infrastructure
- [ ] Configurer Apache pour proxy `/payment/*`
- [ ] Configurer URLs dans dashboard FreeKassa

### Phase 4: Test
- [ ] Tester cada méthode de paiement
- [ ] Vérifier webhook callback
- [ ] Vérifier redirect success/failed

---

## 🧪 Credentials Test - FREEKASSA (MODE TEST)

**⚠️ EN MODE TEST - Pas de vrai paiement!**

| Paramètre | Valeur |
|-----------|-------|
| Merchant ID | `72582` |
| API Key (du dashboard) | (voir dashboard FreeKassa) |
| Secret Word 1 | `k5Y_$),RBv-lWw@` |
| Secret Word 2 | `?7[3su$m$pdeKDM` |

### URLs Test (Dashboard FreeKassa)

| URL | Valeur |
|-----|-------|
| URL Notification | `https://e-probook.site/freekassa/payment/notification` |
| URL Success | `https://e-probook.site/freekassa/payment/success` |
| URL Failed | `https://e-probook.site/freekassa/payment/failed` |

### Tester le Webhook

```bash
# Simuler un callback FreeKassa (pour test local)
curl -X POST http://localhost:8000/api/payments/freekassa/webhook \
  -d "MERCHANT_ID=72582" \
  -d "AMOUNT=10.00" \
  -d "MERCHANT_ORDER_ID=TEST-ORDER-1" \
  -d "SIGN=$(echo -n '72582:10.00:?7[3su\$m\$pdeKDM:TEST-ORDER-1' | md5)"
```

### Commandes Test

```bash
# Tester création lien paiement
curl -X POST http://localhost:8000/api/payments/freekassa/create-order \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10.00,
    "email": "test@example.com",
    "order_id": "TEST-ORDER-1",
    "payment_method": "card"
  }'

# Réponse attendue:
# {"url": "https://pay.fk.money/?m=72582&oa=10.00&...", "order_id": "TEST-ORDER-1"}
```

---

## 📞 Support
