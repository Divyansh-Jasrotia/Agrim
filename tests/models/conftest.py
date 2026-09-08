import pytest

from contracts.fixtures.synthetic_panel import write
from findings.panel import load_panel


@pytest.fixture(scope="session")
def synth_path(tmp_path_factory):
    return write(tmp_path_factory.mktemp("synth") / "panel.csv", n_projects=900, seed=0)


@pytest.fixture(scope="session")
def synth(synth_path):
    return load_panel(synth_path)
