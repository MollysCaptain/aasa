# Build Guide — PM, Ethics & Pitch: Week 3

*Companion to the kanban board's cards P.10–P.13. This is the week the whole project either proves or fails to prove its core hypothesis — treat these cards as the most important checkpoints in the plan, not paperwork around the "real" work.*

---

## Card P.10 — End-to-end smoke test & integration fixes

**Depends on:** Card P.9 · **Owner:** Joint · **Day:** 17 (Week 3)

### Goal in plain language
A **smoke test** is a fast, manual pass through the app's main paths, checking that nothing is obviously broken — named after the old hardware-testing habit of turning a device on and checking it doesn't literally start smoking. You're not looking for subtle bugs here, just "does this work at all end to end, now that the real UI is wired to the real backend."

### Step-by-step

1. **Write down 6–8 scenarios to click through**, covering the happy path and a few edge cases. Use the list below as a starting point, adjusted to your actual fields:

```markdown
## Smoke Test Checklist — Day 17

- [ ] Submit a normal, complete form → see all 3 blocks render with real data (not placeholders).
- [ ] Submit with the budget field empty/zero → see a clear validation error, no crash.
- [ ] Submit with "Regulated" privacy → confirm no consumer-only tool appears in Block A.
- [ ] Submit with "Standard" privacy → confirm the stack differs from the regulated run above.
- [ ] Submit a workflow/industry combination likely to have very few matches → confirm the "no tools cleared" / graceful-empty message shows, not a crash.
- [ ] Click the export/copy control → confirm the copied text actually contains real tool names and the real cost figures shown on screen.
- [ ] Submit the trust survey → confirm a new line appears in `data/telemetry.log`.
- [ ] Reload the page fresh → confirm the form resets cleanly (no leftover state causing confusing behaviour).
```

2. **Run through the checklist together**, one of you driving the keyboard, the other reading the checklist and writing down anything unexpected.
3. **Fix bugs found, in order of how badly they'd embarrass you in front of a real tester** — a crash beats a slightly-off evidence-bar percentage for priority.
4. **Re-run the specific checklist item you just fixed** before moving to the next bug — this catches the common mistake of "fixing" one thing while quietly breaking another.

### How to verify this card is done
- Every item in your smoke-test checklist is checked off with no known crashes remaining.
- Any item you deliberately chose *not* to fix is written down as a known issue with a reason (e.g., "cosmetic only, deferred to Week 4 polish"), not silently dropped.

---

## Card P.11 — Real user testing (5–8 testers)

**Depends on:** Card P.10 · **Owner:** Joint · **Day:** 20 (Week 3)

### Goal in plain language
This is the actual test of your core hypothesis: *"founders will trust an automated recommendation if it's grounded in real deployments and paired with an honest cost estimate."* Everything before this day was preparation for this one day's data.

### Step-by-step

**Before the sessions:**
1. Confirm your P.2 tracker shows 5–8 people scheduled across today and (if needed) tomorrow.
2. Decide roles: one of you moderates (talks to the tester), the other takes notes silently — swap roles partway through if you want both of you to get moderating practice, but don't do both jobs solo; you'll miss things.
3. Set up whatever video tool you'll use (Zoom, Google Meet — anything with screen share).
4. Have the app running locally and ready (`streamlit run app/intake.py`), and have `data/telemetry.log` and the trust-survey code (Card 3.4) already working — you want real telemetry captured *during* these sessions, not reconstructed afterward.

**Session script (repeat for each tester, ~15–20 minutes):**

```markdown
1. Intro (1 min): "Thanks for your time. This is a working prototype from a
   bootcamp capstone — nothing you enter is stored with your name, and there's
   no account. I'll ask you to try it and think out loud, then answer a couple
   of quick questions at the end."

2. Task (8-10 min): "Imagine you're deciding what AI tool to use for [a
   workflow relevant to them, or let them pick]. Go ahead and fill out the
   form and generate a blueprint — feel free to say out loud whatever you're
   thinking."
   [Moderator: resist the urge to explain or defend the product. Let confusion happen and note it.]

3. Built-in trust survey (2 min): let them actually fill out the in-app 1-5
   trust slider and Yes/No net-value question themselves — this is real data,
   don't ask them verbally and transcribe it, let the telemetry capture it.

4. A couple of open questions (3-5 min):
   - "What's the one thing that would make you trust this more?"
   - "Would you have found this faster or slower than your usual way of researching this?"
```

**During each session:** the note-taker writes down direct quotes where possible, not paraphrases — "I don't know what 'seat-priced' means" is more useful later than "was confused by pricing terms."

**After each session:** log it in your P.2 tracker as `completed`.

### How to verify this card is done
- `data/telemetry.log` has real `survey_submitted` entries with actual `trust_score` values from real people, not test data.
- You have written notes (quotes, not just impressions) from all 5–8 sessions.
- You've watched every single session live — don't skip any and rely on the log data alone; the qualitative "why" behind a low trust score only comes from watching it happen.

---

## Card P.12 — Patch bugs/prompts/rules from testing

**Depends on:** Card P.11 · **Owner:** Joint · **Day:** 21 (Week 3)

### Goal in plain language
You now have real signal from real people. This card is the disciplined, timeboxed loop of turning that signal into fixes — before it's forgotten and before Week 4's packaging work crowds it out.

### Step-by-step

1. **Pool every issue from all sessions into one list**, each with how many testers hit it (a bug 4/8 people hit is a different priority than one 1/8 hit).
2. **Sort into three buckets**:
   - **Blocker** — the app broke or gave a nonsensical/untrustworthy answer.
   - **Major** — caused visible confusion or hurt the trust score.
   - **Minor** — cosmetic, or a one-off preference.
3. **Timebox the fix session to today only.** Fix every Blocker, fix as many Majors as you realistically can, explicitly defer Minors (write them down, don't just forget them — they're good "known limitations / roadmap" material for Card P.16).
4. **Split ownership by type, not evenly by count**: Person A takes backend/logic/prompt issues (e.g., the LLM inventing a tool name — tighten the prompt from Card 2.6), Person B takes UI/copy issues.
5. **Re-test each fix against the specific scenario that surfaced it** — if Tester 3 got confused by the word "Regulated," don't just assume your tooltip fix worked; re-run that exact flow yourself and check the confusion is actually gone.

### How to verify this card is done
- Every Blocker from testing is fixed and re-verified.
- A written list of deferred Minor issues exists — this becomes input to Card P.16.

---

## Card P.13 — Ethics: inclusion & clarity check

**Depends on:** Card P.11 · **Owner:** Person B · **Day:** 21 (Week 3)

### Goal in plain language
Confirm your testing wasn't accidentally narrow — specifically, that it included at least one non-technical founder (not another developer) and one non-native English speaker, and that the product's language holds up for both. A tool that only makes sense to people similar to its own builders isn't actually validated yet.

### Step-by-step

1. **Check your P.2 tracker against these two criteria.** If neither a non-technical tester nor a non-native-English-speaking tester is in your completed list, that's a real gap — try to schedule one more short session today or tomorrow rather than skip this quietly.
2. **Re-read your session notes specifically looking for jargon-confusion moments** — any point where a tester paused on a term like "token," "seat-priced," "vector store," or "regulated." Note every one you find, even if the person eventually figured it out.
3. **Do a plain-language pass**: for every jargon term you found causing hesitation, either replace it with plainer wording in the UI or add a short inline explanation (Streamlit's `help=` parameter on a widget, as already used for the privacy radio button in Card 1.1, is the easiest place to add this).
4. **Write a short, honest note** — if you genuinely couldn't recruit a non-native-English speaker in time, say so plainly rather than implying broader testing than actually happened. This kind of honesty is exactly what this project's ethics workstream is built around (see Handbook §9's "fabrication removal" principle) — the same standard applies to your own testing claims, not just the prototype's UI.

### Template

```markdown
## Week 3 Ethics Checkpoint — Inclusion & Clarity
**Date:** ___________  **Owner:** Person B

- Non-technical founder tested? [Y/N — name/session ref]
- Non-native English speaker tested? [Y/N — name/session ref]
- Jargon-confusion moments found: [list terms + what was changed]
- Honest gaps (if any): [state plainly]
```

### How to verify this card is done
- The checkpoint doc above exists, dated, with real answers — not blank checkboxes.
- At least one concrete wording change in the app traces back to a specific jargon-confusion moment you found.

---

## Week 3 — Done Checklist
- [ ] Smoke-test checklist fully run, no known crashes remain.
- [ ] 5–8 real testing sessions completed, all watched live, notes taken for each.
- [ ] Real telemetry (trust scores, timing) captured in `data/telemetry.log` from actual testers.
- [ ] Every Blocker-severity issue from testing is fixed and re-verified.
- [ ] A dated list of deferred Minor issues exists (feeds Card P.16).
- [ ] Inclusion & clarity checkpoint completed with honest, specific answers.

Continue to `17-Build-Guide-Package-Pitch-Week4-v1.md` next.
