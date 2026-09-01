import os
import subprocess
import sys

import pytest


@pytest.mark.skipif(os.environ.get("AGRIM_IN_VALIDATE") == "1", reason="validate.py runs pytest itself; do not recurse")
def test_validator_exits_zero_on_clean_repo():
    p = subprocess.run([sys.executable, "tools/validate.py"], capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "FAIL" not in p.stdout
