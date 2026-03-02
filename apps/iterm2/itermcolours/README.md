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

- **the sRGB gamut shell**: The outer boundary of all colours expressible in the sRGB colour space. Beyond this boundary a colour is "out of gamut" and cannot be displayed on a standard monitor. Colours pushed against the shell have at least one RGB channel at 0 or 255 — they are as vivid as the display allows for that hue.

- **chroma amplification**: Increasing the colourfulness of a colour without changing its hue. In practice this means moving the colour farther from the neutral grey axis in colour space, making it appear more vivid and saturated. Distinct from simply turning up a "saturation" slider, which in HSL space can distort lightness.

- **lightness compensation**: A deliberate reduction in lightness applied alongside a chroma increase, to prevent colours from becoming visually overwhelming or losing legibility against the background. The two adjustments partially cancel each other's perceptual effect, producing a colour that is more vivid but not brighter.

- **hue**: The attribute of a colour that corresponds to its position on the colour wheel — the quality that makes something appear red, green, blue, yellow, and so on. Hue is independent of how bright or vivid a colour is; a pale pink and a deep crimson share the same hue.

- **chroma**: The degree of colourfulness of a colour relative to a neutral grey of the same lightness. A high-chroma colour appears vivid and saturated; a low-chroma colour appears muted or greyed-out. In perceptually uniform models (LCH, Oklch), chroma is a more reliable measure of colourfulness than HSL saturation because equal numerical steps produce equal perceived differences.

- **lightness**: In HSL, the proportion of white or black mixed into a colour, ranging from pure black (0%) through the pure hue (50%) to pure white (100%). This is a mathematical definition and does not correspond reliably to how bright a colour appears to the human eye — a fully saturated yellow at 50% HSL lightness looks far brighter than a fully saturated blue at the same value.

- **perceptual lightness**: A measure of how bright a colour actually appears to a human observer, as modelled by perceptually uniform colour spaces such as CIELAB (L\*), LCH, or Oklch. Colours with equal perceptual lightness appear equally bright regardless of hue — something that HSL lightness does not achieve. Designers use perceptual lightness when they need text or UI elements to feel visually balanced across different hues.

- **simultaneous contrast**: A psychophysical phenomenon in which the perceived colour of an area is influenced by the colours surrounding it. A grey square looks slightly cooler on a warm background and slightly warmer on a cool background. In terminal themes, highly saturated chromatic colours can make the shared neutral background appear to shift in hue or temperature, which may affect reading comfort over time.

- **constant-hue plane**: A two-dimensional slice through a three-dimensional colour space (such as HSL or LCH) in which the hue angle is fixed. All colours on this plane share the same hue but vary in lightness and chroma. Moving a colour "radially outward" within its constant-hue plane means increasing chroma while staying on the same hue — the operation performed by the saturated Flexoki variant.

- **chromatic ANSI slots**: The sixteen ANSI terminal colour slots (0–15) split into achromatic slots (0 = black, 7 = light grey, 8 = dark grey, 15 = white) and chromatic slots — Ansi 1–6 (the standard red, green, yellow, blue, magenta, cyan) and their bright counterparts Ansi 9–14. It is only these twelve chromatic slots that carry hue and are used for syntax highlighting; the four achromatic slots carry no hue and are unchanged between the standard and saturated themes.
