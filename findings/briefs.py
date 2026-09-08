"""LLM project briefs, generated ONCE at build time from a fact sheet, verified number-by-number, cached to briefs.json.
Usage: python -m findings.briefs [--top 60] [--codes 705526,612793] [--model qwen2.5:3b] [--template-only]"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "web" / "public" / "data"
SEED = 0
NUM = re.compile(r"\d[\d,]*\.?\d*")
SYSTEM = ("You write a four-sentence brief for a government infrastructure monitoring officer. Use only the facts below. "
          "Do not introduce any number that is not in the facts. Plain English, no headings, no bullet points.")


def numbers_in(text):
    out = set()
    for m in NUM.findall(text or ""):
        t = m.replace(",", "").rstrip(".")
        if t:
            out.add(t.rstrip("0").rstrip(".") if "." in t else t)
    return out


def _n(x):
    return "—" if x is None else (f"{x:,.2f}" if isinstance(x, float) else str(x))


def fact_sheet(p):
    lines = [f"Project {p['project_code']}: {p['project_name']}; agency {p['agency_raw'] or 'not printed'}; state {p['state'] or 'not printed'}; sector {p['sector'] or 'unknown'}.",
             f"Seen from {p['first_seen']} to {p['last_seen']}; status {p['status']}."]
    for s in p["snapshots"]:
        lines.append(f"Report {s['snapshot']} (page {s['page']}): progress {_n(s['physical_progress_pct'])}%, cumulative expenditure {_n(s['expenditure_cum_cr'])} crore, "
                     f"original cost {_n(s['cost_original_cr'])} crore, revised cost {_n(s['cost_revised_cr'])} crore, original completion {s['doc_original'] or 'not printed'}, revised completion {s['doc_revised'] or 'none'}.")
    for f in p["flags"]:
        lines.append(f"Flag ({f['severity']}): {f['detail']}")
    lines.append(f"Rule-based risk score {p['risk']['score']} ({p['risk']['band']}).")
    ml = p.get("ml")
    if ml:
        if ml.get("slip_prob") is not None:
            lines.append(f"Model: probability of a revised completion date being filed next report {round(100 * ml['slip_prob'])} percent, rank {ml['slip_rank']}.")
        if ml.get("expected_completion"):
            lines.append(f"Model: expected completion {ml['expected_completion']}, expected delay {_n(ml['expected_delay_months'])} months versus the stated date.")
        if ml.get("cost_overrun_residual_pct") is not None:
            resid = ml["cost_overrun_residual_pct"]
            direction = "above" if resid >= 0 else "below"
            lines.append(f"Model: cost overrun {_n(abs(resid))} percentage points {direction} comparable projects.")
    return "\n".join(lines)


# Digits that identify the record rather than measure anything about the project (the
# project code, a source-document page number) must not license a numeric claim in a
# brief: a model can otherwise dress an identifier up as a fabricated measurement (e.g.
# quoting the project code as if it were a distance in meters) and still pass the
# subset check below. These patterns match fact_sheet()'s own formatting, so they stay
# correct for any project/page without hardcoding a specific value.
_PROJECT_CODE_RE = re.compile(r"(?<=^Project )\d[\d,]*\.?\d*(?=:)", re.MULTILINE)
_PAGE_RE = re.compile(r"(?<=\(page )\d[\d,]*\.?\d*(?=\))")


# The exclusion must be POSITIONAL, not by value: subtracting identifier VALUES from the
# whole allowed set (the earlier, wrong approach) bans that value everywhere in the fact
# sheet, so a real quantity elsewhere that merely happens to equal an identifier (e.g. a
# progress percentage that equals a page number) gets wrongly rejected too. Instead, mask
# the identifier substrings out of the fact-sheet TEXT first, then compute numbers_in()
# over the masked text -- an identifier occurrence stops licensing a claim only at its own
# position; the same value occurring elsewhere as a genuine quantity still counts.
def _mask_identifiers(facts):
    text = facts or ""
    for rx in (_PROJECT_CODE_RE, _PAGE_RE):
        # Replace with the SAME NUMBER of a non-digit, non-comma, non-period filler
        # character. Same length keeps every other character's position untouched (so
        # nothing before/after the match can be mis-tokenised); a non-numeric filler
        # means numbers_in() can never re-match across the masked span, so it cannot
        # accidentally splice two neighbouring numbers into a new one.
        text = rx.sub(lambda m: "#" * len(m.group(0)), text)
    return text


def grounded(brief, facts):
    return numbers_in(brief) <= numbers_in(_mask_identifiers(facts))


def template_brief(p):
    last = p["snapshots"][-1]
    first = p["flags"][0]["detail"] if p["flags"] else "No contradictions were found in its record."
    # The project code is an identifier, not a fact-sheet quantity (see grounded()); it is
    # not woven into this sentence as a bare number so the template stays grounded by
    # construction under the stricter, identifier-aware check.
    return (f"{p['project_name']} is monitored under {p['agency_raw'] or 'an unnamed agency'} in {p['state'] or 'an unstated location'}. "
            f"In the {last['snapshot']} report it stands at {_n(last['physical_progress_pct'])}% physical progress with cumulative expenditure of {_n(last['expenditure_cum_cr'])} crore against a revised cost of {_n(last['cost_revised_cr'])} crore. "
            f"{first} "
            f"The rule-based risk score is {p['risk']['score']} ({p['risk']['band']}).")


def _ollama_generate(model, prompt):
    import ollama
    r = ollama.generate(model=model, prompt=prompt, options={"seed": SEED, "temperature": 0, "num_ctx": 4096}, stream=False)
    return (r.get("response") or "").strip()


def brief_for(p, model, template_only=False):
    facts = fact_sheet(p)
    h = hashlib.sha256(facts.encode("utf-8")).hexdigest()
    if template_only:
        text = template_brief(p)
        return {"project_code": p["project_code"], "brief": text, "model": "template", "seed": SEED,
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "grounded": grounded(text, facts), "attempts": 0, "facts_hash": h}
    prompt = f"{SYSTEM}\n\nFACTS:\n{facts}\n\nBRIEF:"
    attempts, text = 0, ""
    for attempts in range(1, 4):
        text = _ollama_generate(model, prompt)
        if text and grounded(text, facts):
            return {"project_code": p["project_code"], "brief": text, "model": model, "seed": SEED,
                    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "grounded": True, "attempts": attempts, "facts_hash": h}
        # Feedback must list what the check actually rejected: numbers masked as identifiers
        # (project code, page numbers) are not "in the facts" as far as grounded() is
        # concerned, so this uses the same masked view grounded() itself uses -- otherwise a
        # model that invented an identifier-shaped number would never be told to remove it.
        bad = sorted(numbers_in(text) - numbers_in(_mask_identifiers(facts)))
        prompt = f"{SYSTEM}\n\nFACTS:\n{facts}\n\nYour previous brief contained numbers not in the facts: {', '.join(bad)}. Remove them and write the brief again.\n\nBRIEF:"
    # Ships template_brief(p) text after exhausting all LLM attempts. This must record the
    # REAL grounded() result on that text, exactly like the --template-only branch above --
    # not a hardcoded False. That hardcoding was roughly harmless while template_brief()
    # often failed grounding, but the fix that made template_brief() grounded-by-construction
    # (see test_template_brief_grounded_for_all_real_projects) turned this into a false
    # negative almost every time the branch fires: text that is genuinely grounded, mislabelled
    # as unverified.
    fallback_text = template_brief(p)
    return {"project_code": p["project_code"], "brief": fallback_text, "model": "template", "seed": SEED,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "grounded": grounded(fallback_text, facts), "attempts": attempts, "facts_hash": h}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--codes", default="")
    ap.add_argument("--model", default="qwen2.5:3b")
    ap.add_argument("--template-only", action="store_true")
    a = ap.parse_args(argv)
    projects = json.loads((DATA / "projects.json").read_text(encoding="utf-8"))
    ongoing = sorted((p for p in projects if p["status"] == "ongoing"), key=lambda p: (-p["risk"]["score"], p["project_code"]))
    wanted = [p["project_code"] for p in ongoing[:a.top]] + [c.strip() for c in a.codes.split(",") if c.strip()]
    by = {p["project_code"]: p for p in projects}
    out_path = DATA / "briefs.json"
    existing = {b["project_code"]: b for b in json.loads(out_path.read_text(encoding="utf-8"))} if out_path.exists() else {}
    out = []
    for code in dict.fromkeys(wanted):
        p = by.get(code)
        if not p:
            print("skip unknown code", code)
            continue
        h = hashlib.sha256(fact_sheet(p).encode("utf-8")).hexdigest()
        if code in existing and existing[code]["facts_hash"] == h and existing[code]["grounded"]:
            out.append(existing[code])
            continue
        b = brief_for(p, a.model, a.template_only)
        print(code, "grounded" if b["grounded"] else "TEMPLATE FALLBACK", f"(attempts {b['attempts']})")
        out.append(b)
    out.sort(key=lambda b: b["project_code"])
    out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out_path}: {len(out)} briefs, {sum(b['grounded'] for b in out)} grounded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
