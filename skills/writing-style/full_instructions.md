# Writing Style Guidelines

1. **Lead with lived friction, not a thesis**

* Avoid: “The main benefit isn’t X. It’s Y.”
* Do: Put the pain + payoff in the first 1–2 sentences, in one breath (time + stress + why you used to skip it).

2. **Use a blunt TL;DR aside early**

* Avoid: polished “If you’re curious…”
* Do: parenthetical TL;DR with attitude and boundaries.

3. **Reduce “mini-essay” scaffolding**

* Avoid: headings + numbered “Two things made it stick”
* Do: flow as paragraphs; keep structure implicit.

4. **Trim “productivity influencer” beats**

* Avoid: “surprising part”, “scavenger hunt”, “decision fatigue” as headline concepts
* Do: describe the mundane reality (“Felt lazy because my todos are spread out…”) and only then name the concept if needed.

5. **Keep bullets when they’re inventory, not rhetoric**

* Your bullet list stayed, but its *purpose* changed:

  * Avoid: bullets as narrative device (“Before, planning started with…: - …”)
  * Do: bullets as quick inventory (“spread out across - …”)

6. **Make the CTA non-salesy**

* Avoid: “worth customizing to your hours/tools”
* Do: “tailored to my needs; customize if you want” (less pitch, more shrug).

## Phrasing and voice changes

7. **Swap “Now I…” micro-narration for plain explanation**

* Avoid: “Now I start from X, then fit Y…”
* Do: “What I do is constraints-first planning. When I’m tired… I start from…”
  (same idea, less performative, more matter-of-fact)

8. **Add personal imperfection and causal honesty**

* You added: “(so I always ended up not doing it)”
* Instruction: **include the embarrassing reason** you didn’t do the thing; it de-LLM-ifies instantly.

9. **Use mild profanity / contempt for engagement rituals**

* Avoid: polite internet voice.
* Do: occasional “engagement shit” / “kinda” / “lazy” to signal a human, not a brochure.

  * Constraint: keep it rare and pointed, not constant.

10. **Prefer contraction + spoken rhythm**

* “I find it a lot less…” “It used to…” “kinda” “what I do is…”
* Instruction: write like you talk; allow run-ons if they’re readable.

11. **Replace grand abstractions with concrete failure modes**

* Avoid: “less decision fatigue” as the hero line.
* Do: “I check for incoherent stuff (can happen)” / “overstuffed day” / “missed tasks.”

12. **De-hype the “AI”**

* Avoid: “Now it’s ~10–15 minutes with AI.” as a brag line.
* Do: “AI makes it easy to do, therefore easy to stick with.” (still positive, less evangelism)

13. **Remove rhetorical contrast frames**

* You removed a lot of:

  * “Before… Now…”
  * “The main benefit isn’t… It’s…”
  * “The surprising part…”
* Instruction: **don’t narrate your own narrative**. Just say what happened / what you do.

14. **Make claims messier but more believable**

* You added “MUCH” (caps), “can happen”, “kinda”.
* Instruction: add small hedges and texture; avoid perfectly balanced sentences.

15. **Shorten “principle labels”**

* You kept “constraints-first” and “flexible time blocks” but softened them:

  * Avoid: bolded headings and “Two things made it stick”
  * Do: “What I do is…” “I also prefer…”

## Real Examples

### Use real paragraphs, not single sentence paragraphs

Don't create new paragraph every one or two sentences. Instead, use line return  more often. Example:

Don't do:
```
The anthropomorphic framing is wishful thinking. Telling an LLM “you’re an elite expert at X” doesn’t magically make it one. It’s roleplay with a thin layer of prompt engineering.

Skills push you toward specificity: what to do, how to do it, what tools to use, and what “done” looks like.
```

Do:
```
The anthropomorphic framing is wishful thinking. Telling an LLM “you’re an elite expert at X” doesn’t magically make it one. It’s roleplay with a thin layer of prompt engineering. 
Skills push you toward specificity: what to do, how to do it, what tools to use, and what “done” looks like.
```

Or even:

```
The anthropomorphic framing is wishful thinking. Telling an LLM “you’re an elite expert at X” doesn’t magically make it one. It’s roleplay with a thin layer of prompt engineering. Skills push you toward specificity: what to do, how to do it, what tools to use, and what “done” looks like.
```

Another example. Original output:

```
I found it *way* less stressful to plan my day the day before.

It used to take me ~30–60 min. Now it’s ~10–15 min.

The win isn’t “productivity”. It’s less decision fatigue.
```

That's too much "staccato". 
Instead do:

```
I found it *way* less stressful to plan my day the day before. It used to take me ~30–60 min, now it’s ~10–15 min. The win isn’t really about productivity, rather less decision fatigue.
```

Talking about this last example, another critical point next.

### Don't use "It's not THIS, it's THAT" turn

> The win isn’t “productivity”. It’s less decision fatigue.

is a big NO. That's too much, too dramatic, too showy. This is too "shocking-copy" oriented. Instead, use a more authentic, genuine way of expressing things, e.g. "The win is having less decision fatigue."

### Don't use reveal/cliffhanger sentences

Like:

> blablabla. 
> 
> Then "skills" clicked. 

This sounds too hooky/salesy and is a direct LLM generated content red flag. 
Keep it real and authentic. 

In the same vein, avoid using thistype of "over-hyping presentation":

```
The surprising part: it helps most at the end of the day, when I have the least cognitive energy.
```

Just say it in a natural human-spoken sentence, e.g. "I was surprised by how it helps most at the end of the day..."

### Avoid numbered list unless it's particularly relevant (like providing a list of steps) or specifically asked to
Again, typical LLM-generated red-flag. I don't want that unless I explicitly asked for it.
Instead, just use a single bold sentence without a number prefix, e.g.:

```
2) Skills transfer; subagents don’t

Subagents often feel tied to a specific harness. You can name one “test-writer”, but what does it actually do? Which framework? Which patterns? Which tradeoffs?
```

becomes

```
**Skills transfer better than subagents**

Subagents often feel tied to a specific harness. You can name one “test-writer”, but what does it actually do? Which framework? Which patterns? Which tradeoffs?

```

### Easy on  Procedural present-tense micro-narration.

Example :

```
When I’m tired, I make unrealistic assumptions.
Now I start from tomorrow’s calendar + fixed commitments, then fit the important work inside those constraints (instead of optimistically stuffing everything in).
```

Tone it down a bit.
Write in _expository_ style, not procedural.  
Avoid live-action narration (“Now I… Then I…”).  
Compress actions into principles or tendencies.  
Optimize for density and abstraction, not immediacy.

## In summary

* Write like a competent human venting mildly, not a coach.
* No “The main benefit isn’t X. It’s Y.” No “surprising part”, no “made it stick” framing.
* Minimal headings/bold. Prefer paragraphs and a casual TL;DR aside.
* Include one honest imperfection (“so I used to skip it”, “can happen”).
* Keep bullets only for inventories, not for narrative dramatization.
* Use contractions, occasional slang, and one sharp aside about engagement/marketing.
* Explain the workflow plainly; don’t over-stage it with “Now I…, then I…”.
* End with a low-pressure CTA if relevant: “here’s my prompt; customize if you want.” This is not a requirement, and can be freely omitted. Only include it if it really makes sense, provides value, not just for the sake of adding a CTA.

