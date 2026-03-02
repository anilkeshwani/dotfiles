# iTerm2 Colour Palettes

## Flexoki Light vs. Flexoki Light Saturated: A Colour Theory Analysis

After converting the sRGB float values to HSL for all 12 chromatic ANSI slots (Ansi 1–6 and their bright variants 9–14), a very precise and consistent pattern emerges.

### What is identical

The structural palette — background, foreground, black/white neutrals (Ansi 0, 7, 8, 15), cursor, selection, and UI chrome — is byte-for-byte identical between the two themes. The background is #FFFDF0 (a warm cream, chromatically very
slightly yellow) and the foreground is #100F0F (near-black with a faint warm cast).

### The single transformation: chroma amplification with lightness compensation

The saturated variant applies a uniform operation to every chromatic colour: hue is preserved exactly while chroma is pushed toward the sRGB gamut boundary, compensated by a reduction in lightness.


| Colour | Hue (both) | Lightness (std) | Lightness (sat) | Saturation (std) | Saturation (sat) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Red (Ansi 1) | ~3° | 42% | 35% | 62% | 93% |
| Green (Ansi 2) | ~73° | 27% | 22% | 84% | 100% |
| Yellow (Ansi 3) | ~45° | 34% | 28% | ~99% | 100% |
| Blue (Ansi 4) | ~212° | 39% | 32% | 68% | 100% |
| Magenta (Ansi 5) | ~326° | 41% | 33% | 55% | 82% |
| Cyan (Ansi 6) | ~175° | 33% | 27% | 57% | 86% |

The saturated variants of green, yellow, and blue hit B=0.0 (blue channel floor), meaning they sit on the sRGB gamut surface — they cannot be made more chromatic within sRGB.

### Formal colour theory framing

In HSL terms this is a chroma boost. In LCH / Oklch (the perceptually-uniform models more relevant to modern design systems), what's happening is an increase in C (chroma) — the distance from the neutral achromatic axis — while L
(perceptual lightness) decreases. This is not a simple saturation slider operation; the lightness compensation keeps the colours from bleaching out into neon, maintaining approximate luminance parity relative to the text rendering context.

The transformation is geometrically equivalent to moving each chromatic colour radially outward toward the sRGB gamut shell within its constant-hue plane, with a simultaneous descent along the lightness axis to avoid perceptual
oversaturation.

### UX design implications

Standard Flexoki Light — Restrained chroma, moderate lightness:
- Colours sit closer to the neutral axis, producing lower chromatic contrast between syntax categories
- The palette reads as "analogous" in feel — harmonious, low-tension
- Suits extended reading sessions; reduced chromatic fatigue and lower simultaneous contrast induction on the warm background
- Aligns with Steph Ango's stated design intent: a "paper and ink" aesthetic where colour is subordinate to typographic structure

Flexoki Light Saturated — High chroma, lower lightness:
- Stronger categorical differentiation: each ANSI colour occupies more distinct chromatic territory, improving pre-attentive pop-out for syntax scanning
- Higher colorimetric distance between adjacent hue categories reduces confusion at small font sizes or with peripheral vision
- The lower lightness compensates for the stronger chroma to maintain adequate luminance contrast against the #FFFDF0 background — these are not "neon" colours
- Trade-off: more chromatic tension in the palette; Simultaneous contrast effects from highly saturated colours can subtly shift the perceived warmth of neutral areas (the background may read as cooler or more yellowish by comparison)
- Better choice for quick scanners and users with moderate colour vision deficiencies, where hue alone is a weaker differentiator and chroma difference aids discrimination

### The key design insight

Both themes share the same hue identity and achromatic structure. The saturated version is not a different colour system — it is the same Flexoki semantic colour map with its chromatic colours pushed to the boundary of what sRGB can
represent at those hue angles. The standard theme keeps those same colours pulled back toward a more muted, ink-like quality. This is precisely the trade-off between aesthetic harmony (standard) and functional legibility through colour
(saturated).

### Explanation of Concepts and Terms

- **the sRGB gamut shell**: 
- **chroma amplification**: 
- **lightness compensation**: 
- **hue**: 
- **chroma**: 
- **lightness**: 
- **perceptual lightness**: 
- **simultaneous contrast**: 
- **constant-hue plane**: 
- **chromatic ANSI slots**: 
