import json
from pathlib import Path

import pytest

from tools.slides import render

NUMS = Path("deck/numbers.json")


@pytest.mark.skipif(not NUMS.exists(), reason="deck/numbers.json not generated")
def test_slides_render_all_six_and_use_only_known_numbers():
    nums = json.loads(NUMS.read_text(encoding="utf-8"))
    text = render(nums)
    for heading in ["TITLE PAGE", "IDEA TITLE", "TECHNICAL APPROACH", "FEASIBILITY AND VIABILITY", "IMPACT AND BENEFITS", "RESEARCH AND REFERENCES"]:
        assert heading in text
    assert "{" not in text and "}" not in text            # every placeholder substituted
    assert str(nums["projects_latest"]) in text
