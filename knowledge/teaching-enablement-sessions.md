# Enablement sessions — teaching real customers to prompt

Source: Granola transcripts. Brilliant Earth AMP enablement (Jul 22), Fullscript
POC check-in (Jul 27), Chime weeklies (Jun 30 Context Hub, Jul 22 approvals,
Jul 29 insights), EF workshop prep (Jun 29, internal).

Attribution note: in these transcripts **Doni Goodman does most of the hands-on
teaching**; Nate contributes the strategic framings (styles-as-guardrails,
shots-on-goal, brand-profile architecture, "select no style and push it").
Granola mislabels speakers often — verify before attributing publicly.

## The three-layer mental model (Nate's clearest articulation)

From the Fullscript governance conversation — this is the answer to "locked vs.
freeform" and belongs at the center of any customer guide:

> "Generally the brand context should be used by everybody — just have some
> good sensible rules in there around logo usage, basic stuff. And then really
> where we see the difference between workflows is styles. The non-designers
> would use styles where there's a lot more baked-in guardrails. And then if
> someone like yourself, Ryan, wanted to try to push the platform to new
> places... select no style and then try to push it."

> "It's almost like two different modes we're trying to unlock — there's a more
> locked-down version that the non-designers could use to make some simple
> things, and then obviously giving you the freedom to push the platform
> outside of these styles."

Target end state: *"ultimately the goal should be like Fullscript v2, which is
one profile that works for everybody... and then a set of styles that you can
optionally use."* Transitional plan: old profile for marketers (safe,
approved), new profile for creative leads' rebrand work, converge over months.

**Styles defined for a beginner:**

> "A style is like guardrails that you give the platform so that it helps
> generate closer to what you're looking for, so that typography, photography,
> buttons are all considered specifically to this style."

And why setup pays off: *"getting set up is a little bit more efficient so that
your prompts — you don't have to kind of think of each thing to not do or do."*
Nate: styles mean *"you can use really simple prompts then to get high quality
outputs."*

## The single most-repeated technique: references

> "If you have a reference of something that you like, that's like the best way
> — just the easiest, heaviest hitting, best way to get more ideas in that
> generation."
>
> "Image references is like one of the best ways I would say to sort of art
> direct the system... if there's like a competitor's ad or a photo shoot from
> another brand that you really like, you can just come here and grab an image."

**Critically — say what you liked about it.** This is the difference between a
reference working and not:

> "If you give it a vague 'I like this image, make more,' it doesn't know what
> you liked about it necessarily. So if you say 'I love the color grading in
> this photo' or 'I love the lifestyle photography' or 'I love the scale of the
> elements' — those are sort of art-direction-style inputs that help it know
> what you're looking for."

## Word choice teaches intent — the "riff" lesson

Asked why he changed "create" to "riff" mid-prompt:

> "Riff is just a bit more exploratory... it's just gonna take elements from it
> but not specifically. I would say like explore, riff, or ideate, come up
> with."

And how to escape established styles without going off brand:

> "Break out of the current established styles but make sure it feels on
> brand... the 'on brand' will look at the brand guidelines, it'll look at the
> fonts, but it won't be referencing specifically these established styles."

## No special syntax required — the reassurance novices need

> "You don't have to code or know any sort of markdown language... it's really
> normal speak, but it's just speaking very pointedly at what you're looking
> to change."

The customer's own relieved paraphrase (Ryan Yuke, Fullscript) is the best
possible summary line for a beginner guide:

> "It sounds like it's just think critically and speak to it like you would
> anyone else and it'll get you what you need."

## Shots on goal — ask for volume

> "Another big tip I have is asking for a lot of assets at once because you get
> more shots on goal and it's just more likely for one of them to be good. So I
> usually ask for 10 — more than 10 it might start getting slower."
>
> "You can just say give me five images or 10 images so that your chances of
> getting one that you're more likely to choose is better."

Plus parallel work: *"while this is running, often I'll go back, click ads and
launch a new idea... you can just keep on pumping a bunch of those."*

## The prompt toolkit (guide-ready, all taught live)

- **Constrain what you don't want:** *"normally you would want to establish
  'this is just a photo, don't include any text or copy.'"*
- **Leave room for CTAs** — a customer repeated it back, which is how you know
  it landed: *"say like account for blank space along the bottom third of the
  image."*
- **Anchor to real products:** *"always go and look at the product catalog to
  find real SKUs so that it doesn't make products that we don't actually sell."*
- **Anchor to performance:** *"based on our top performing ads, our highest CTR
  ads, create 10 new ads."*
- **Fix stocky output:** *"make sure the photography feels 100% authentic and
  real."*
- **Force variety:** *"create more variety in photography so that each layout
  feels original"* / *"give me completely new layouts for each one."*
- **Iterate from winners:** click an ad you like into the chat — *"I like the
  original photography and layout here, please give me 10 more ideas, make sure
  each are completely different."*
- **Isolate edits (fixes the biggest frustration):** *"just explicitly say
  'keep the overlay exactly the same, only edit the background video.'"*
- **Disambiguate elements:** for a stubborn asterisk, *"'the asterisk in the 3D
  type' might be a better way"* — name which one when several are similar.
- **Give dimensions in words:** *"just saying like make me a 100 pixel by 150
  pixel ad and it'll generate within those constraints"*; also *"ask it to keep
  the phone aspect ratio at 9 by 16."*
- **Resize inside the platform, before export:** *"the resizing works best when
  Hightouch creates the asset"* — re-imported assets resize less reliably.
- **Curate ruthlessly:** *"if something is totally wonky and there's nothing in
  it that you want to keep, just delete it."*
- **Batch-select and re-prompt** across several outputs at once.
- **Promote recurring fixes into Context Hub** so nobody has to remember them:
  *"maybe we can add that to the context layer."*
- **Watch the reasoning trace:** *"if you're curious what's happening behind
  the scenes, you just click here... the part that you'll understand is
  reasoning. I always like to watch what it's doing."*
- **Just try it:** *"I'd recommend that you just try it out — always just try it
  out first, see what you get, and then we can keep sharing."*

## Compliance as context (Chime)

The Context Hub explanation, with disclosures as the example:

> "This is where you can upload any relevant context — copywriting, disclosures
> for example... it tells the agent, when there is this trigger word like
> 'third parties' or 'spot me $200,' you always have to overlay the following
> disclosure at the bottom of the ad."

Demoed live: a general prompt ("#1 most loved banking app") auto-triggered the
correct disclosure overlay. Customer reaction: *"this is really cool and really
helpful."*

## Five predictable customer gaps a beginner guide must close

**(a) Input-quality misattribution.** Dave (Fullscript):

> "It's taking our shitty looking ads and just making more of them, and maybe
> incrementally making them look a little better. But again, it's garbage in,
> it's garbage out — we don't have great photography... I haven't been
> disappointed yet, I think it's interesting."

**(b) Self-blame vs. tool-limits confusion.** Ryan Yuke — the exact voice of a
capable professional with no AI experience:

> "Where I started to hit a wall was when I started to push it to art direct
> for me... is it because I'm not an art director and I'm not very good at
> prompting it? But I'm also thinking, am I expecting it to do too much
> critical thinking than it's capable of? Because it is really good at
> replicating style... do I need to upload examples of creative that I like so
> that it can try and replicate those?"
>
> "I can't truly evaluate this until I have more confidence in my own
> prompting."

**(c) Edit blast radius.** JoJo (Chime art director):

> "When I reprompted, even when I said okay enlarge this card... it gave me
> completely different one, completely different animation. I basically want
> the same animations, I just want to enlarge that video."

Also anthropomorphizing uncertainty: *"I have asked 'make the asterisk smaller,
please' — I don't know if I have to say please."*

**(d) Overwhelm.** Sarah (Chime) — the strongest argument for a guided
curriculum:

> "What we're trying to figure out is like what's the best use case of
> Hightouch?... because I think sometimes it's like overwhelming. There's like
> so much that it can do and we get in there and then we're like, oh my gosh,
> it's like cognitive overload. So please, let us know, steer us in the right
> direction."

Erica (Chime) asking for exactly this portal: *"can we do some sort of more
intensive onboarding or boot camp... I know we're definitely scratching the
surface, but I think it's also a part of us not having dedicated time to really
go deep."* And Megan on day one: *"are there guides and best practices for
sample prompts and stuff like that... specific to Chime, or is there
generalized guides at all?"*

**(e) Trust and QC anxiety.** Dave: *"I have nothing but faith that Ryan and I
will inspect every single ad... but all the other ads — I feel like once we give
these keys over to some people..."* Answered with: *"the guardrails will
help... we're kind of making this for the lowest common denominator so that
it's generally outputting the best and most effective pieces without needing a
microscope."*

Related real failure modes customers hit: stereotype outputs (*"every doctor is
wearing a white lab coat and a stethoscope. And I'm like, that doesn't look
like a registered dietitian"*), wrong-audience slips (*"whoops, I forgot you're
talking to provider, not a patient"*), and domain constraints AI can't guess
(Fullscript legally can't show branded supplement bottles).

## Discovery beats a prepped demo

At Brilliant Earth the prepared demo (promo banners) was the wrong use case and
got discarded live — the customer said *"that's just such a small use case for
us, honestly."* Value clicked only when the tool was pointed at their real
problem: photography they never shot (color diamonds, pinky rings,
cross-category shots). Lesson for the portal: let users bring their own problem
early rather than walking a fixed script.

Also, the templating objection worth pre-empting: *"what's different from us
versus like ads is they're very rinse and repeat, they're very templated. We're
not... we are all over the place, so it's hard to find like it's always going to
be text here and it's always going to be CTA here — that's just not how we
operate."*

## The workspace-prep methodology (internal, EF prep)

> "There's the first step, which is just setting up the bare bones of the
> workspace. And then there's another step, which is adding in the right
> guardrails so that on Wednesday, when people are asking for assets, it's
> producing what they would expect."

- Encode the customer's actual intent as a guardrail (e.g. EF didn't want net
  new imagery — only overlays, expansion, cropping, text).
- Brand-guideline PDFs are run through Claude with an extraction prompt before
  loading into Context Hub, then QA'd.
- Pre-workshop dry runs to confirm outputs are "on brand and on brief."
- Asset hygiene (fonts, logos) is the unglamorous prerequisite — a whole call
  chunk went to debugging corrupted font files.

## Adoption North Star (Chime, Jul 22)

> "We are going to try to produce at least 40 to 50% of our creative — at least
> for statics and lo-fi motion — using Hightouch by end of year... we're trying
> to get to 7,000 delivered assets by end of year. We are at 4,000 right now...
> that was pre-Hightouch, that was pre-AI."

## What makes value click

Never the generic demo. It's the customer's own hardest problem solved live —
Brilliant Earth's unshot photography, Fullscript's Hims-quality riffs, Chime's
auto-applied disclosures — plus visible performance data (*"I just want to know
what's working"*).
