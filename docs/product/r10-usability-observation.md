# R-10 usability observation script

## Purpose

Evaluate the R-10 hypothesis in the GrowthTwin service blueprint: one campaign
and permission model can serve both first-time advertisers and experienced
advertisers when advanced details appear progressively. This script is for
moderated observation of the local synthetic prototype. It is a research
instrument, not evidence that the design has passed usability validation.

## Session setup

- Use the authenticated local workspace and the fixed synthetic Ankara home
  maintenance campaign. Do not enter real business, customer, account, lead,
  payment, or personal information.
- Use the same campaign screen and starting state for every participant. Reset
  only the disposable synthetic fixture between sessions if a participant
  changes it.
- Record participant type (new to paid ads / experienced advertiser), viewport,
  task completion, time, wrong turns, help requested, and the participant's
  own explanation. Do not record names or identifying details.
- Ask permission before recording audio or video. Notes without identifiers are
  sufficient.
- Read the task verbatim. Do not explain labels or point to controls. If the
  participant is stuck, wait, then ask only: “What would you expect to happen
  next?” Record help separately from independent completion.

## Opening script

“We are evaluating this prototype, not you. Please think aloud as you use it.
The campaign and business shown are fictional. Nothing here is published, no
advertising account is connected, and no money is spent. You may stop at any
time. I may stay quiet while you work.”

## Tasks for a first-time advertiser

1. **Understand the draft.** “In your own words, what is this campaign trying
   to do, where is it aimed, and has it gone live?”
2. **Understand the limit and dates.** “What is the maximum media amount for
   this example, and what period does it cover? Is that amount GrowthTwin's
   service fee?”
3. **Find uncertainty.** “Can this screen tell you how many people will see or
   click the ad? What does it say when it cannot?”
4. **Find the next step.** “What would you look at or change before deciding
   whether this draft is ready?”

## Tasks for an experienced advertiser

1. **Inspect creative controls.** “Find the source/version and any relevant
   character-limit details for a proposed ad text. Tell me what you learn.”
2. **Inspect planning assumptions.** “Find the channel suitability context,
   destination, total media cap, dates, and daily-average assumption. Which of
   these are estimates versus actual platform controls?”
3. **Inspect evidence gaps.** “Determine whether a real reach, click, cost, or
   conversion forecast is available, and explain why.”
4. **Assess operational readiness.** “Find what is still needed before a real
   campaign could be published. Does this screen grant legal approval or
   connect an ad account?”

## Post-task questions

- “What, if anything, was hard to find or interpret?”
- “Was any statement confusing, overly technical, or more certain than the
  evidence supports?”
- “What would you want to see before taking the next step?”
- For experienced advertisers: “Which detail would you need for professional
  review that was missing or took too long to find?”

## Scoring

For each task record:

| Measure | Record |
| --- | --- |
| Independent completion | Yes / no; no moderator hint was given |
| Correct understanding | Correct / partly correct / incorrect, with a short anonymized note |
| Time | Seconds from task readout to answer |
| Effort | Wrong turns and number of interactions |
| Assistance | None / neutral prompt / direct hint |
| Confidence | Participant's own high / medium / low rating |

Do not combine “partly correct” with success. A participant passes only when
they independently give the required correct explanation.

## Acceptance criteria

- Every first-time advertiser independently identifies the campaign goal, the
  total media cap, the planned period, and that the draft is unpublished.
- Every first-time advertiser distinguishes the media cap from GrowthTwin's
  service fee and understands that the prototype does not provide a real
  performance forecast.
- Every experienced advertiser finds the creative source/version,
  character-limit context, channel suitability caveat, and missing forecast
  evidence within two intentional disclosure/navigation interactions per
  detail.
- No participant interprets the synthetic suitability label as legal
  clearance, the daily average as a platform-enforced cap, or the draft as a
  real result, guarantee, publication, or spend.
- Report results by participant type and task, including failures and
  ambiguity. Do not claim validation until observations from both participant
  types have been completed and reviewed.

## Current execution status

The local campaign screen was opened and visually reviewed on 2026-10-15. At
the captured viewport, the top-level status clearly says “Önizleme ·
yayınlanmadı”; the suitability caveat and plan summary follow beneath it. The
accessibility tree exposes collapsed controls for source/date, text details,
forecast search terms, and launch readiness. This was a product-owner review,
not a participant session; no usability outcome is claimed. Participant
recruitment and observation remain to be scheduled.
