"""Runs M1-M4 once, assembles models.json, the per-project ml blocks, extra flags and the model card."""
import os
from datetime import datetime, timezone

import sklearn

from findings.features import pair_frame
from findings.models import m1_slip, m2_progress, m3_drivers, m4_anomaly, model_card
from findings.panel import latest, pairs_present, series

CONTRACT_VERSION = "1.0.0"


def run(panel, flags, sectors):
    pair_list = pairs_present(panel)
    frames = {pid: pair_frame(panel, a, b, flags) for pid, a, b in pair_list}
    test_pair = pair_list[-1][0]
    m1, p1, pairs_meta = m1_slip.run(panel, flags, frames, pair_list, test_pair=test_pair)
    m2, p2 = m2_progress.run(panel, flags, frames, pair_list, test_pair=test_pair)
    m3, p3 = m3_drivers.run(panel, flags)
    m4, p4, extra = m4_anomaly.run(panel)
    last = latest(panel)
    ml = {}
    for code, rs in series(panel).items():
        if rs[-1]["snapshot"] != last:
            continue
        a, b, c, d = p1.get(code, {}), p2.get(code, {}), p3.get(code, {}), p4.get(code, {})
        ml[code] = {"slip_prob": a.get("slip_prob"), "slip_rank": a.get("slip_rank"), "slip_top_factors": a.get("slip_top_factors", []),
                    "progress_next_pred": b.get("progress_next_pred"), "expected_completion": b.get("expected_completion"),
                    "expected_delay_months": b.get("expected_delay_months"),
                    "peer_expected_cost_overrun_pct": c.get("peer_expected_cost_overrun_pct"), "cost_overrun_residual_pct": c.get("cost_overrun_residual_pct"),
                    "peer_expected_time_overrun_months": c.get("peer_expected_time_overrun_months"), "time_overrun_residual_months": c.get("time_overrun_residual_months"),
                    "anomaly_score": d.get("anomaly_score"), "anomaly_flag": bool(d.get("anomaly_flag", False)), "scored_at_snapshot": last}
    generated = os.environ.get("AGRIM_GENERATED_AT") or datetime.now(timezone.utc).isoformat(timespec="seconds")
    models = {"meta": {"contract_version": CONTRACT_VERSION, "generated_at": generated,
                       "sklearn_version": sklearn.__version__, "random_state": 0, "omp_threads": int(os.environ.get("OMP_NUM_THREADS", "1")),
                       "pairs": pairs_meta, "test_pair": test_pair, "train_pairs": [pid for pid, _, _ in pair_list[:-1]]},
              "m1_slip": m1, "m2_progress": m2, "m3_drivers": m3, "m4_anomaly": m4}
    return models, ml, extra, model_card.build(models, panel)
