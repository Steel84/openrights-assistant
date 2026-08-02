# Demo

A 60 second recording for the grant application. Shot on a real phone, in
airplane mode, because that is the whole claim.

## Before recording

1. Open https://openrights.fortravels.xyz/ **with internet on**.
2. Wait for the status to read **"Ready · saved for offline"**. If it says
   "online only", the archive is not cached and airplane mode will fail.
3. Install it: browser menu, "Add to Home screen".
4. **Turn on airplane mode.** Check the icon is visible in the status bar.
5. Open the app from the home screen, not from the browser.
6. Start the screen recorder. Portrait, clean home screen.

## Questions to ask on camera

These are covered by plain-language answers, so each returns a real answer
rather than statute text. Verified by `python -m openrights coverage`.

**Use these three.** Different laws, obviously real problems, short answers
that fit on one screen:

1. **What is the federal minimum wage?**
   Answers with $7.25 and the state-minimum rule. Instant, unambiguous, and
   the viewer can check it themselves.

2. **Can a debt collector call me at work?**
   Answers with the 8am-9pm rule and the workplace restriction. This is the
   one that lands: a real problem, a specific answer.

3. **Can I be fired without a reason?**
   At-will employment, and the illegal exceptions. Shows the tool handling a
   question with a genuinely nuanced answer.

Good alternatives if one falls flat: *Do part-time workers have the same rights
as full-time workers?* · *Can I refuse dangerous work?* · *Am I entitled to a
lunch break?* · *How much family and medical leave can I take?*

**Do not ask on camera:** housing, eviction, credit reports, unemployment
benefits, immigration, small claims. No plain-language answer covers those yet,
so the app correctly says so and shows statute text instead. Honest, but not
what you want in a 60 second demo. `docs/COVERAGE.md` has the full gap list.

## Sequence

| Time | Show | Say |
| --- | --- | --- |
| 0:00 | Home screen, airplane mode icon | "This phone has no connection." |
| 0:05 | Tap the app icon | "Everything runs on the device." |
| 0:10 | Type question 1, tap Search | "Ask in plain English." |
| 0:20 | The answer card | "A direct answer, not a search result." |
| 0:28 | Expand supporting passages | "And the law it comes from, so you can check it." |
| 0:35 | Question 2 | "Debt collection, workplace safety, discrimination." |
| 0:45 | Question 3 | |
| 0:52 | Pull down the notification shade | "Still offline. Nothing left the phone." |

## Worth saying out loud

- Under 2 MB. Runs on a phone nobody would call new.
- No account, no permissions, no network calls after install.
- Every answer names the statute and links to it.
- 8 official sources, 46 plain-language answers, checked on every commit.

## Tips

- Record the voiceover separately. Phone mics are bad.
- 1080p, portrait, no personal widgets on the home screen.
- 60 to 90 seconds. Reviewers watch a lot of these.
