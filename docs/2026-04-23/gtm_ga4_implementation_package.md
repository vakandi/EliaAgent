# GTM GA4 Implementation Package - Bene2Luxe
**Created**: 23 Avril 2026  
**Status**: Ready for Implementation  
**Target**: bene2luxe.com  

---

## 📦 PACKAGE CONTENTS

### 1. GTM Container Setup Guide
### 2. dataLayer Implementation Code
### 3. Consent Banner HTML/CSS/JS
### 4. Event Mapping Documentation
### 5. Google Tag Configuration

---

## 1. GTM CONTAINER SETUP GUIDE

### Step 1: Create GTM Container
1. Go to [tagmanager.google.com](https://tagmanager.google.com)
2. Create account: "Bene2Luxe"
3. Create container: "bene2luxe.com"
4. Container type: Web

### Step 2: Required Tags (Create in this order)

| Order | Tag | Type | Trigger |
|-------|-----|------|---------|
| 1 | Google Tag (GA4) | Google Tag | All Pages |
| 2 | Conversion Linker | Conversion Linker | All Pages |
| 3 | Consent Initialization | Custom HTML | Consent Initialization - All Pages |
| 4 | Google Ads Conversion | Google Ads Conversion | Purchase Event |
| 5 | Enhanced Conversions | Google Tag | Purchase Event |

### Step 3: GTM Container ID Format
```
GTM-XXXXXXX
```

---

## 2. dataLayer IMPLEMENTATION CODE

### 2.1 Base dataLayer (Add to all pages - before GTM script)

```html
<script>
window.dataLayer = window.dataLayer || [];
</script>
```

### 2.2 Homepage/Categories/Search - view_item_list

```javascript
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'view_item_list',
  ecommerce: {
    currency: 'EUR',
    items: [
      {
        item_id: 'LV-NEVERFULL-MM',
        item_name: 'Neverfull MM',
        item_brand: 'Louis Vuitton',
        item_category: 'Bags',
        item_category2: 'Totes',
        item_variant: 'Monogram',
        price: 185.00,
        discount: 0,
        quantity: 1
      },
      // ... more items
    ]
  }
});
</script>
```

### 2.3 Product Click - select_item

```javascript
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'select_item',
  ecommerce: {
    currency: 'EUR',
    items: [{
      item_id: 'LV-NEVERFULL-MM',
      item_name: 'Neverfull MM',
      item_brand: 'Louis Vuitton',
      item_category: 'Bags',
      price: 185.00
    }]
  }
});
</script>
```

### 2.4 Product Page View - view_item

```javascript
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'view_item',
  ecommerce: {
    currency: 'EUR',
    value: 185.00,
    items: [{
      item_id: 'LV-NEVERFULL-MM',
      item_name: 'Neverfull MM',
      item_brand: 'Louis Vuitton',
      item_category: 'Bags',
      item_variant: 'Monogram',
      price: 185.00,
      discount: 0
    }]
  }
});
</script>
```

### 2.5 Add to Cart - add_to_cart

```javascript
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'add_to_cart',
  ecommerce: {
    currency: 'EUR',
    value: 185.00,
    items: [{
      item_id: 'LV-NEVERFULL-MM',
      item_name: 'Neverfull MM',
      item_brand: 'Louis Vuitton',
      item_category: 'Bags',
      price: 185.00,
      quantity: 1
    }]
  }
});
</script>
```

### 2.6 Remove from Cart - remove_from_cart

```javascript
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'remove_from_cart',
  ecommerce: {
    currency: 'EUR',
    value: 185.00,
    items: [{
      item_id: 'LV-NEVERFULL-MM',
      item_name: 'Neverfull MM',
      item_brand: 'Louis Vuitton',
      price: 185.00,
      quantity: 1
    }]
  }
});
</script>
```

### 2.7 View Cart - view_cart

```javascript
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'view_cart',
  ecommerce: {
    currency: 'EUR',
    value: 370.00,
    items: [
      {
        item_id: 'LV-NEVERFULL-MM',
        item_name: 'Neverfull MM',
        price: 185.00,
        quantity: 1
      },
      {
        item_id: 'DIOR-SADDLE',
        item_name: 'Saddle Bag',
        price: 185.00,
        quantity: 1
      }
    ]
  }
});
</script>
```

### 2.8 Begin Checkout - begin_checkout

```javascript
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'begin_checkout',
  ecommerce: {
    currency: 'EUR',
    value: 370.00,
    items: [
      {
        item_id: 'LV-NEVERFULL-MM',
        item_name: 'Neverfull MM',
        price: 185.00,
        quantity: 1
      }
    ]
  }
});
</script>
```

### 2.9 Add Shipping Info - add_shipping_info

```javascript>
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'add_shipping_info',
  ecommerce: {
    currency: 'EUR',
    value: 385.00,
    shipping_tier: 'Colissimo | Chronopost | Point Relais',
    items: [...]
  }
});
</script>
```

### 2.10 Add Payment Info - add_payment_info

```javascript>
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'add_payment_info',
  ecommerce: {
    currency: 'EUR',
    value: 385.00,
    payment_type: 'Credit Card | PayPal | Crypto',
    items: [...]
  }
});
</script>
```

### 2.11 Purchase (MOST IMPORTANT) - on confirmation page

```javascript
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'purchase',
  ecommerce: {
    transaction_id: 'ORD-12345-UNIQUE-ID',
    affiliation: 'Bene2Luxe',
    currency: 'EUR',
    value: 385.00,
    tax: 32.08,
    shipping: 15.00,
    coupon: 'PROMO10',
    items: [
      {
        item_id: 'LV-NEVERFULL-MM',
        item_name: 'Neverfull MM',
        item_brand: 'Louis Vuitton',
        item_category: 'Bags',
        item_variant: 'Monogram',
        price: 185.00,
        quantity: 1,
        discount: 0
      }
    ]
  }
});
</script>
```

### 2.12 Refund - refund

```javascript
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'refund',
  ecommerce: {
    transaction_id: 'ORD-12345-UNIQUE-ID',
    currency: 'EUR',
    value: 185.00,
    items: [
      {
        item_id: 'LV-NEVERFULL-MM',
        item_name: 'Neverfull MM',
        price: 185.00,
        quantity: 1
      }
    ]
  }
});
</script>
```

### 2.13 View Promotion - view_promotion

```javascript
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'view_promotion',
  ecommerce: {
    items: [{
      promotion_id: 'SUMMER_SALE_2026',
      promotion_name: 'Summer Sale',
      creative_name: 'Hero Banner',
      creative_slot: '1'
    }]
  }
});
</script>
```

### 2.14 Select Promotion - select_promotion

```javascript>
<script>
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'select_promotion',
  ecommerce: {
    items: [{
      promotion_id: 'SUMMER_SALE_2026',
      promotion_name: 'Summer Sale',
      creative_name: 'Hero Banner',
      creative_slot: '1'
    }]
  }
});
</script>
```

---

## 3. CONSENT BANNER (GDPR Compliant)

### 3.1 HTML Structure

```html
<div id="cookie-consent-banner" class="cookie-banner" style="display:none;">
  <div class="cookie-content">
    <h2>🍪 Gestion des Cookies</h2>
    <p>
      Nous utilisons des cookies pour améliorer votre expérience et analyser notre trafic.
      <a href="/politique-cookies" target="_blank">En savoir plus</a>
    </p>
    <div class="cookie-buttons">
      <button id="accept-all-cookies" class="cookie-btn cookie-btn-accept">
        Accepter tout
      </button>
      <button id="reject-cookies" class="cookie-btn cookie-btn-reject">
        Refuser
      </button>
      <button id="customize-cookies" class="cookie-btn cookie-btn-customize">
        Personnaliser
      </button>
    </div>
  </div>
</div>
```

### 3.2 CSS Styles

```css
.cookie-banner {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
  z-index: 9999;
  padding: 20px;
  font-family: system-ui, sans-serif;
}

.cookie-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.cookie-content h2 {
  margin: 0 0 10px 0;
  font-size: 1.5rem;
}

.cookie-content p {
  margin: 0 0 20px 0;
  color: #666;
}

.cookie-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.cookie-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: opacity 0.2s;
}

.cookie-btn:hover {
  opacity: 0.9;
}

.cookie-btn-accept {
  background: #1a1a1a;
  color: #fff;
}

.cookie-btn-reject {
  background: #e0e0e0;
  color: #333;
}

.cookie-btn-customize {
  background: transparent;
  color: #1a1a1a;
  text-decoration: underline;
}
```

### 3.3 JavaScript Logic

```javascript
<script>
(function() {
  // Consent state
  const CONSENT_KEY = 'bene2luxe_consent';
  
  function getConsent() {
    return JSON.parse(localStorage.getItem(CONSENT_KEY) || 'null');
  }
  
  function setConsent(consent) {
    localStorage.setItem(CONSENT_KEY, JSON.stringify(consent));
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: 'consent_update',
      consent: consent
    });
  }
  
  function showBanner() {
    document.getElementById('cookie-consent-banner').style.display = 'block';
  }
  
  function hideBanner() {
    document.getElementById('cookie-consent-banner').style.display = 'none';
  }
  
  function updateGTMConsent(consent) {
    // Update GTM Consent Mode
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: 'consent_update',
      consent_settings: consent
    });
  }
  
  // Initialize
  document.addEventListener('DOMContentLoaded', function() {
    const consent = getConsent();
    
    if (!consent) {
      showBanner();
      
      // Accept all
      document.getElementById('accept-all-cookies').addEventListener('click', function() {
        const consent = {
          ad_storage: 'granted',
          analytics_storage: 'granted',
          ad_user_data: 'granted',
          ad_personalization: 'granted',
          timestamp: Date.now()
        };
        setConsent(consent);
        updateGTMConsent(consent);
        hideBanner();
      });
      
      // Reject
      document.getElementById('reject-cookies').addEventListener('click', function() {
        const consent = {
          ad_storage: 'denied',
          analytics_storage: 'denied',
          ad_user_data: 'denied',
          ad_personalization: 'denied',
          timestamp: Date.now()
        };
        setConsent(consent);
        updateGTMConsent(consent);
        hideBanner();
      });
    }
  });
})();
</script>
```

---

## 4. GOOGLE TAG (GTM) INSTALLATION CODE

### Place in <head> section (before other scripts)

```html
<!-- Google Tag Manager -->
<script>
window.dataLayer = window.dataLayer || [];
</script>
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
<!-- End Google Tag Manager -->
```

### Place right after <body> opening tag

```html
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
```

---

## 5. GTM TRIGGER CONFIGURATIONS

### All Pages Trigger
```javascript
Trigger Type: Page View
Conditions: Page URL contains .
```

### Consent Initialization Trigger
```javascript
Trigger Type: Consent Initialization
Fire on: All Pages
```

### Custom Events Trigger (for all ecommerce events)
```javascript
Trigger Type: Custom Event
Event Name: .*
Fire on: All Pages
```

---

## 6. GOOGLE ADS CONVERSION SETUP

### Step 1: Get Conversion ID and Label
1. Go to Google Ads → Goals → Conversions
2. Create new conversion action
3. Category: Purchase
4. Value: Use different values
5. Copy Conversion ID and Label

### Step 2: Configure in GTM
```
Tag Type: Google Ads Conversion Tracking
Conversion ID: AW-XXXXXXXXX
Conversion Label: XXXXXXXXXXXXXX
Order ID: {{Transaction ID}}
Conversion Value: {{Value}}
Currency: {{Currency Code}}
```

---

## 7. ENHANCED CONVERSIONS SETUP

### Enable in GA4
1. Admin → Data Display → Conversions
2. Enable Enhanced Conversions for leads

### Implement in GTM
```javascript
Tag Type: Google Tag
Configuration:
  - Tag ID: G-XXXXXXXXXX
  - Additional settings → Enhanced conversions
  - Enable: "User-provided data"
```

---

## 8. TESTING CHECKLIST

### GTM Preview Mode
- [ ] Open GTM Preview
- [ ] Navigate homepage
- [ ] Click product → select_item fires
- [ ] View product page → view_item fires
- [ ] Add to cart → add_to_cart fires
- [ ] View cart → view_cart fires
- [ ] Checkout → begin_checkout fires
- [ ] Add shipping → add_shipping_info fires
- [ ] Add payment → add_payment_info fires
- [ ] Complete purchase → purchase fires

### GA4 DebugView
- [ ] Enable DebugView in GA4
- [ ] Complete test purchase
- [ ] Verify transaction_id is unique
- [ ] Verify all item parameters present
- [ ] Verify no duplicate purchase events

### Tag Assistant
- [ ] Install Tag Assistant Chrome extension
- [ ] Visit site
- [ ] Verify GTM container fires
- [ ] Check for any errors

---

## 9. DEPLOYMENT RESPONSIBILITIES

| Task | Owner | Status |
|------|-------|--------|
| Create GTM Container | Wael/Thomas | Pending |
| Install GTM code on site | Thomas | Pending |
| Add dataLayer to pages | Thomas | Pending |
| Create Consent Banner | Thomas | Pending |
| Configure GTM Tags | Wael | Pending |
| Create Google Ads Conversion | Wael | Pending |
| Test with DebugView | Wael | Pending |
| Publish GTM Container | Wael | Pending |

---

**Status**: Ready for Implementation  
**Next Step**: Thomas creates GTM container and installs code on server