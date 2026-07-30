# What customers actually struggle with (Ad Studio)

Source: Hightouch internal PM doc "Making creatives more successful" (Nate
Argosh), plus the "Ad Studio Workshops" playbook. This is the single most
important input for the training portal: it is the honest internal account of
where real users fail.

## The core diagnosis

> "It's unclear to designers how to really leverage AI in their workflows.
> They don't have a clear mental model of what ad studio knows and does and
> what their role is in steering it."

Two halves to that: **what the system knows** (context) and **what my job is**
(steering). Every customer failure below is one of those two halves missing.

## Customer evidence, by account

**Staples (enterprise)** — Designers didn't know what to prompt in the
workshop. They fell back to out-of-the-box prompts or the "test prompts" from
the slide. They explicitly asked for prompting training:

> "Is there anything you guys could share with us that would be helpful for
> the agent generation? ... with all AI there are certainly **prompting best
> practices** and it would be helpful for us to get them."

And they didn't know the boundary between what the system already knows and
what they must say:

> "And also understanding **what's built into the context docs** — not that we
> need to understand everything, but if there's stuff the agent already knows
> that we don't have to tell them... understanding it a little bit as like a
> working doc."

Also: one of their designers can use Weavy; "the others are lost."

**EF** — Designers hadn't used any AI creative tools.

**Rakuten (enterprise)** — "It wasn't clear to them how the tool actually
clicks into their current workflows. What do I do with this?"

**Otrium** — Designer didn't know the tool could do video, or animated text.

**Dropbox** — The designer they worked with had never used AI creative tools.

**Fullscript** — Designers hadn't used any AI creative tools.

**Chime** — Their designer was already AI-fluent and a power user, and *still*
her biggest challenge was figuring out where Ad Studio saved her time "vs
being prompting hell." The unlock:

> She finally felt like she unlocked this when she transitioned from
> specifying every little design detail to "**art directing the system**" —
> uploading interesting imagery and having the agent riff on them to come up
> with **lots** of ads at once. This workflow was not clear to her as an
> option from the start.

**Block** — Their marketer/designer is "pretty AI pilled" but still didn't
know everything the app could do (e.g. motion graphics).

**The Key** — Their pseudo-designer doesn't understand her role. She's used to
designing every individual ad in Canva, so she expects Hightouch to "just spit
out final polished ready to go ads." She's not seeing that there's an
in-between where she has a role in guiding the system.

**Gen Digital (counter-example)** — Designers constantly push the system,
quite AI-fluent, would benefit from advanced controls. Even they don't know
how to make good UGC on Ad Studio.

## The double-persona pattern

Hightouch sees a clear split requiring two modes:

1. **Safe mode** — a marketer uses templates and styles to create assets that
   follow stricter guidelines.
2. **Free mode** — a designer uses the tool to create genuinely new assets.

Practical governance strategy Nate recommended at Fullscript: non-designers
work inside locked styles; the creative leads use "no style" to push direction
freely; transition the org over months.

Also worth remembering for enterprise: they are *not* firing design teams so
marketers can self-serve. The realistic goal is meeting creatives where they
are and bringing them along the AI maturity curve.

## What designers SHOULD be doing (the five behaviors)

This is effectively the curriculum. Each is described internally as
non-obvious to users:

1. **Reference existing assets/work.** Use assets already in the workspace, as
   is or modified. You can reference by name or by vague description ("a blue
   sweater") across uploaded assets, catalog products, and past ad creative
   that was pulled in automatically. HTML templates make the agent strictly
   respect type styles and spacing. *"This is unclear"* to users.
2. **Ask for many outputs at once.** "One of the most effective ways to use
   the system but it's non obvious. You have to ask for many outputs."
3. **Explore different formats and workflows** — motion graphics, UGC,
   slideshows/GIFs, memes, re-slicing existing videos, adding text overlays
   and end cards to videos.
4. **Iterate within the chat** — including bulk-selecting ads and asking for
   changes across them.
5. **Kick off lots of chats at once** rather than waiting for one to finish.

Aspirational (not yet reliable): teach the agent what's good and what isn't;
jam back and forth quickly.

## The workshop playbook (how Hightouch teaches it live)

Hard prerequisite: **at least 2 weeks of prep with access to the client's
design team.** And: *do not proceed with the workshop until the customer's
design team agrees the outputs are on brand.*

**Prep principle — "raise the floor":** set the workspace up so that on
workshop day, marketers can "input any random prompt under the sun and get
outputs that look on brand." Setting up styles is called a **must-do** because
styles raise the quality floor.

Critically, prep testing must use **very basic prompts**, not sophisticated
ones — deliberately mimicking what a non-designer will type on the day.
The literal test prompts used:

- `Make 10 ads`
- `Make ads in the style of the attached images`
- `Make an ad for <x>. Give me 9:16 and 1:1`
- `Turn this into a 9:16` (with an image or video attached)
- `Analyze what's working on meta and make a winning campaign`
- `Generate a carousel for <x>`
- `Make an ad for my product: <link to my site>`
- then prompt an edit on an ad you just made

**Workshop-day structure:** Intro → Insights & Reporting → Creative → Working
time. Attendees must include marketing *and* design. Give the team very
specific goals, e.g. "make 50 ads," "set up a report," "find an interesting
insight about a competitor." Give them time to actually use the tool.

## Implications for the training portal

- The portal's job is to install the missing mental model *first*: what the
  system already knows vs. what you must tell it. That is the #1 documented
  confusion.
- Teach "art direct the system" as the target behavior, not
  specify-every-detail. That's the documented moment of unlock even for a
  power user.
- Teach volume early (ask for 10, not 1) — high leverage, low obviousness.
- Teach references as the primary input, since users don't know they can
  point at existing assets at all.
- Surface capability discovery (motion, UGC, carousels, resizing) — repeated
  evidence that users simply don't know these exist.
- Assume zero AI experience and no vocabulary. Basic prompts are the realistic
  starting point; the ladder should climb from `Make 10 ads`.
