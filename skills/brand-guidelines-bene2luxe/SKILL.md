---
name: brand-guidelines
description: Bene2Luxe brand guidelines, colors, typography, and graphical style for consistent branding across all interfaces. Use this skill whenever adding branding elements, redesigning components, or creating new features for the luxury fashion resale platform.
---

# Bene2Luxe Brand Guidelines

## Brand Essence

**Bene2Luxe** is a luxury fashion resale marketplace serving France and Switzerland. The brand represents:
- **Premium Quality**: Authentic luxury items at competitive prices
- **French Elegance**: Sophisticated, refined aesthetic rooted in European fashion heritage
- **Trust & Authenticity**: Verified luxury items with transparent pricing
- **Modern Luxury**: Combining classic elegance with contemporary digital experiences

**Market Positioning**: B2C luxury fashion resale platform operating in France and Switzerland with a focus on premium streetwear, designer labels, and exclusive collections.

---

## Color Palette

### Primary Colors

| Color Name | HSL Value | Hex Code | Usage |
|------------|-----------|----------|-------|
| Primary (Vibrant Red) | `354 70% 54%` | `#D93025` | CTAs, buttons, accents, brand highlights |
| Primary Dark | `354 70% 45%` | `#B8221A` | Hover states, darker accents |
| Primary Light | `354 70% 60%` | `#E85A55` | Subtle highlights, hover backgrounds |

### Neutral Colors

| Color Name | HSL Value | Hex Code | Usage |
|------------|-----------|----------|-------|
| White | `0 0% 100%` | `#FFFFFF` | Backgrounds, cards, text on dark |
| Soft Black | `0 0% 10%` | `#1A1A1A` | Primary text, headings |
| Dark Gray | `240 3.8% 46.1%` | `#737373` | Muted text, secondary content |
| Border Gray | `240 5.9% 90%` | `#E5E5E5` | Borders, dividers |
| Background Beige | `40 20% 97%` | `#F7F5F2` | Page background, sections |
| Secondary Beige | `40 20% 94%` | `#F0EBE6` | Cards, elevated surfaces |

### Semantic Colors

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Success | `#22C55E` | Success states, confirmations |
| Warning | `#F59E0B` | Warnings, pending states |
| Destructive | `#DC2626` | Errors, destructive actions |
| Info | `#3B82F6` | Informational states |

### CSS Variables (Tailwind + CSS)

```css
/* Core Design Tokens - Defined in index.css */
:root {
  --primary: 354 70% 54%;        /* Vibrant Red */
  --primary-foreground: 0 0% 100%;
  --secondary: 40 20% 97%;       /* Light Beige */
  --secondary-foreground: 0 0% 10%;
  --muted: 240 5% 96%;
  --muted-foreground: 240 3.8% 46.1%;
  --accent: 40 20% 94%;
  --accent-foreground: 240 5.9% 10%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 0 0% 98%;
  --border: 240 5.9% 90%;
  --input: 240 5.9% 90%;
  --ring: 354 70% 54%;
  --radius: 1rem;                 /* 16px - Rounded corners */
  --background: 0 0% 100%;
  --foreground: 0 0% 10%;
  --card: 0 0% 100%;
  --card-foreground: 0 0% 10%;
  --popover: 0 0% 100%;
  --popover-foreground: 0 0% 10%;
}
```

### Tailwind Color Extensions (tailwind.config.js)

```javascript
// Additional custom colors
colors: {
  navy: '#000000',
  ice: '#FFFFFF',
  red: '#DC2626',
  success: '#22C55E',
  warning: '#F59E0B',
  'dark-border': '#404040',
  'muted-foreground': '#737373',
}

// Custom box shadows
boxShadow: {
  panel: '0 4px 25px 0 rgba(0, 0, 0, 0.1)',
  glowred: '0 0 40px rgba(220, 38, 38, 0.35)',
  glow: '0 0 20px rgba(220, 38, 38, 0.4), 0 0 40px rgba(220, 38, 38, 0.3)',
  glow2: '0 0 20px rgba(0, 0, 0, 0.2), 0 0 40px rgba(0, 0, 0, 0.1)',
}
```

---

## Typography

### Font Family

| Usage | Font | Fallback |
|-------|------|----------|
| Headings | `'Poppins', sans-serif` | system-ui, sans-serif |
| Body | `'Poppins', sans-serif` | system-ui, sans-serif |
| UI Elements | `'Poppins', sans-serif` | system-ui, sans-serif |

**Google Fonts Import**:
```css
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');
```

### Font Weights

| Weight | Value | Usage |
|--------|-------|-------|
| Light | 300 | Subtitles, secondary text |
| Regular | 400 | Body text, general content |
| Medium | 500 | Emphasized body, buttons |
| Semi-Bold | 600 | Navigation, subheadings |
| Bold | 700 | Headings, emphasis |
| Extra Bold | 800 | Hero titles, callouts |
| Black | 900 | Logo, extreme emphasis |

### Type Scale

| Element | Size | Weight | Line Height | Tracking |
|---------|------|--------|-------------|----------|
| Hero Title | 3.2rem - 11rem | 900 | 1 | -0.06em |
| H1 | 2.5rem (40px) | 700 | 1.2 | tight |
| H2 | 2rem (32px) | 700 | 1.25 | tight |
| H3 | 1.5rem (24px) | 700 | 1.3 | tight |
| H4 | 1.25rem (20px) | 600 | 1.4 | tight |
| Body Large | 1.125rem (18px) | 400 | 1.6 | normal |
| Body | 1rem (16px) | 400 | 1.6 | normal |
| Small | 0.875rem (14px) | 400 | 1.5 | normal |
| Caption | 0.75rem (12px) | 500 | 1.4 | wide (0.05em) |
| Label | 0.625rem (10px) | 700 | 1 | wide (0.1em - 0.25em) |

### Special Text Treatments

```css
/* Uppercase labels */
.uppercase-label {
  @apply text-xs font-black uppercase tracking-widest;
}

/* Section subtitles */
.section-subtitle {
  @apply text-sm font-bold uppercase tracking-[0.16em] text-black/60;
}

/* Navigation links */
.nav-link {
  @apply text-sm font-bold uppercase tracking-wide text-black/90 hover:text-primary transition-colors;
}
```

---

## Spacing & Layout

### Container System

```css
.container-lg {
  @apply max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 w-full box-border;
  max-width: 100%;
  overflow-x: hidden;
}
```

### Spacing Scale (Tailwind)

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Tight spacing, icon gaps |
| sm | 8px | Compact elements |
| md | 16px | Default padding |
| lg | 24px | Section gaps |
| xl | 32px | Large gaps |
| 2xl | 48px | Section padding |
| 3xl | 64px | Hero spacing |
| 4xl | 96px | Large sections |

### Section Layouts

```css
/* Standard section */
.section {
  @apply py-16 md:py-24;
}

/* Rounded section container */
.section-rounded {
  @apply rounded-[2rem] md:rounded-[3rem] overflow-hidden my-4 md:my-8 mx-2 md:mx-4;
}
```

### Breakpoints

| Breakpoint | Width | Usage |
|------------|-------|-------|
| sm | 640px | Small tablets |
| md | 768px | Tablets |
| lg | 1024px | Laptops |
| xl | 1280px | Desktops |
| 2xl | 1536px | Large screens |

---

## Component Patterns

### Buttons

**Primary Button**:
```tsx
<Button variant="default" className="btn-primary">
  Acheter maintenant
</Button>
```
- Background: `hsl(354 70% 54%)` (Primary Red)
- Text: White
- Border-radius: Full (rounded-full)
- Padding: `px-8 py-3`
- Font: `text-sm font-bold uppercase tracking-wide`
- Hover: `hover:bg-primary/90 shadow-lg hover:shadow-xl`
- Transition: `transition-all duration-300`

**Secondary Button**:
```tsx
<Button variant="outline" className="btn-secondary">
  Voir plus
</Button>
```
- Background: White
- Border: `border-gray-200`
- Text: Black
- Hover: `hover:bg-gray-50`
- Border-radius: Full

**Ghost Button**:
```tsx
<Button variant="ghost" className="hover:text-primary hover:bg-gray-100 rounded-full">
  <Icon />
</Button>
```
- Icon buttons: `rounded-full w-10 h-10`

### Cards

**Product Card**:
```tsx
<div className="group relative overflow-hidden rounded-2xl transition-all duration-500 hover:shadow-[0_0_30px_rgba(217,48,37,0.3)] hover:-translate-y-1">
  {/* Image with hover scale */}
  <img className="transition-transform duration-700 group-hover:scale-110" />
  {/* Overlay gradient */}
  <div className="bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
</div>
```

**Card Hover Effect**:
```css
.card-hover {
  @apply hover:translate-y-[-4px] transition-transform duration-300 ease-out;
}
```

### Navigation

**Header (Sticky)**:
```tsx
<header className="sticky top-0 z-[100] w-full transition-all duration-300 bg-white/95">
  {/* Scrolled state */}
  {isScrolled ? "shadow-sm border-b border-black/10 py-2" : "border-b border-transparent py-4"}
</header>
```

**Nav Links**:
```tsx
<NavigationMenuLink className="text-sm font-bold uppercase tracking-wide text-black/90 hover:text-primary transition-colors px-2 py-2">
```

### Badges

**Primary Badge**:
```tsx
<Badge variant="default" className="bg-primary text-white">
  Nouveau
</Badge>
```

**Outline Badge**:
```tsx
<Badge variant="outline" className="text-foreground border-gray-200">
  En stock
</Badge>
```

### Inputs

**Standard Input**:
```tsx
<input className="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm ring-offset-background placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" />
```

### Modals & Dialogs

**Modal Container**:
```tsx
<div className="w-[900px] p-8 bg-white rounded-3xl shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)] border border-black/5 relative overflow-hidden">
  {/* Gradient accent line */}
  <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-60" />
</div>
```

### Icons

**Icon Library**: Lucide React

**Common Usage**:
```tsx
import { Search, ShoppingBag, Heart, User, Menu, ArrowRight } from 'lucide-react';

// Icon button
<Button variant="ghost" size="icon" className="text-black hover:text-primary hover:bg-gray-100 rounded-full w-10 h-10">
  <Search className="h-5 w-5" strokeWidth={2} />
</Button>
```

**Icon Sizing**:
- Small: `h-4 w-4`
- Default: `h-5 w-5`
- Large: `h-6 w-6`
- Hero: `h-8 w-8`

---

## Visual Effects

### Shadows

| Name | Value | Usage |
|------|-------|-------|
| panel | `0 4px 25px 0 rgba(0, 0, 0, 0.1)` | Cards, dropdowns |
| glowred | `0 0 40px rgba(220, 38, 38, 0.35)` | Hero glow effects |
| glow | `0 0 20px rgba(220, 38, 38, 0.4), 0 0 40px rgba(220, 38, 38, 0.3)` | Button hover |
| glow2 | `0 0 20px rgba(0, 0, 0, 0.2), 0 0 40px rgba(0, 0, 0, 0.1)` | Dark hover states |

### Gradients

```css
/* Primary gradient */
.bg-gradient-primary {
  background: linear-gradient(135deg, hsl(354 70% 54%) 0%, hsl(354 70% 45%) 100%);
}

/* Accent gradient line */
.bg-gradient-primary-line {
  background: linear-gradient(90deg, transparent, hsl(354 70% 54%), transparent);
}

/* Overlay gradient for images */
.bg-gradient-overlay {
  background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.4) 50%, transparent 100%);
}
```

### Border Radius

| Element | Radius | Class |
|---------|--------|-------|
| Buttons (pill) | Full | `rounded-full` |
| Cards | 1rem (16px) | `rounded-2xl` |
| Large cards | 1.5rem (24px) | `rounded-3xl` |
| Inputs | `var(--radius)` | `rounded-md` |
| Badges | Full | `rounded-full` |
| Section | 2-3rem | `rounded-[2rem] md:rounded-[3rem]` |

---

## Animation & Motion

### Keyframe Animations

```css
/* Fade up entrance */
@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Marquee (brand ticker) */
@keyframes marquee {
  0% { transform: translateX(0%); }
  100% { transform: translateX(-100%); }
}

/* Sparkle effect */
@keyframes sparkle {
  0%, 100% { opacity: 0.6; scale: 0.8; transform: rotate(0deg) scale(0.8); }
  25% { opacity: 0.9; scale: 1.1; transform: rotate(90deg) scale(1.1); }
  50% { opacity: 1; scale: 1.2; transform: rotate(180deg) scale(1.2); }
  75% { opacity: 0.9; scale: 1.1; transform: rotate(270deg) scale(1.1); }
}
```

### Animation Classes

```css
.animate-fade-up {
  animation: fade-up 0.6s ease-out forwards;
  opacity: 0;
}

.animate-marquee {
  animation: marquee 25s linear infinite;
}

.animate-sparkle {
  animation: sparkle 2s ease-in-out infinite;
}
```

### Transition Timings

| Effect | Duration | Easing |
|--------|----------|--------|
| Hover state | 300ms | `ease-out` |
| Card hover | 300ms | `ease-out` |
| Image scale | 500-700ms | `ease-in-out` |
| Fade up entrance | 600ms | `ease-out` |
| Scale in | 400ms | `ease-out` |
| Menu slide | 300ms | `ease-in-out` |

### Micro-interactions

```css
/* Button hover */
.btn-primary {
  @apply transition-all duration-300 shadow-lg hover:shadow-xl;
}

/* Card hover lift */
.card-hover {
  @apply hover:translate-y-[-4px] transition-transform duration-300 ease-out;
}

/* Image zoom on hover */
.group:hover .scale-image {
  @apply scale-110 transition-transform duration-700;
}

/* Cart bounce on add */
.animate-bounce {
  animation: bounce 0.3s;
}
```

### Page Transitions

- **Entrance animations**: Fade up with staggered delays (0.15s, 0.22s, 0.35s, 0.42s)
- **Easing curve**: `[0.22, 1, 0.36, 1]` (custom cubic-bezier for smooth deceleration)
- **Hero title animation**: 1.15s duration with blur-to-clear effect

---

## Responsive Design

### Mobile-First Approach

The design follows mobile-first principles with breakpoints:
- Default styles for mobile
- `md:` prefix for tablet (768px+)
- `lg:` prefix for desktop (1024px+)
- `xl:` prefix for large screens (1280px+)

### Header Responsive

| Breakpoint | Desktop | Mobile |
|------------|--------|--------|
| Logo | Full "BENE² LUXE" + tagline | "B2" square only |
| Navigation | Full horizontal menu | Hamburger menu |
| Search | Icon trigger | Full-screen overlay |
| Cart/Wishlist | Visible | Visible |
| User menu | Icon | Icon |

### Hero Responsive

| Element | Mobile | Desktop |
|---------|--------|---------|
| Height | 85vh | 95vh |
| Background | banner-mobile.png | banner.png |
| Title size | 3.2rem | Up to 11rem |
| Title position | Center | Center |
| CTA buttons | Stacked | Side by side |
| Corner radius | 0 | 2.5rem |

### Grid Systems

```tsx
// Product grid
<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">

// Category grid (4 columns desktop)
<div className="grid grid-cols-4 gap-5">

// Two column layout
<div className="grid grid-cols-1 md:grid-cols-2 gap-8">
```

---

## Brand Identity Elements

### Logo

**Primary Logo**:
- Red square with "B2" in white: `bg-primary text-white`
- Font: Black, 1.5rem (24px), tracking-tighter

**Full Logo**:
- "BENE" + superscript "2" + "LUXE"
- Font: Black, 1.25rem-1.5rem
- Tagline: "Distribution" in small caps below

**Usage**:
```tsx
// Red square logo
<div className="flex h-10 w-10 items-center justify-center bg-primary font-black text-xl tracking-tighter rounded-sm">
  B2
</div>

// Full logo
<span className="font-black text-xl tracking-tighter">
  BENE<sup className="text-primary text-sm">2</sup> LUXE
</span>
```

### Tagline

- French: "Distribution" (used in header)
- Positioning: Below main logo, uppercase, tracking [0.2em]

### Imagery Style

- **Product photos**: Clean white or light gray background
- **Lifestyle shots**: Dark overlays with white text
- **Category images**: Rounded corners, hover zoom effect
- **Backgrounds**: Marble texture (`/background_marble.jpeg`) for premium sections

### Marble Background Effect

```css
.bg-marble {
  background-color: hsl(40 20% 97%);
}

.bg-marble::before {
  content: "";
  @apply absolute inset-0 z-[-1] opacity-60 mix-blend-multiply pointer-events-none;
  background-image: url('/background_marble.jpeg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
```

---

## Do's & Don'ts

### Do's

✅ **Use Primary Red** (`#D93025`) for:
- Primary CTAs and buttons
- Brand accents and highlights
- Active states and selections

✅ **Use Poppins font** for all text elements

✅ **Use full rounded buttons** (`rounded-full`) for primary actions

✅ **Add subtle shadows** on cards: `shadow-panel` or `hover:shadow-[0_0_30px_rgba(217,48,37,0.3)]`

✅ **Use uppercase** for labels, navigation, and small text emphasis

✅ **Add smooth transitions** (300ms) on all interactive elements

✅ **Use gradient accents** on section dividers and hero elements

✅ **Maintain white space** - generous padding and margins

### Don'ts

❌ **Don't use blue or green** as primary colors (reserved for semantic states)

❌ **Don't use sharp corners** - always use rounded edges (minimum `rounded-md`)

❌ **Don't mix font families** - Poppins is the only font

❌ **Don't use black** (#000000) for text - use soft black (`#1A1A1A` or `text-black/90`)

❌ **Don't create flat designs** - always add subtle shadows or depth

❌ **Don't use default browser styling** - always apply custom styles

❌ **Don't forget accessibility** - maintain contrast ratios, use proper focus states

---

## Quick Reference Code Snippets

### Button Variants

```tsx
// Primary (Red)
<Button variant="default">Shop Now</Button>

// Secondary (White outline)
<Button variant="outline">Learn More</Button>

// Ghost (Icon button)
<Button variant="ghost" size="icon"><Icon /></Button>

// Large CTA
<Button variant="default" size="lg" className="h-14 text-lg">Get Started</Button>
```

### Card Component

```tsx
<div className="group relative overflow-hidden rounded-2xl bg-white shadow-panel transition-all duration-300 hover:shadow-[0_0_30px_rgba(217,48,37,0.3)] hover:-translate-y-1">
  <img src="..." className="w-full h-64 object-cover transition-transform duration-700 group-hover:scale-110" />
  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
  <div className="absolute bottom-0 p-4">
    <h3 className="text-lg font-bold text-white">Product Name</h3>
  </div>
</div>
```

### Section Layout

```tsx
<section className="section bg-marble">
  <div className="container-lg">
    <h2 className="text-3xl font-bold mb-8">Section Title</h2>
    {/* Content */}
  </div>
</section>
```

### Navigation Link

```tsx
<Link className="text-sm font-bold uppercase tracking-wide text-black/90 hover:text-primary transition-colors">
  Link Text
</Link>
```

### Badge

```tsx
<Badge className="bg-primary text-white">New</Badge>
<Badge variant="outline" className="border-gray-200 text-gray-600">Sale</Badge>
```

### Input Field

```tsx
<input 
  type="text" 
  placeholder="Rechercher..." 
  className="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary" 
/>
```

---

## File Locations Reference

| Asset | Location |
|-------|----------|
| CSS Variables | `/src/index.css` |
| Tailwind Config | `/tailwind.config.js` |
| ZUI Components | `/src/components/zui/` |
| UI Components | `/src/components/ui/` |
| Layout Components | `/src/components/layout/` |
| Section Components | `/src/components/sections/` |
| Hero Image | `/public/banner.png`, `/public/banner-mobile.png` |
| Backgrounds | `/public/background_marble.jpeg` |

---

*Last Updated: March 2026*
*For Bene2Luxe Luxury Fashion Resale Platform - France/Switzerland*
