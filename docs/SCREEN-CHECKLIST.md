# Screen checklist

Tasks 1-17 had `tools/validate.py` and `pytest -q` deciding whether output was correct.
The screens had no arbiter, and came out as six identical cards per page. This is the
arbiter. A screen task is not done until every route's screenshot has been checked
against all six conditions and the screenshots are attached to the task.

Run `python tools/routes.py`, open each URL at 1440x900, screenshot, then check:

1. **No number wraps.** No figure breaks across lines. `₹ 37,10,641.55 cr` fits one line.
2. **No dead column.** No table column shows the same value in every visible row.
3. **Colour means severity.** critical/high/medium/ok are used only for severity.
   No colour is decorative. A falling trend is never drawn in the `ok` green.
4. **Model numbers are marked.** Every model-derived figure is in `#5B4B9A` and the
   word "model" appears beside it.
5. **One focal point.** The screen has a single thing the eye lands on first. Not six
   equal cards.
6. **Provenance.** Every displayed figure either traces to a page citation or is
   explicitly labelled model-derived.

Wording: the headline word is **contradictions**, never "impossibilities".
