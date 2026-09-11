"""Display-only: merge consecutive same-type flags on the same project into one row.

Never apply this before findings.models.features builds feature set B — that reads the
raw flag list for n_flags_to_t0 and exp_decrease_ever, and collapsing first would change
M1's features and invalidate the frozen metrics.
"""


def collapse(flags):
    groups = {}
    order = []
    for f in flags:
        key = (f["project_code"], f["type"])
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(f)
    out = []
    for key in order:
        members = sorted(groups[key], key=lambda f: f["to_snapshot"])
        head = dict(members[-1])
        head["first_snapshot"] = members[0]["from_snapshot"] or members[0]["to_snapshot"]
        head["occurrences"] = len(members)
        seen, sources = set(), []
        for m in members:
            for s in m["sources"]:
                k = (s["snapshot"], s["page"])
                if k not in seen:
                    seen.add(k)
                    sources.append(s)
        head["sources"] = sorted(sources, key=lambda s: (s["snapshot"], s["page"]))
        out.append(head)
    out.sort(key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    return out
