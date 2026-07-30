# How Ad Studio is actually taught — onboarding & working sessions

Source: Gong transcripts of hands-on Ad Studio sessions led by Nate Argosh and
Kelly Wong. Chime (Jul 29, creative team onboarding), Lume/Mammoth Brands
(Apr 16 + Apr 23 weeklies), DoorDash for Business (Apr 23). Quotes verbatim.

## The load-bearing mental model: art-direct a junior designer

Nate's canonical framing, which resolves nearly every novice confusion:

> "One of the big differences between prompting in Hightouch and like
> prompting let's say like Gemini directly or like one of the image models is
> that Hightouch can like go and reference different things for you. It can go
> and do like research. It can come up with ideas for you. It can also create
> many things at once. So like the way I like to think about it is you're sort
> of like art directing the agent — like treat it as your sort of like junior
> designer that you can assign work to."

Delegate outcomes, not pixel specs:

> "Rather than having to say it like really specifically like I want one asset
> with this copy and I want the person on the left... you can say things like
> I want to come up with 10 new assets for my organic channels... lifestyle
> imagery seems to be performing well, so lean into that and come up with
> different copy angles that you think might work."
>
> "You can kind of like give it direction but also leave it ambiguous and it
> can go and, you know, look at your data."

A customer (Jeff, Lume) independently converged on the same distinction —
worth quoting in the guide because it's the user's own words:

> "Higgsfield's different... You need to be very prescriptive of what you're
> building... it's just a more literal tool. Whereas this is a little more
> wide open... you start more at the brand context level than you do at like
> an inspiring image level."

## The teaching order (consistent across calls)

1. **Calibrate first.** Before demoing, Nate asks: "Have you all been in
   Hightouch before, tried to make any assets?" and "How much experience do
   you have using any other AI creative tools?" Plus which formats they need.
   The Chime call literally restarts the in-progress demo to do this.
2. **Where ads live** — projects/folders.
3. **The layers of guardrails**, always before prompting:
   > "There's a couple of different levels of like baked in guardrails and
   > context that we give the system. You can see all of that context in
   > the UI."
   - Context Hub: brand basics (logos, colors), file library (copywriting
     guides, brand guidelines), disclosures — stressed as user-owned:
     *"You don't have to wait for us. If you want to make changes, you can
     always come in here."*
   - Styles as the second layer = trained per-campaign instructions (casting,
     poses, lighting). Framed as **bumpers**: *"we want to give it bumpers so
     that it's going to be creating in a specific style."* On Auto:
     *"auto is like for the lowest common denominator... you don't want no
     style because then it's just going to make something completely
     off brand."*
   - Assets = *"building blocks for the ads... pieces that you want the system
     to use directly or to sort of like rip on."*
   - Reference images = *"to give the system a sense of the visual range."*
   - Data context files = *"the persistent context and memory that the agent
     always operates on top of."* Low friction: *"You can just come in here,
     hit add context and just start tapping away."*
4. **Prompting tips** (junior-designer framing above).
5. **References and the asset library** — *"a picture is worth a 1,000 words as
   they say. So adding references is always super helpful."* You can reference
   past ads by name, not just by uploading.
6. **Iteration by selecting assets in the chat** — live demo.
7. **Resizing** — safe zones respected, with honest caveats.
8. **The editor** — for small manual tweaks.
9. **Figma plugin** — two-way.
10. **Close by asking for reactions** and routing feedback to Slack.

## The prompting curriculum, in the order taught

**(a) References beat descriptions.** Highest-leverage input.

**(b) Iterate by reacting in like/dislike language.** Nate's live demo prompt,
which is the model sentence for the whole method:

> "I like these big blocky numbers but the backgrounds seem a bit plain. So
> let's create 10 more iterations that have more interesting backgrounds with
> these blocky numbers."
>
> "Just like iterating with the agent and telling it what you like and what
> you don't like — it can be really helpful."

**(c) Push divergence with visually different references.** Direct fix for
"it keeps giving me the same thing":

> "A lot of these are just like big numbers on a plain background. So if you
> want to push it outside the bounds, like giving it more references that are
> like visually different."

**(d) Explode a winner.**

> "You land on something that you kind of like and you're like this is a cool
> direction — let's make 10 different variants of this, just explode this out
> and it'll just make 10 new ones."

**(e) Scope your context explicitly.** A customer's self-taught lesson
(Chris, DoorDash) worth teaching directly:

> "I didn't give the agent enough context of like, usually we use the copy
> guidelines but like use that as a rough reference, and then specifically use
> the catering go-to-market document that I provided."
>
> "There's a few things that I could have clarified — like, it says in this
> doc that we have concierge but we're not focusing on that for this launch."

Wrong assumption being corrected: attaching a doc ≠ the agent knowing which
parts are current.

**(f) Chain insights into creation.** Copy a report URL into the ad chat:
*"generate 10 ads based off this report... identifying a trend worth riding...
then generate 10 ads that ride on this trend that are on brand."*

**(g) Two prompting modes are both valid.**

> "If you leave it to a high level prompt, the system will use its reasoning
> to try to figure it out and come up with ideas and flesh out your prompt
> more. But you can also use it sort of like you would use Higgsfield with
> like a very specific prompt."

**(h) When in doubt, try it.** *"I would always recommend trying it."* /
*"Just prompt it."* Using Claude to help write prompts is explicitly endorsed:
*"we definitely have a lot of people using Claude to help them write prompts."*

## Right tool for the size of the edit

> "If it's something bigger, like I hate this imagery... you can just tell it
> like create a new ad with new imagery. If it's not something minor that you
> want to tweak with the edit tool."
>
> "If you want to just literally change one piece of copy or move the logo up
> a little bit, it's probably much faster to just do it in the editor than
> asking."

Version history is the safety net: *"if you accidentally make an edit that you
didn't like, you can always revert."* Figma is for final polish:
*"exporting back into Hightouch from Figma is more useful when it's like,
okay, I'm finalizing these 10 ads."*

## The #1 novice failure mode: invisible behavior read as a bug

Jenne (Chime ACD/copywriter, 2 days in, self-described "not a prompting
expert") on decomposing:

> "It generated a bunch of ads and I was like these look cool... one had like
> bubble type and another is like a neon sign... And then before my eyes, it
> literally updated everything again and moved all of the cool type treatment,
> made it all editable... And then I tried to prompt it to do it again. And it
> got really confused and made it look really weird."
>
> "At one point it generated them in balloons. And I was like that looks
> awesome. And then it took away the balloons and made it sad."

The explanation that fixes it (must come *before* first generation):

> "It goes from a flat image, which is like the early generation of the idea
> of the ad, and then it decomposes it into editable text for you so that all
> the layers are then editable... the font that it chooses, it's not an actual
> font... it's guessing because it's generating a flat image, and then to turn
> that into the actual approved font it goes and changes it. So it looks a
> little different sometimes."

**Second failure mode: over-templating.** Jenne built a prompt template with
Claude and *"felt like it was just kind of spitting out basically the same
thing."* The fix is not a more prescriptive template — it's diverse references
plus reactive iteration.

## Other real customer confusions (use as FAQ seeds)

- "What's the difference between style and auto though?"
- "Can you say ignore the context rules? Is there a way to work around it?"
  (Answer: `no style` keeps global fonts/colors/logos but drops styles.)
- "Can you be that precise about how you want the end file to be generated?"
  — expecting Photoshop-grade layer control. Honest answer: *"it generally
  won't separate layers of art unless they're really distinct."*
- Didn't know brand context existed at all (Katie, Lume): *"do you have any
  place for like brand context or style guide or something? Cause it's just
  continuing to use color schemes that are like a no-go for us."*
- Didn't know statics could be animated (Chris): *"I did not know that was an
  option. So that unlocks a lot."*
- Product accuracy: *"it's probably batting like 60 percent accuracy on the
  product itself"*; *"the package looks good, but then the cap's the wrong
  color."* Root-caused to input quality (blurry catalog images, flat vector
  art), not the model.
- Fear of generic output (Erica, Chime): *"we don't want things to look too
  generic cause that is kind of the problem. We're not prompting it enough. It
  feels just sort of a little flat... you do need to have the prompt do some
  heavy lifting."*
- Momentum loss from slowness: *"it takes a long time to get the output... I
  accidentally got off the screen... I just lost my momentum."* Honest
  expectation set: 10 ads ≈ 10–15 minutes, because product images get a second
  quality pass.
- Focus risk, self-diagnosed: *"the fear is you kind of just go wild in this
  tool, just making cool stuff. But like you don't test it."*

## Aha moments (what makes value click)

- The writer who can finally make visuals: *"as the writer, I can finally
  make all my cool visual ideas come to life."*
- Learning the reactive-iteration grammar in real time — after one demo, Jenne
  extends it herself: *"we could be like more interesting textures on the
  numbers... different colors."*
- Team hand-off: creative sets direction, marketing swaps copy on the same
  link. Prompted the question *"Can you have it do lorem ipsum work?"* →
  *"Yeah, totally. Just prompt it."*
- Consolidation of a multi-tool workflow: *"to have like a one shop tool is
  pretty cool"* / *"things always get lost in translation when you're using
  multiple different tools."*
- The one-click riff: *"I just pressed to riff off of a competitor report... I
  was like, I wonder what happens if I do this? It worked really well."*
- Motion unlocking a real bottleneck (a year of unchanged CTV creative).

## Teaching principles worth copying into the portal

1. **Calibrate before teaching** — ask experience level, then pitch.
2. **Explain the layers of context before any prompting.**
3. **Root-cause quality problems to inputs the user owns**, not the model.
4. **Be radically honest about weaknesses** (resize needs tweaks, UGC is beta,
   generation is slow and here's why). It builds trust and pre-empts the "it's
   broken" reaction.
5. **Teach inside the user's own workspace**, never generic demo data. Kelly
   pre-generates ads in the customer's workspace before the call.
6. **Pre-empt invisible behaviors** (decomposing above all).
