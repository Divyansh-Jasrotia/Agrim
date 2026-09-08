# Human steps remaining for Task 20

Everything an AI agent could do for the deck and pitch is done and committed:
`tools/slides.py`, `deck/slides.md` (generated, all six slides, every number
traced to `deck/numbers.json`), and `deck/pitch.md` (script with timings,
numbers as `{key}` placeholders read aloud from `deck/slides.md`).

Two steps from the plan need a human and are not done. Do them in this order.

## Step 3 — Fill the official template by hand

Needs: the competition's own `.pptx` template, PowerPoint (or an editor that
preserves its layout), and a human's design judgement.

1. Download the template: https://www.sih.gov.in/letters/2026/SIH2026-IDEA-Presentation-Format.pptx
   Save it as `deck/AGRIM-SIH26103.pptx`.
2. For each of slides 1–6, copy the matching block of bullets from
   `deck/slides.md` into the template's existing text boxes. Do not change the
   template's headings or its pointer/instruction text — only fill the content
   areas. All numbers in `deck/slides.md` are already substituted from
   `deck/numbers.json`; copy them as printed, don't retype them by hand.
3. Delete the template's slide 7 ("IMPORTANT INSTRUCTIONS"). The deck must end
   at six slides.
4. On slide 3 (Technical Approach), draw the pipeline as boxes and arrows
   using the flow bullet in `deck/slides.md` Slide 3 as the sequence: PAIMANA
   PDFs → pinned fetch + checksums → adapter parser → canonical panel →
   findings engine (F1–F6) → feature builder → models M1–M4 → LLM briefs with
   grounding check → JSON bundle → dashboard.
5. On slide 4 (Feasibility and Viability), add one screenshot of the
   Contradiction Ledger and one of the model-vs-baseline comparison table from
   the Predict screen — not a gallery of every screen. Take both from the
   running demo (`RUN_DEMO.bat`, described below) so they match the committed
   data.
6. Export the finished deck as PDF to `deck/AGRIM-SIH26103.pdf`.

## Step 5 — Rehearse on a cold machine

Needs: a second physical laptop, separate from the one used for development.

1. On that second laptop: `git clone <this repo> C:\dev\agrim` — clone only,
   do not run `npm install` and do not install any Python packages.
2. Turn Wi-Fi off.
3. Run `RUN_DEMO.bat` from the repo root. It serves the already-committed
   `web/dist` (built by `npm run build` in this task) on `localhost:8080` and
   opens it — this must work with no network and no toolchain installed,
   because `web/dist` and `web/public/data` are committed, not generated at
   demo time.
4. Walk the demo path in `deck/pitch.md` (`#/ledger?type=EXP_DECREASE` →
   `#/project/{opener_code}` → source page → `#/predict` → `#/exits` →
   `#/assistant` question 8) while reading the pitch script aloud, substituting
   each `{key}` placeholder with the number printed for that key in
   `deck/slides.md`, spoken in words.
5. Time the full pitch three times with a stopwatch.
6. Append one line to the bottom of `deck/pitch.md`:
   `Rehearsal: <date> <m:ss>, <m:ss>, <m:ss>`
   These are the only literal numbers allowed in that file, and each must
   stay under two digits (minutes and seconds), so `tools/validate.py`'s
   hardcoded-number check on `deck/pitch.md` still passes. Re-run
   `python tools/validate.py` after adding the line to confirm.
7. Commit `deck/AGRIM-SIH26103.pptx`, `deck/AGRIM-SIH26103.pdf`, and the
   updated `deck/pitch.md` together, message style `task 20: <what>`.

## Where things live

- Generated slide text: `deck/slides.md` (run `python tools/slides.py` again
  any time `deck/numbers.json` changes — it overwrites the file).
- Pitch script: `deck/pitch.md`.
- Numbers used everywhere above: `deck/numbers.json` (44 keys, all traceable
  — this is what `tools/validate.py` checks).
- Demo entry point: `RUN_DEMO.bat` at the repo root, serving `web/dist`.
- Model Card screen already discloses the map's pre-2019 state boundaries
  (Jammu & Kashmir undivided, no separate Ladakh polygon) — do not describe
  the map as using current boundaries anywhere in the filled deck or in
  spoken Q&A.
