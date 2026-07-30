# Ad Studio Operator Manual — Zero to Finished Ad

Source: Hightouch Ad Studio, self-documented in response to a structured
interrogation (2026-07-30). This is the tool describing its own observable
behavior at the interface. Treat internals claims with care; behavior claims
verified against real usage read as accurate.

The one-sentence version: **Give it a clear message and a real product image
and it handles the craft; leave those vague and it guesses — and its guesses
look generic.**

---

## Stage 1 — Setup (the context it stands on)

Context loading happens before a single pixel is drawn. An admin loads it
once per workspace: brand guidelines, business context, copywriting guide,
product catalogs, logos, reference images, disclosures, saved styles, synced
reference ads.

It treats these as the constitution for every ad — exact hex palette,
approved fonts, voice rules, and hard prohibitions come from the loaded
files, not from memory or the brand's public fame.

**What changes output the most (ranked):**
1. Product/food images + logos — the single biggest lever. It cannot draw a
   product from words; it reproduces it from a reference file. No file =
   hallucinated packaging.
2. Brand guidelines — palette, typography, imagery rules set the entire look.
3. Copywriting guide — governs every word.
4. Business context — audience, personas, value props shape the angle.

Optional/situational: saved styles, synced reference ads, disclosures,
competitor data.

- Strong setup: transparent-background logo PNG, clean product photo on
  white, guidelines with named hex tokens and font names → on-brand on the
  first try.
- Weak setup: no logo, no product image, "use our brand colors" with no
  hexes → approximations that look off-brand.

Common mistake: assuming it "knows" a famous brand. It follows loaded files,
not reputation.

> **Rule of thumb:** If a product appears in the ad, its image must exist in
> the workspace — products render from files, never from fame.

## Stage 2 — The brief

| Must be stated | Inferred if unstated |
| --- | --- |
| What product/offer the ad is about | Aspect ratio (defaults 1:1) |
| The core message, or permission to choose one | Number of ads (defaults ~5 for "a few") |
| Any mandatory copy, claim, or CTA | Palette, fonts (from brand files) |
| Format/channel if it matters | Audience and tone (from business context) |
| How many ads | Composition and hook style |

- Minimum viable: "Make an ad for the Pimento Cheese Chicken Sandwich."
- Ideal: "Make 3 square Meta ads for the Pimento Cheese Chicken Sandwich
  targeting busy parents. Lead with the 'made with care' angle, warm and
  hospitality-first, no discount language, horizontal logo top-left."

Common mistake: packing five ideas into one ad. One ad = one bet.

> **Rule of thumb:** Tell it the one thing a viewer should remember; it
> designs everything else around that.

## Stage 3 — Prompting mechanics (the vocabulary it rewards)

It converts words into a visual-execution spec. Concrete nouns and
placements execute faithfully. It responds best to spatial, sensory, and
exact-string language.

- Layout: "top-left logo," "headline across the upper third," "product
  centered with generous white space," "CTA pill lower-center."
- Copy: exact strings in quotes.
- Imagery: "bright natural daylight," "appetizing hero shot on white,"
  "no clutter."
- Typography: name the loaded font and weight — "Apercu Bold headline,
  sentence case."
- Color: named hex tokens — "CFA Red #DD0031 field, white text."
- Format: "1:1 square, 2048×2048" or "9:16 for Stories."

**Vague → expert ladder (output quality tracks specificity):**
1. Vague: "Chicken sandwich ad." → invents everything; generic.
2. Basic: "Square ad for our spicy chicken sandwich, on brand." → right
   palette, guessed message.
3. Solid: "Square Meta ad, spicy chicken sandwich hero on white, warm
   hospitality tone, headline about quality." → on-brand, clear focal point.
4. Strong: "1:1 ad, sandwich centered on white, headline 'Made with care' in
   Apercu Bold upper third, CFA Red logo top-left, no CTA, no discount
   language." → predictable and polished first pass.
5. Expert: "1:1 2048×2048 Meta ad. Sandwich hero centered on #FFFFFF with
   generous negative space. Headline 'Made with care.' in Apercu Bold,
   sentence case, near-black #2D2926, upper third, rendered once. Horizontal
   logo top-left with clearspace. No CTA, no watermark, no duplicate text.
   Warm, bright, appetizing." → near-exactly a designer handoff.

Common mistake: subjective adjectives with no anchor — "pop," "modern,"
"premium," "clean." Unmeasurable words don't move the canvas.

> **Rule of thumb:** If a word can't be pointed at on the canvas, it won't
> change the canvas — swap adjectives for placements.

## Stage 4 — Generation (what it decides for you)

Once briefed, it plans the concept, generates a full mockup, decomposes it
into an editable base image plus text overlays, and saves automatically.

It decides on your behalf: hook angle (unless copy dictated), composition,
sizes (default 1:1 at 2048×2048), variant differentiation axis (message,
product, persona, or format), and which logo/product assets to attach.

It will NOT: invent a product, fabricate a statistic, add an unrequested
CTA, or override a brand prohibition.

Common mistake: expecting it to ask clarifying questions before generating.
In build mode it proceeds; thin briefs get defaults, not questions.

> **Rule of thumb:** Silence in the brief becomes a default in the output —
> decide the things you care about before it generates.

## Stage 5 — The revision loop

A **targeted edit** modifies only what you name, preserving everything else.
A **regenerate** throws out the execution and starts a new concept. Refine
with targeted edits; regenerate only when the whole direction is wrong.

Edits that work (concrete, single-target):
- "Make the headline the focal point — increase its size, move it to the
  upper third."
- "Swap the CTA text to 'Order now'."
- "Increase white space around the sandwich; shrink it to 60% width."
- "Change the background field to #DD0031 with white text."

Edits that fail (unmeasurable): "make it pop," "more premium," "feels off,
fix it," "modernize it." Translate the feeling into a lever — "pop" usually
means more contrast, bigger headline, or more negative space; say which.

Common mistake: chaining many edits into one vague sentence, or regenerating
when a one-line targeted edit would fix it.

> **Rule of thumb:** Name the element and the change — "bigger headline,
> upper third" beats "make it pop" every time.

## Stage 6 — Styles and consistency

Saved styles are reusable visual guidance (dimension prompts + reference
images) on the brand profile. A bound style prepends its references to every
generation. Same style across ads keeps palette, composition energy, and
type treatment consistent so a set reads as one campaign.

- Create a style from a look you like so it's reusable.
- Apply by naming it.
- Keep campaigns consistent by fixing style + one message, varying only
  execution ad to ad.

Common mistake: re-describing the desired look in prose every time. Prose
drifts; a saved style doesn't.

> **Rule of thumb:** Fix the style and the message; vary only the execution
> — that's what makes many ads feel like one campaign.

## Stage 7 — Finishing (export and handoff)

Each saved ad carries an editable SVG overlay, base image assets, and a
composite. Shipping to a channel means resizing into that channel's exact
canvas (Meta 1:1 1024×1024, 9:16 768×1376, Google 1.91:1 1200×628), reusing
the same base and reflowing overlays.

Pre-ship checklist:
- Copy spelled correctly, appears once (no duplicated headline)
- Product matches its reference — packaging, colors, on-pack text
- Right logo variant, legible, clearspace, adequate contrast
- Palette and fonts match brand tokens; no invented colors
- No unrequested CTA, watermark, or placeholder text
- No prohibited content per brand rules
- Right sizes exist for every launch channel

> **Rule of thumb:** Approve one master, then resize into each channel's
> exact canvas — never stretch one size to fit all.

## Stage 8 — Boundaries

Genuinely can't:
- Invent a product accurately (no reference = hallucinated packaging)
- Fabricate facts or stats
- Manufacture a logo variant that isn't loaded
- Edit stored brand/context files
- Guarantee performance

Does less well:
- Long small legal text rendered pixel-perfect in-image
- Precise data charts baked into a creative
- Unanchored subjective requests
- Many products in one frame (quality drops past ~3; use a grid)

Users wrongly assume: "you know our brand" (it follows files), "make it go
viral" (it optimizes craft, not outcomes), performance analysis while
building (opt-in only), editing brand guidelines (read-only).

> **Rule of thumb:** It turns clear decisions into polished ads fast — but
> it can't make the decisions, invent the facts, or draw a product it's
> never been shown.
