# Motion Design Principles for Premium Videos

This reference defines the animation quality bar for `/brag` compositions. Every video must feel like it was animated by a motion designer, not a developer.

---

## Core Principles

### 1. Every Move Has Purpose

No decorative animation. Every tween must serve one of:
- **Reveal**: bringing new content into view
- **Emphasis**: drawing attention to what matters
- **Transition**: moving from one idea to the next
- **Rhythm**: creating a visual pulse that syncs with audio

If an animation doesn't do one of these, delete it.

### 2. Physics Over Linear

Linear motion feels robotic. Use physics-based easing for organic, premium feel:

| Motion Type | Easing | Use Case |
|---|---|---|
| **Entrance** | `power4.out` or `elastic.out(1, 0.5)` | Elements arriving on screen |
| **Exit** | `power3.in` | Elements leaving the frame |
| **Settle** | `back.out(1.7)` | Final position with subtle overshoot |
| **Hold** | `sine.inOut` | Gentle breathing, ambient motion |
| **Impact** | `power2.in` then `elastic.out(1, 0.3)` | Slam, then bounce |
| **Spring** | `elastic.out(1, 0.3)` | Playful, bouncy arrivals |

**Never use:** `linear`, `power1.inOut`, or any easing that feels flat.

### 3. Staggered Reveals

Sequential elements should never appear simultaneously. Use staggered timing:

```javascript
// ❌ BAD: All cards appear at once
tl.fromTo(".card", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.5 });

// ✅ GOOD: Cards stagger with rhythm
tl.fromTo(".card", 
  { opacity: 0, y: 40 }, 
  { opacity: 1, y: 0, duration: 0.5, ease: "power3.out", stagger: 0.1 }
);
```

**Stagger timing by element type:**
- Text lines: 0.08–0.12s
- Cards/blocks: 0.10–0.15s
- Icons/images: 0.12–0.18s
- Large reveals: 0.20–0.30s

### 4. Depth and Layering

Flat videos feel cheap. Create depth through:

- **Scale hierarchy**: Hero elements at 1.0–1.2x, supporting elements at 0.8–0.9x
- **Z-index layering**: Background → midground → foreground → overlay
- **Parallax**: Elements at different depths move at different speeds
- **Perspective**: Use `perspective: 1200px` for 3D card flips and rotations

```javascript
// Parallax depth example
tl.to(".bg", { y: -100, duration: 1, ease: "none" }, 0);
tl.to(".mid", { y: -50, duration: 1, ease: "none" }, 0);
tl.to(".fg", { y: 0, duration: 1, ease: "none" }, 0);
```

### 5. Typography as Motion

Text is not just content—it's a visual element that moves.

**Entrance patterns:**
- **Slide up + fade**: `y: 30 → 0, opacity: 0 → 1` (most common)
- **Scale in**: `scale: 0.8 → 1, opacity: 0 → 1` (hero text)
- **Reveal mask**: `clipPath` from left to right (kinetic typography)
- **Letter stagger**: Each character animates sequentially (for short words only)

**Hold patterns:**
- **Breathing**: Subtle `scale: 1.0 → 1.02 → 1.0` over 2–3s (premium feel)
- **Glow pulse**: `textShadow` opacity oscillation (subtle, 0.1–0.2 range)

**Exit patterns:**
- **Fade up**: `y: 0 → -20, opacity: 1 → 0` (most common)
- **Scale out**: `scale: 1 → 1.1, opacity: 1 → 0` (dramatic)

### 6. Transition Choreography

Transitions are not just between scenes—they're part of the story.

**Transition timing by energy:**
| Energy | Duration | Example |
|---|---|---|
| Calm | 0.6–0.8s | Slow crossfade, gentle slide |
| Medium | 0.4–0.5s | Standard push, blur through |
| High | 0.2–0.3s | Hard cut, flash, glitch |
| Impact | 0.1–0.15s | Slam, shutter, instant cut |

**Transition selection guide:**
- **Reveal new information**: Push slide, scale zoom, or direction blur
- **Dramatic moment**: 3D flip, light leak, or overexposure burn
- **Rhythmic cut**: Hard cut on beat, flash cut, or glitch
- **Smooth flow**: Crossfade, gentle slide, or blur through

### 7. Texture and Atmosphere

Premium videos have visual texture, not just flat colors.

**Subtle effects:**
- **Film grain**: CSS `background-image: url("data:image/svg+xml,...")` with low opacity (0.03–0.06)
- **Vignette**: Radial gradient overlay, darker at edges
- **Light leaks**: Warm color overlays that drift across frame
- **Ambient particles**: Subtle floating dots or specks (use sparingly)

**Background treatment:**
- Gradient meshes (2–3 color stops, not linear)
- Subtle noise texture
- Depth-of-field blur on background elements

---

## Animation Recipes

### Hero Text Entrance (Premium)

```javascript
// Phase 1: Scale + blur entrance
tl.fromTo("#hero",
  { scale: 0.85, opacity: 0, filter: "blur(8px)" },
  { scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.7, ease: "power3.out" },
  0
);

// Phase 2: Subtle breathing after settle
tl.to("#hero", 
  { scale: 1.02, duration: 2, ease: "sine.inOut", yoyo: true, repeat: -1 },
  0.7
);
```

### Staggered Card Reveal

```javascript
// Cards enter with stagger + slight rotation
tl.fromTo(".card",
  { y: 60, opacity: 0, rotation: -2 },
  { 
    y: 0, 
    opacity: 1, 
    rotation: 0, 
    duration: 0.6, 
    ease: "back.out(1.7)", 
    stagger: 0.12 
  },
  0.3
);

// Cards settle with subtle scale pulse
tl.to(".card",
  { scale: 1.02, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: 1, stagger: 0.12 },
  1.0
);
```

### Dramatic Scale Reveal

```javascript
// Background zooms in dramatically
tl.fromTo("#bg",
  { scale: 1.5, opacity: 0 },
  { scale: 1, opacity: 1, duration: 1.2, ease: "power2.out" },
  0
);

// Foreground text slams in
tl.fromTo("#text",
  { scale: 2, opacity: 0, filter: "blur(10px)" },
  { scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "back.out(2)" },
  0.8
);
```

### Kinetic Typography Reveal

```javascript
// Text reveals with clip-path mask
tl.fromTo("#text",
  { clipPath: "inset(0 100% 0 0)" },
  { clipPath: "inset(0 0% 0 0)", duration: 0.6, ease: "power3.out" },
  0.3
);

// Underline draws in
tl.fromTo("#underline",
  { scaleX: 0 },
  { scaleX: 1, duration: 0.4, ease: "power2.out", transformOrigin: "left" },
  0.7
);
```

### Glitch Transition (Premium)

```javascript
// RGB channel split
tl.set("#glitch-r", { opacity: 0.6, x: 0 }, T);
tl.set("#glitch-b", { opacity: 0.6, x: 0 }, T);

// Split channels
tl.to("#glitch-r", { x: -40, opacity: 0.8, duration: 0.15, ease: "power2.in" }, T);
tl.to("#glitch-b", { x: 40, opacity: 0.8, duration: 0.15, ease: "power2.in" }, T);

// Jitter scene
tl.to(old, { x: -10, duration: 0.03 }, T);
tl.to(old, { x: 15, duration: 0.03 }, T + 0.03);
tl.to(old, { x: -5, duration: 0.03 }, T + 0.06);

// Swap at peak
tl.set(old, { opacity: 0 }, T + 0.15);
tl.set(new, { opacity: 1 }, T + 0.15);

// Converge channels
tl.to("#glitch-r", { x: 0, opacity: 0, duration: 0.15 }, T + 0.15);
tl.to("#glitch-b", { x: 0, opacity: 0, duration: 0.15 }, T + 0.15);
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Linear Motion
```javascript
// BAD: Robotic, cheap feel
tl.to("#el", { x: 100, duration: 0.5, ease: "linear" });
```

### ❌ Simultaneous Reveals
```javascript
// BAD: Everything appears at once, overwhelming
tl.fromTo(".item", { opacity: 0 }, { opacity: 1, duration: 0.3 });
```

### ❌ Flash-Frame Text
```javascript
// BAD: Text appears and disappears too quickly
tl.to("#text", { opacity: 1, duration: 0.1 });
tl.to("#text", { opacity: 0, duration: 0.1, delay: 0.2 });
```

### ❌ Decorative Particles
```javascript
// BAD: Generic floating particles that don't serve the story
// Avoid: random dots, circles, or squares that just float around
```

### ❌ Oversized Easing
```javascript
// BAD: So much overshoot it looks broken
tl.to("#el", { x: 100, duration: 0.5, ease: "elastic.out(1, 0.1)" });
// Use: elastic.out(1, 0.3) or elastic.out(1, 0.5) for subtle bounce
```

---

## Quality Checklist

Before finalizing any composition, verify:

- [ ] No `linear` easing anywhere
- [ ] All entrances use `power3.out`, `power4.out`, `back.out`, or `elastic.out`
- [ ] All exits use `power2.in` or `power3.in`
- [ ] Sequential elements have stagger (0.08–0.20s)
- [ ] Hero text has a 2-phase entrance (blur/scale → settle)
- [ ] At least one element has subtle breathing/pulse animation
- [ ] Transitions match the energy of the content
- [ ] No text appears for less than 0.8s (readability floor)
- [ ] Background has subtle texture (grain, gradient, or noise)
- [ ] Depth is created through scale, z-index, or parallax
