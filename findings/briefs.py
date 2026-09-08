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
            lines.append(f"Model: cost overrun {_n(ml['cost_overrun_residual_pct'])} percentage points above comparable projects.")
    return "\n".join(lines)


def grounded(brief, facts):
    return numbers_in(brief) <= numbers_in(facts)


def template_brief(p):
    last = p["snapshots"][-1]
    first = p["flags"][0]["detail"] if p["flags"] else "No contradictions were found in its record."
    return (f"{p['project_name']} ({p['project_code']}) is monitored under {p['agency_raw'] or 'an unnamed agency'} in {p['state'] or 'an unstated location'}. "
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
        return {"project_code": p["project_code"], "brief": template_brief(p), "model": "template", "seed": SEED,
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "grounded": True, "attempts": 0, "facts_hash": h}
    prompt = f"{SYSTEM}\n\nFACTS:\n{facts}\n\nBRIEF:"
    attempts, text = 0, ""
    for attempts in range(1, 4):
        text = _ollama_generate(model, prompt)
        if text and grounded(text, facts):
            return {"project_code": p["project_code"], "brief": text, "model": model, "seed": SEED,
                    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "grounded": True, "attempts": attempts, "facts_hash": h}
        bad = sorted(numbers_in(text) - numbers_in(facts))
        prompt = f"{SYSTEM}\n\nFACTS:\n{facts}\n\nYour previous brief contained numbers not in the facts: {', '.join(bad)}. Remove them and write the brief again.\n\nBRIEF:"
    return {"project_code": p["project_code"], "brief": template_brief(p), "model": model, "seed": SEED,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "grounded": False, "attempts": attempts, "facts_hash": h}


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
