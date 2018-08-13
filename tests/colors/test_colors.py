import pytest

from pyqttoolkit.colors import *

@pytest.mark.parametrize('hex_,rgb', [
    ('#ffffff', (1, 1, 1)),
    ('#000000', (0, 0, 0)),
    ('#FFFFFF', (1, 1, 1)),
    ('#0080FF', (0, 128/255, 1))
])
def test_hex_to_rgb_converts_correctly(hex_, rgb):
    assert hex_to_rgb(hex_) == rgb

@pytest.mark.parametrize('hex_,rgb', [
    ('#ffffff', (1, 1, 1)),
    ('#000000', (0, 0, 0)),
    ('#0080ff', (0, 128/255, 1))
])
def test_rgb_to_hex_converts_correctly(rgb, hex_):
    assert rgb_to_hex(rgb) == hex_


@pytest.mark.parametrize('a,b,n,result', [
    ((0, 0, 0), (1, 1, 1), 1, [(0.5, 0.5, 0.5)]),
    ((0, 0, 0), (1, 1, 1), 3, [(0.25, 0.25, 0.25), (0.5, 0.5, 0.5), (0.75, 0.75, 0.75)]),
    ((0, 0, 0), (0.75, 0.75, 0.75), 2, [(0.25, 0.25, 0.25), (0.5, 0.5, 0.5)]),
    ((0, 1, 0), (0.75, 0.25, 0.75), 2, [(0.25, 0.75, 0.25), (0.5, 0.5, 0.5)]),
])
def test_interpolate_rgb_returns_correct_values(a, b, n, result):
    assert interpolate_rgb(a, b, n) == result

def test_expand_rgb_expands_simple_sequence():
    assert expand_rgb([(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)], 5) == [(0, 0, 0), (0.25, 0.25, 0.25), (0.5, 0.5, 0.5), (0.75, 0.75, 0.75), (1.0, 1.0, 1.0)]

def test_expand_rgb_returns_original_sequence_if_no_extras():
    assert expand_rgb([(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)], 3) == [(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)]
    
def test_expand_rgb_returns_original_sequence_if_fewer_required():
    assert expand_rgb([(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)], 2) == [(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)]