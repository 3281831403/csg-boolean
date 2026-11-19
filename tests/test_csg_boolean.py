import pytest

from geometry import csg_boolean as mod

CASES = [
    ('include_coplanar', [[(0, 1)], [(1, 2), (0, 1)]], [(0, 1), (1, 2)], False),
    ('include_coplanar', [[], [(0, 1)]], [(0, 1)], False),
    ('drop_degenerate', [[[(0, 0), (1, 0), (0, 1)], [(0, 0), (0, 0), (1, 1)]], 1e-09], [[(0, 0), (1, 0), (0, 1)]], False),
    ('drop_degenerate', [[], 1e-09], [], False),
    ('fan_triangulate', [[(0, 0), (1, 0), (1, 1)]], [[(0, 0), (1, 0), (1, 1)]], False),
    ('fan_triangulate', [[(0, 0), (1, 0), (1, 1), (0, 1)]], [[(0, 0), (1, 0), (1, 1)], [(0, 0), (1, 1), (0, 1)]], False),
    ('weld_vertices', [[(0, 0), (0.0001, 0), (1, 1)], 0.01], [(0, 0), (0, 0), (1, 1)], False),
    ('weld_vertices', [[(0, 0), (0.0001, 0), (1, 1)], 1e-09], [(0, 0), (0.0001, 0), (1, 1)], False),
    ('fix_orientation', [[[(0, 0), (0, 1), (1, 0)]]], [[(0, 0), (1, 0), (0, 1)]], False),
    ('fix_orientation', [[[(0, 0), (1, 0), (0, 1)]]], [[(0, 0), (1, 0), (0, 1)]], False),
    ('cache_key', ['m', 'union', 2], 'm|union|2', False),
    ('rebuild_uv', [[(-0.5, 0.5), (1.2, -1.0)]], [[0.0, 0.5], [1.0, 0.0]], False),
    ('group_materials', [['a', 'b', 'a']], {'a': 2, 'b': 1}, False),
    ('depth_allowed', [3, 3], True, False),
    ('commit_batch', [[True, False]], False, False),
]


@pytest.mark.parametrize("func_name,args,expected,approx", CASES)
def test_csg_boolean_contract(func_name, args, expected, approx):
    func = getattr(mod, func_name)
    result = func(*args)
    if approx:
        assert result == pytest.approx(expected)
    else:
        assert result == expected
