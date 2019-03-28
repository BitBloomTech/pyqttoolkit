# pyqttoolkit
# Copyright (C) 2018-2019, Simmovation Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
from enum import Enum

from itertools import chain
from math import ceil

def hex_to_rgb(hex_value):
    hex_value = hex_value.lstrip('#')
    return tuple(int(hex_value[i:i+2], 16) / 255 for i in [0, 2, 4])

def rgb_to_hex(rgb_value):
    return '#' + ''.join('{:02x}'.format(int(v * 255)) for v in rgb_value)

def interpolate_rgb(a, b, n):
    if n <= 0:
        return [a, b]
    step = tuple((b_val - a_val) / (n + 1) for a_val, b_val in zip(a, b))
    return [tuple(a_val + step_val * i for a_val, step_val in zip(a, step)) for i in range(1, n+1)]

def expand_rgb(colors, n):
    extras_per_gap = int(ceil((n - len(colors)) / (len(colors) - 1)))
    if extras_per_gap <= 0:
        return list(colors)
    result = [*chain(
        *([a, *interpolate_rgb(a, b, extras_per_gap)] for a, b in zip(colors, colors[1:]))
    ), colors[-1]]
    return result

class ColorFormat(Enum):
    rgba_string_256 = 0
    rgb_string_256 = 1
    hex_string = 2
    hexa_string = 3

def format_color(color, color_format=ColorFormat.rgba_string_256, opacity=None, lighten=None):
    if len(color) == 4:
        r, g, b, a = color
    elif len(color) == 3:
        r, g, b = color
        a = 255
    else:
        raise ValueError(f'Invalid value for color: {color}')
    a = a if opacity is None else opacity

    if lighten is not None:
        r, g, b = redistribute_rgb(lighten * (r or 100), lighten * (g or 100), lighten * (b or 100))

    if color_format == ColorFormat.rgba_string_256:
        return f'rgba({r},{g},{b},{a})'
    if color_format == ColorFormat.rgb_string_256:
        return f'rgb({r},{g},{b})'
    if color_format == ColorFormat.hex_string:
        return '#{:02x}{:02x}{:02x}'.format(*(int(c * 255) for c in (r, g, b)))
    if color_format == ColorFormat.hexa_string:
        return '#{:02x}{:02x}{:02x}{:02x}'.format(*(int(c * 255) for c in (a, r, g, b)))
    
    raise ValueError(f'Invalid format: {color_format}')

def redistribute_rgb(r, g, b):
    threshold = 255.999
    m = max(r, g, b)
    if m <= threshold:
        return int(r), int(g), int(b)
    total = r + g + b
    if total >= 3 * threshold:
        return int(threshold), int(threshold), int(threshold)
    x = (3 * threshold - total) / (3 * m - total)
    gray = threshold - x * m
    return int(gray + x * r), int(gray + x * g), int(gray + x * b)
