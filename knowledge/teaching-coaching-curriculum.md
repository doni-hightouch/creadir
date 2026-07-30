# The coaching curriculum — what gets taught when real work goes wrong

Source: Gong transcripts of ongoing Ad Studio working sessions. Dropbox (Apr 8,
May 27, Jun 24), Fullscript deep-dive (Jun 4), Gen Digital pilot check-in
(May 27). Coaches: Kelly Wong (primary hands-on), Nate Argosh, Jared Kitade.

Attribution caution: several Gong URLs resolve to different accounts than their
Glean titles suggest (titles said JCrew / DraftKings / Veronica Beard / WHOOP;
contents were Chime, Dropbox ×2, Fullscript). Verify account names before
quoting publicly. The pedagogy is unaffected.

## The canonical coaching stack, in teaching order

**1. Root generation in your own data.** Report first, then:
> "based on this report below, create 10 new ads for [X] campaign"
— pasting the whole report. Or reference a report by URL: *"you could just grab
the URL and say, you know, build me idea number six."*

**2. When output is wrong, don't just re-prompt — encode the correction.**
Nate's stated #1 tip, given on the very first working call:

> "That's my number one tip, I guess, to make sure that we can get the most out
> of this — is like when we find areas where the system is making mistakes,
> just noting that down so that we can add that into the brand and into the
> rules."

Worked examples: a customer didn't want a sub-product featured → added to brand
guidelines. Double-logo defect → guardrail. Copy reading "a little softer" than
brand voice → *"we can make a new piece of context called the copywriting
guidelines."* Learnings from a long chat → fold back into the report prompt:

> "You could paste in the original report prompt and say like, okay, let's
> update this prompt based on everything we've talked about and all that you've
> learned, and go and update that prompt in the report. That way, the baseline
> report output is just higher quality and has baked-in assumptions from the
> conversation."

**3. Context files need "read this when X" descriptions.** The single most
concrete prompting rule in the whole corpus, discovered live while debugging why
a customer's context wasn't being used:

> "For the incremental strategy output — if that's the context file, it's super
> important to add a description. And I see that there's not a description. So
> my hunch is that maybe the agent didn't pull that context file in... because
> it uses the description to figure out which context it should read."
>
> "I usually go with like 'read this when X', rather than just saying 'this is
> our incrementality data'... I would just tell it: read this when analyzing SEM
> campaigns, read this when producing static ads."
>
> "Just to be safe, I would over-encourage the agent to pull it in."

Note the follow-on confusion — the customer thought "over-encourage" meant in
the chat. Nate clarified: *"In the description name."* **Where an instruction
lives is itself a teachable concept.**

**4. Match strictness to reality.** Asked "should the writing style be very
binary in nature — if this, then that, super strict?":

> "It's okay to be really strict, but you need to make sure that it actually
> warrants that level of strictness. Is it actually binary, black and white —
> do this and don't do this — or is there wiggle room? And if there's wiggle
> room, then you might confuse the system by being so strict."
>
> "In general, imagine you're instructing a very junior data analyst. It might
> not always be 'do X then Y' — some things might require more tips and tricks,
> like 'hey, you should probably think about this when you're analyzing our
> data.'"

He defers to Anthropic's prompting guides for the rest. Kelly's companion
heuristic — the green light / red light idea:

> "Sometimes the agent has all this great context but they don't know like,
> hey, do this or do not do this if it doesn't exceed X guardrail... instruct
> the agent in a more like 'here's a green light, here's a red light' way — so
> it's able to parse through that context better, cause even though sometimes
> you have a lot of great information, it gets a little confused."

Where strictness does help (Kelly): *"when you're instructing it to look at
certain data tables or conversion events for reporting."*

**5. Expect a bad first batch.** The best single line for a beginner:

> "The best way to be successful with the creative part of the platform in my
> opinion is to iterate — like give the agent feedback. The first batch is
> going to be the worst, right? So to get to better creative, iterate with the
> system. And number two, if there's issues that you keep running into, share
> that feedback with us so we can make the product better."

**6. Don't prompt for deterministic edits.** Use layered editing for fonts and
deletions; prompting is for concepts, not pixel tweaks. See the Fullscript font
saga below.

## Two mental models, one per surface

- **Creative work → junior designer.** "Art-direct the agent."
- **Reporting/data work → very junior data analyst.** Tips and tricks, not
  commandments.

## The recipes / ingredients metaphor (styles vs. assets)

Nate, crediting a customer's brand team:

> "These [styles] are sort of the recipes and then the assets are like the
> ingredients. So we've given it a bunch of ingredients in the asset library.
> And then the styles are these different recipes about how to use these
> assets, how to mix and match things, how to create this layout."

Build-vs-use is a real confusion point — a customer tried the style mock-up tool
and concluded the feature made things worse. The correction:

> "This area is all about building the style. And then when you want to actually
> use it, that's just in the normal ads page... I would just upload the file and
> then pick the style, and just say 'update this to use the cut shape.'"

Style creation flow: *"drop in a bunch of the ads featuring those styles, or you
can describe your style here... the AI will actually pull out and synthesize the
information that it takes from those example ads... you can continue to edit it
or delete certain things that are not accurate."* Plus a test harness:
*"you can actually test your style, to mock up an ad before adding it."*

## Context = skills (the clearest beginner definition in the corpus)

Given as the answer to "could we build our own legal agent?":

> "This is where customers will upload their legal guidelines... basically what
> you're doing is you're giving the agent sort of like skills. So you can tell
> the agent, whenever producing new ads, always review these legal guidelines,
> and it'll make sure that it's always referencing these so that everything the
> agent produces at least has a better chance of being approved."

## No tagging required — just ask

> "I would definitely encourage you all to tell the system to look at the
> creative, or also display the creative. It can go look at all the creative and
> understand what's actually in it."
>
> "That's sort of the beauty of LLMs. Like no more need to tag — you just ask a
> question and it'll go figure out what's the difference between these different
> creatives."

Customers repeatedly ask the opposite ("Is there anything we need to label?"),
so this needs stating explicitly.

## Chats don't share memory — the most instructive customer experiment

Two customers ran a genuine A/B: one spent a long session teaching a report chat
her assumptions, then had a colleague try the same scenarios from the same
report. Her hypothesis was that the agent would have learned. It hadn't:

> "Because I was going off of the same chat... would it learn from everything
> that I had been prompting it... if someone else was doing it? So Leah just
> tried the same scenarios." → "I would say the answer is no... in my chat with
> the same report, it was actually suggesting putting a lot of money in brand...
> net, there seems to be some inconsistencies even though we were both chatting
> with the same report."

The correction and the right expectation:

> "The agent does not have context of the follow-up chats from one another... it
> makes sense that as you start chatting, there might be discrepancies because
> you are having different conversations. If, based on the same context, it's
> spitting out different answers, then that would be more concerning to me."

Remedy: move knowledge out of individual chats into shared, well-described
context — the whole point of the portal.

## The Fullscript font saga — why "prompt harder" is the wrong instinct

Their prior-tool experience, which is the emotional starting point for many
users:

> "Both Dasha and I would say spent far too much time trying to get them to
> where we wanted them to be... we took that output and we gave it to the
> creative team and we said these are like 95 percent here, but we need you to
> make them beautiful... that's really not the intention of how it's supposed to
> work."
>
> "The delivered results were with the obvious, clear impression that it was
> created through AI, like some awkward stuff."
>
> "It was pretty basic stuff in my opinion, like font — it gives the illusion of
> 'change this font to Beasley' and it wouldn't do it, just didn't do it."

The design answer, which doubles as a teaching point:

> "We see that challenge a lot. I'll show you in our platform how we try to
> solve that by not using AI for the fonts and just overlaying it directly...
> we've heard very similar pain points where it gets you 90 percent of the way
> there, but then the last 10 percent is very grueling trying to prompt back
> and forth."

## Video expectations, stated honestly

> "You can ask the system to create short animations up to around 15 seconds...
> once you get longer than 15 seconds, it'll start to generate multiple clips
> and stitch them together... it's just a bit more beta. The assets that we feel
> most confident on the animation front are sort of like motion graphics, not
> full-on videos that have a storyline and a script."

On editing existing video: simple frames (a closing tagline/CTA) can be cut and
regenerated; *"if it's a complex animation with lots of things moving around,
people involved, the system is not going to be as good."*

## The improve-instructions loop ("that's magic")

> "In the spirit of teaching y'all to fish, not just writing reports for you —
> if you jump into one of these reports, there's the whole configuration... If
> we jump in here to improve instructions, you can actually just leave feedback
> for the agent to improve the report. So this is how I've been iterating with
> it. I've been saying like 'I want to add a section before hooks that compares
> [vendor] CAC versus the brand studio CAC.'"

Customer reaction: *"That's magic."*

## Homework as pedagogy

> "I have some clear homework to update this chart, but I also wanted to give you
> all some homework... it would be great if everybody asks at least a question of
> the data in the chats page, and then also tries to spin up some new ads on the
> ad studio page — to just get everybody more comfortable with the platform."

## The operating model, stated as doctrine

Consistent across all accounts:

> "The design team is responsible for owning the foundation layer — how do we
> encode our brand into a system or tool so that AI can understand it? ... They
> set the guardrails, the constraints, but then the marketers are able to really
> scale up into lots of different ideas and assets."
>
> "We see the most success when we have performance marketers actually building
> the assets, but it's important that we get the design team's input into
> setting up the guardrails... we want to avoid a scenario where you build all
> these assets, and then you bring them to the brand team and they have all
> these nitpicks and issues and then we have to go back to the drawing board."

The two failure modes it sits between:

> "One is the design team gets new tools to try to speed up their process, but
> it's kind of siloed from the marketing team. And then the opposite... the
> marketing team is like, okay, let's just automate everything about the design
> process. And the teams that we're seeing adopt AI most successfully are
> landing somewhere in between."

## The central unsolved problem customers name: consistency

The best articulation of why a training portal is needed at all:

> "Clearly the capability is there, now it's about consistency... they're
> clearly happy — pretty close to the outputs that [the Hightouch designer]
> is able to get, I'm not getting those, like the same quality. So how do we
> make that more repeatable? ... It feels like we're right there, it's just how
> do we tweak the workflow or the inputs a little bit."

Expert operators get great output; novices with the same tool don't.

## Failure modes to design the curriculum around

1. **Expecting cross-chat memory / shared learning.**
2. **Not knowing where an instruction lives** — chat vs. context vs. context
   *description* vs. style vs. report prompt.
3. **Believing tagging is required.**
4. **Empty states read as a broken product.** The strongest trust hazard
   observed: a customer couldn't find performance data mid-call —
   *"I still don't see any of the performance data within there, am I missing
   where it is?... I was looking pretty much everywhere."* It was a backfill in
   progress. Nearly derailed the session.
5. **Prompting endlessly for deterministic edits** (fonts, deletions).
6. **Being unable to judge output quality themselves** — *"it looks different
   when you use the styles versus the other one, but I just don't know which one
   they're going to like more"*; *"I'm not a creative person, so I'll have to
   defer to others"*; *"I have absolutely no inkling or creative bone in my
   body."*
7. **Distrusting unexplained AI classifications** — *"How did you classify a
   climber?"*; *"it didn't tell me why it suggested it."* Customers stress-test
   every AI-derived number, and rightly insist AI-invented methodology be
   replaced with their own definitions.
8. **Jargon in AI output the operator can't decode** — a customer had to ask
   *"is FSS file storage?"* about the report's own abbreviation.
9. **Not knowing a capability exists** — *"I didn't know we could pull
   individual visual assets and get down to that level."*

## What keeps customers engaged vs. what discourages them

**Engaged by:** fast iteration (statics down to ~3 minutes; *"it's gotten a lot
faster"*), visible responsiveness (bugs owned in-call with concrete timelines,
including *"I must've missed that. Sorry."*), magic-feeling loops
(improve-instructions), proactive coaching (Kelly literally watches usage:
*"I see Lucy prompting, maybe I should just reach out to her"* → customer:
*"I feel like you read my mind sometimes"*), homework that forces reps, uncapped
usage instead of credits, and quick mundane wins (resizing to lift Google ad
strength).

**Discouraged by:** brand/legal approval stalls, defects in live assets forcing
manual audits, the agent refusing or deflecting mid-analysis (*"you've pointed
out a good flaw, good catch"* instead of complying — the customer *"kind of
stopped my work there"*), "obviously AI" polish gaps that force creative rework,
empty states, and definitions they already supplied not making it into the build.

**The turnkey wish, worth noting as a design tension:** *"I'd like to just push
go. That sounds kind of lazy but it'd be nice."*
