from findings.field_audit import whipple_band, whipple_index


def test_uniform_terminal_digits_score_one_hundred():
    assert whipple_index({d: 100 for d in range(10)}) == 100.0


def test_every_value_on_zero_or_five_scores_five_hundred():
    assert whipple_index({0: 500, 5: 500}) == 500.0


def test_no_observations_returns_none():
    assert whipple_index({}) is None
    assert whipple_index({d: 0 for d in range(10)}) is None


def test_bands_follow_the_un_thresholds():
    assert whipple_band(102.0) == "very accurate"
    assert whipple_band(107.0) == "relatively accurate"
    assert whipple_band(120.0) == "approximate"
    assert whipple_band(150.0) == "rough"
    assert whipple_band(200.0) == "very rough"
    assert whipple_band(None) is None
