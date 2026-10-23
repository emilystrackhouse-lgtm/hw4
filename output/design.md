# Homework 4 — Design: "Elm City After Dark" (Problem 10)

**The idea:** *Avatar*, but for Yale. Yale after nightfall is reimagined as a bioluminescent world. The old elms and gothic towers glow Yale blue, points of light drift through the air like glowing seeds, and every product sits in its own lit display case. The theme is still Campus Customs: the navy and Yale-blue palette, the condensed collegiate type, and the "Est. 1975" seal all stay. It's the shop across from Old Campus, seen at its most magical hour.

## What changed

**Colors**
- Daylight white became a deep night sky (`#040a17` to `#0e2347`), lit by a bioluminescent Yale blue (`#6fd3ff`).
- Small touches of aqua and aurora violet add depth.
- Text is near-white, with muted blue-gray (`#a9bdd8`) for secondary text, both readable against the dark background.
- Product photos keep a bright white backdrop, so the clothes stay true to color and pop against the dark.

**Fonts**
- Archivo Narrow stays for the athletic, collegiate headings.
- New: **Fraunces italic**, a soft, old-style serif, for the hero's signature line ("*the shop's still lit.*"). It's filled with a glowing blue-to-violet gradient. The pairing of classic serif and sporty sans says "old university, young energy."

**Signature effects** (all original, drawn in code)
- **Elm spores** (`Spores.tsx`): about 40 to 110 points of light drift up behind every page, twinkle, and **brighten and grow when the pointer passes near**, so the page responds to the shopper.
- **Glowing skyline** (`Skyline.tsx`): a silhouette of a Harkness-style tower, chapel roofs, spires, and elm canopies along the bottom of the hero. Its windows glow and flicker.
- **Lantern glow:** a soft pool of light follows the pointer across the hero.
- **The seal:** it now floats inside a slowly turning ring of blue, violet, and aqua light.
- **Entrances:** the hero headline rises in line by line. Sections and product cards glide in as you scroll (CSS scroll-driven animation, no extra code).

**Clearer visual hierarchy**
- One hero message, one bright primary button ("Shop the collection," lit from within with a gradient), and quieter outlined secondary buttons.
- Prices glow in Yale blue everywhere, so the eye always finds the price.
- Glass panels with soft halos (cards, the toolbar, forms) separate content without heavy borders.

**Product displays**
- Cards are **glowing display cases**: they tilt a few degrees toward the pointer, lift, and light up, and a sweep of light crosses the photo on hover.
- A **"Few sizes left"** badge marks styles with 3 or fewer sizes in stock.
- On the product page, the item floats gently on a **lit pedestal** with a blue and violet glow beneath it.
- Size tiles glow: aqua for "Only N left," dimmed for sold out.

**Chat experience**
- The **Ask us** button is a breathing orb of light, a guide spirit for the store.
- The panel is frosted glass with a Yale-blue-to-violet header.
- Shopper messages are lit blue bubbles, and replies and product cards glide in.
- The chat's product cards share the glowing look of the main grid.

**Care**
- Shoppers who choose "reduce motion" in their device settings get a still version: no drifting, tilting, floating, or pulsing.
- Focus outlines glow, so keyboard users can see where they are.
- The light field pauses when the tab is hidden, to save battery.
- The theme lives in one file, `frontend/src/theme.css`, loaded after the original styles.

## Why it should help sales

- **A reason to linger.** The drifting light, the lantern, and the tilting cards respond to every movement. Browsing feels like exploring, so shoppers stay longer and see more products. That's the strongest predictor of buying.
- **The product is the star.** Bright white photos inside glowing cases on a dark stage pull the eye straight to the clothes, as a lit shop window at night does. Glowing prices remove the "how much?" friction.
- **Clear next steps.** One bright button per screen, lit cards that clearly invite a click, and an always-glowing chat orb guide shoppers from looking to asking to buying.
- **Gentle urgency.** "Few sizes left" badges and glowing low-stock size tiles nudge decisions without pressure.
- **A memorable, giftable brand.** "When the elms glow blue, the shop's still lit" turns a merch store into a feeling, proud and nostalgic and a little magical. That's exactly what parents, alumni, and students are buying when they buy Yale gear, and an experience worth sharing is free marketing.
- **Trust intact.** It still reads as Campus Customs: the same navy-and-Yale-blue palette, the collegiate type, the Est. 1975 seal, and the family story. It's distinctive without feeling like a different store.
