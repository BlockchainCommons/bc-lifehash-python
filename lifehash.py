"""
python implementation of https://github.com/BlockchainCommons/bc-lifehash
"""

from math import fmod
import math
import functools
from bitstring import BitArray
from hashlib import sha256
import unittest

def lerp_to(toA, toB, t):
    """
    Interpolate t from [0..1] to [a..b].
    """
    return t * (toB - toA) + toA

def lerp_from(fromA, fromB, t):
    """
    Interpolate t from [a..b] to [0..1].
    """
    return (fromA - t) / (fromA - fromB)

def lerp(fromA, fromB, toC, toD, t):
    return lerp_to(toC, toD, lerp_from(fromA, fromB, t))

def clamped(n):
    """
    Return n clamped to the range [0..1].
    """
    return max(min(n, 1), 0)

def modulo(dividend, divisor):
    x = fmod(fmod(dividend, divisor) + divisor, divisor)
    return x

class BitAggregator:
    def __init__(self):
        self._data = list()
        self.bitMask = 0

    def append(self, bit: bool):
        if self.bitMask == 0:
            self.bitMask = 0x80
            self._data.append(0)

        if bit:
            self._data[-1] |= self.bitMask

        self.bitMask >>= 1

    def get_data(self):
        return bytes(self._data)

class BitEnumerator:
    def __init__(self, data):
        self.data = data
        self.index = 0
        self.mask = 0x80

    #def for_all(self, callback):
    #    while self.has_next():
    #        callback(self.next())

    def has_next(self):
        return self.mask != 0 or self.index != (len(self.data) - 1)

    def next(self):
        if not self.has_next():
            raise Exception("BitEnumerator underflow.")

        if self.mask == 0:
            self.mask = 0x80
            self.index += 1

        b = (self.data[self.index] & self.mask) != 0

        self.mask >>= 1

        return b

    def next_configurable(self, bitMask, bits):
        value = 0
        for i in range(0, bits):
            if self.next():
                value |= bitMask
            bitMask >>= 1
        return value

    def next_uint2(self):
        bitMask = 0x02
        return self.next_configurable(bitMask, 2)

    def next_uint8(self):
        bitMask = 0x80
        return self.next_configurable(bitMask, 8)

    def next_uint16(self):
        bitMask = 0x8000
        return self.next_configurable(bitMask, 16)

    def next_frac(self):
        return self.next_uint16() / 65535.0

class Size:
    # public
    width: int
    height: int

    def __init__(self, width, height):
        self.width = width
        self.height = height

class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Point):
            return other.x == self.x and other.y == self.y
        else:
            return other.__eq__(self)
Point.zero = Point(0, 0)

class Grid:
    # public
    size: Size

    # private
    _capacity: int
    _maxX: int
    _maxY: int

    _storage: list

    def __init__(self, size: Size):
        self.size = size
        self._capacity = size.width * size.height
        # TODO: what should be the default value in _storage ?
        self._storage = [0] * (size.width * size.height)
        self._maxX = size.width  - 1
        self._maxY = size.height - 1

    def _offset(self, point: Point):
        return point.y * self.size.width + point.x

    @staticmethod
    def circular_index(index, modulus):
        return (index + modulus) % modulus

    def set_all(self, value):
        self._storage = [value] * self._capacity

    def set_value(self, value, point: Point):
        offset = self._offset(point)
        self._storage[offset] = value

    def get_value(self, point: Point):
        return self._storage[self._offset(point)]

    #def for_all(self, some_callback):
    #    for y in range(0, self._maxY + 1):
    #        for x in range(0, self._maxX + 1):
    #            some_callback(Point(x, y))

    #@property
    #def points(self):
    #    points = []
    #    for y in range(0, self._maxY + 1):
    #        for x in range(0, self._maxX + 1):
    #            points.append(Point(x, y))
    #    return points

    def get_points(self):
        counter = 0
        for y in range(0, self._maxY + 1):
            for x in range(0, self._maxX + 1):
                counter += 1
                yield Point(x, y)

        assert counter == len(self._storage) == self._capacity

    #def for_neighborhood(self, point: Point, some_callback):
    #    for oy in range(-1, 1 + 1):
    #        for ox in range(-1, 1 + 1):
    #            o = Point(ox, oy)
    #            px = Grid.circular_index(ox + point.x, self.size.width)
    #            py = Grid.circular_index(oy + point.y, self.size.height)
    #            p = Point(px, py)
    #            some_callback(o, p)

    def get_neighborhood(self, point: Point):
        point_pairs = []
        for oy in range(-1, 1 + 1):
            for ox in range(-1, 1 + 1):
                o = Point(ox, oy)
                px = Grid.circular_index(ox + point.x, self.size.width)
                py = Grid.circular_index(oy + point.y, self.size.height)
                p = Point(px, py)
                point_pairs.append((o, p))
                yield (o, p)

    def colors(self):
        result = []

        for (idx, color_value) in enumerate(self._storage):
            color = self.color_for_value(color_value)

            result.append(color.r)
            result.append(color.g)
            result.append(color.b)

        return result

class Color:
    r: float
    g: float
    b: float

    def __init__(self, r=0, g=0, b=0):
        (self.r, self.g, self.b) = (r, g, b)

    @classmethod
    def from_uint8_values(cls, r, g, b):
        x = cls(r / 255, g / 255, b / 255)
        return x

    def lighten(self, t):
        return self.lerp_to(Colors.white, t)

    def darken(self, t):
        return self.lerp_to(Colors.black, t)

    def luminance(self):
        return math.sqrt(math.pow(0.299 * self.r, 2) + math.pow(0.587 * self.g, 2) + math.pow(0.144 * self.b, 2))

    def burn(self, t):
        f = max(1.0 - t, 1.0e-7)
        return self.__class__(
            min(1.0 - (1.0 - self.r) / f, 1.0),
            min(1.0 - (1.0 - self.g) / f, 1.0),
            min(1.0 - (1.0 - self.b) / f, 1.0),
        )

    def lerp_to(self, other, t):
        f = clamped(t)
        red = clamped(self.r * (1 - f) + other.r * f)
        green = clamped(self.g * (1 - f) + other.g * f)
        blue = clamped(self.b * (1 - f) + other.b * f)
        return self.__class__(red, green, blue)

class Colors:
    white = Color(1, 1, 1)
    black = Color(0, 0, 0)
    red = Color(1, 0, 0)
    green = Color(0, 1, 0)
    blue = Color(0, 0, 1)
    cyan = Color(0, 1, 1)
    magenta = Color(1, 0, 1)
    yellow = Color(1, 1, 0)

class CellGrid(Grid):
    """
    A class that holds an array of boolean cells and that is capable of running
    Conway's Game of Life to produce the next generation.
    """

    def __init__(self, size: Size):
        self.data = BitAggregator()
        super().__init__(size)

    def get_data(self):
        aggregator = BitAggregator()

        #self.for_all(lambda p: aggregator.append(self.get_value(p)))
        for point in self.get_points():
            aggregator.append(self.get_value(point))

        return aggregator.get_data()

    def set_data(self, data):
        assert self._capacity == len(bytes(data)) * 8
        # TODO: does this need to be multiplied by 8?

        e = BitEnumerator(data)
        i = 0

        #def callback(boolean):
        #    self._storage[i] = boolean
        #    i += 1
        #e.for_all(callback)

        while e.has_next():
            boolean = e.next()
            self._storage[i] = boolean
            i += 1

    @staticmethod
    def is_alive_in_next_generation(current_alive, neighbors_count):
        if current_alive:
            return neighbors_count in [2, 3]
        else:
            return neighbors_count == 3

    def count_neighbors(self, point: Point):
        total = 0

        for (point_o, point_p) in self.get_neighborhood(point):
            if point_o == Point.zero:
                continue

            if self.get_value(point_p):
                total += 1

        return total

    def next_generation(self, current_change_grid, next_cell_grid, next_change_grid):
        next_cell_grid.set_all(False)
        next_change_grid.set_all(False)

        for p in self.get_points():
            current_alive = self.get_value(p)
            if current_change_grid.get_value(p):
                neighbors_count = self.count_neighbors(p)
                next_alive = CellGrid.is_alive_in_next_generation(current_alive, neighbors_count)
                if next_alive:
                    next_cell_grid.set_value(True, p)
                if current_alive != next_alive:
                    next_change_grid.set_changed(p)
            else:
                next_cell_grid.set_value(current_alive, p)

    def color_for_value(self, value):
        if value:
            return Colors.white
        else:
            return Colors.black

class FracGrid(Grid):
    def overlay(self, cell_grid: CellGrid, frac):
        for point in self.get_points():
            if cell_grid.get_value(point):
                self.set_value(frac, point)

    def color_for_value(self, value):
        return Colors.black.lerp_to(Colors.white, value)

class ChangeGrid(Grid):
    def set_changed(self, point: Point):
        for (o, p) in self.get_neighborhood(point):
            self.set_value(True, p)

    def color_for_value(self, value):
        if value:
            return Colors.red
        else:
            return Colors.blue

class Pattern:

    snowflake = 0 # Mirror around central axes.
    pinwheel = 1 # Rotate around center.
    fiducial = 2 # Identity.

    @staticmethod
    def select_pattern(entropy, version):
        if version in [LifeHashVersion.fiducial, LifeHashVersion.grayscale_fiducial]:
            return Pattern.fiducial
        else:
            #if next(entropy):
            if entropy.next():
                return Pattern.snowflake
            else:
                return Pattern.pinwheel

class Transform:
    transpose: bool
    reflect_x: bool
    reflect_y: bool

    def __init__(self, transpose, reflect_x, reflect_y):
        self.transpose = transpose
        self.reflect_x = reflect_x
        self.reflect_y = reflect_y

class ColorGrid(Grid):
    """
    A class that takes a grayscale grid and applies color and symmetry to it to
    yield the finished LifeHash.
    """

    snowflake_transforms = [
        Transform(False, False, False),
        Transform(False, True, False),
        Transform(False, False, True),
        Transform(False, True, True),
    ]

    pinwheel_transforms = [
        Transform(False, False, False),
        Transform(True, True, False),
        Transform(True, False, True),
        Transform(False, True, True),
    ]

    fiducial_transforms = [
        Transform(False, False, False),
    ]

    transforms_map = {
        Pattern.snowflake: snowflake_transforms,
        Pattern.pinwheel: pinwheel_transforms,
        Pattern.fiducial: fiducial_transforms
    }

    def __init__(self, frac_grid: "FracGrid", gradient: "ColorFunc", pattern: Pattern):

        size = self.target_size(frac_grid.size, pattern)
        super().__init__(size=size)

        if pattern in self.transforms_map.keys():
            transforms = self.transforms_map[pattern]
        else:
            transforms = []

        for point in frac_grid.get_points():
            value = frac_grid.get_value(point)
            some_color = gradient(value)
            self.draw(point, some_color, transforms)

    def color_for_value(self, color):
        return color

    def target_size(self, in_size: Size, pattern: Pattern):
        if pattern == Pattern.fiducial:
            multiplier = 1
        else:
            multiplier = 2
        return Size(in_size.width * multiplier, in_size.height * multiplier)

    def transform_point(self, point: Point, transform: Transform):
        result = Point(point.x, point.y)

        if transform.transpose:
            # swap values
            (result.x, result.y) = (result.y, result.x)

        if transform.reflect_x:
            result.x = self._maxX - result.x

        if transform.reflect_y:
            result.y = self._maxY - result.y

        return result

    def draw(self, point: Point, color: Color, transforms):
        for transform in transforms:
            p2 = self.transform_point(point, transform)
            self.set_value(color, p2)

class HSBColor:
    """
    Only used in version1 lifehashes. Represents a color in the HSB space.
    """

    hue: float
    saturation: float
    brightness: float

    def __init__(self, hue, saturation=1, brightness=1):
        self.hue = hue
        self.saturation = saturation
        self.brightness = brightness

    def to_color(self):
        brightness = self.brightness
        saturation = self.saturation
        hue = self.hue

        v = clamped(brightness)
        s = clamped(saturation)

        (red, green, blue) = (None, None, None)

        if s <= 0:
            (red, green, blue) = (v, v, v)
        else:
            h = modulo(hue, 1)
            if h < 0:
                h += 1
            h *= 6
            i = floor(h)
            f = h - i
            p = v * (1 - s)
            q = v * (1 - s * f)
            t = v * (1 - s * (1 - f))

            if i == 0:
                (red, green, blue) = (v, t, p)
            elif i == 1:
                (red, green, blue) = (q, v, p)
            elif i == 2:
                (red, green, blue) = (p, v, t)
            elif i == 3:
                (red, green, blue) = (p, q, v)
            elif i == 4:
                (red, green, blue) = (t, p, v)
            elif i == 5:
                (red, green, blue) = (v, p, q)
            else:
                raise Exception("Internal error.")

        return Color(red, green, blue)

    @classmethod
    def make_from_color(cls, color):
        (r, g, b) = (color.r, color.g, color.b)

        max_value = max(r, g, b)
        min_value = min(r, g, b)

        brightness = max_value

        d = max_value - min_value

        saturation = None
        if max_value == 0:
            saturation = 0
        else:
            saturation = d / max_value

        hue = None

        if max_value == min_value:
            hue = 0 # achromatic
        else:
            if max_value == r:
                hue = ((g - b) / d + (6 if g < b else 0)) / 6
            elif max_value == g:
                hue = ((b - r) / d + 2) / 6
            elif max_value == b:
                hue = ((r - g) / d + 4) / 6
            else:
                raise Exception("Internal error.")


        return cls(hue=hue, saturation=saturation, brightness=brightness)

def reverse(some_colorfunc):
    def reverse_anonfunc(t):
        return some_colorfunc(1 - t)
    return reverse_anonfunc

def blend(color1, color2):
    def blendanonfunc(t):
        return color1.lerp_to(color2, t)
    return blendanonfunc

def blend_many(colors):
    color_count = len(colors)
    if color_count == 0:
        return blend(Colors.black, Colors.black)
    elif color_count == 1:
        return blend(colors[0], colors[0])
    elif color_count == 2:
        return blend(colors[0], colors[1])
    else:
        def blendmanyanonfunc(t):
            if t >= 1:
                return colors[color_count - 1]
            elif t <= 0:
                return colors[0]
            else:
                segments = color_count - 1
                s = t * segments
                # TODO: what's the correct python translation of this?
                #segment = size_t(s)
                segment = int(s)
                segment_frac = modulo(s, 1)
                c1 = colors[segment]
                c2 = colors[segment + 1]
                return c1.lerp_to(c2, segment_frac)
        return blendmanyanonfunc

grayscale = blend(Colors.black, Colors.white)

def select_grayscale(entropy: "BitEnumerator"):
    if entropy.next():
        return grayscale
    else:
        return reverse(grayscale)

def make_hue(t):
    return HSBColor(t).to_color()

spectrum_colors = [
    (0, 168, 222),
    (51, 51, 145),
    (233, 19, 136),
    (235, 45, 46),
    (253, 233, 43),
    (0, 158, 84),
    (0, 168, 222),
]
spectrum = blend_many([Color.from_uint8_values(*vals) for vals in spectrum_colors])

spectrum_cmyk_safe_colors = [
    (0, 168, 222),
    (41, 60, 130),
    (210, 59, 130),
    (217, 63, 53),
    (244, 228, 81),
    (0, 158, 84),
    (0, 168, 222),
]
spectrum_cmyk_safe = blend_many([Color.from_uint8_values(*vals) for vals in spectrum_cmyk_safe_colors])

def adjust_for_luminance(color, contrast_color):
    lum = color.luminance()
    contrast_lum = contrast_color.luminance()

    threshold = 0.6
    offset = abs(lum - contrast_lum)
    if offset > threshold:
        return color

    boost = 0.7
    t = lerp(0, threshold, boost, 0, offset)
    if contrast_lum > lum:
        # darken this color
        return color.darken(t).burn(t * 0.6)
    else:
        # lighten this color
        return color.lighten(t).burn(t * 0.6)

def monochromatic(entropy, hue_generator):
    hue = entropy.next_frac()
    is_tint = entropy.next()
    is_reversed = entropy.next()
    key_advance = entropy.next_frac() * 0.3 + 0.05
    neutral_advance = entropy.next_frac() * 0.3 + 0.05

    key_color = hue_generator(hue)

    contrast_brightness = None
    if is_tint:
        contrast_brightness = 1
        key_color = key_color.darken(0.5)
    else:
        contrast_brightness = 0

    neutral_color = grayscale(contrast_brightness)

    key_color_2 = key_color.lerp_to(neutral_color, key_advance)
    neutral_color_2 = neutral_color.lerp_to(key_color, neutral_advance)

    gradient = blend(key_color_2, neutral_color_2)

    if is_reversed:
        return reverse(gradient)
    else:
        return gradient

def monochromatic_fiducial(entropy):
    hue = entropy.next_frac()
    is_reversed = entropy.next()
    is_tint = entropy.next()

    contrast_color = Colors.white if is_tint else Colors.black
    key_color = adjust_for_luminance(spectrum_cmyk_safe(hue), contrast_color)

    gradient = blend_many([key_color, contrast_color, key_color])
    if is_reversed:
        return reverse(gradient)
    else:
        return gradient

def complementary(entropy, hue_generator):
    spectrum1 = entropy.next_frac()
    spectrum2 = modulo(spectrum1 + 0.5, 1)
    lighter_advance = entropy.next_frac() * 0.3
    darker_advance = entropy.next_frac() * 0.3
    is_reversed = entropy.next()

    color1 = hue_generator(spectrum1)
    color2 = hue_generator(spectrum2)

    luma1 = color1.luminance()
    luma2 = color2.luminance()

    darker_color = None
    lighter_color = None
    if luma1 > luma2:
        darker_color = color2
        lighter_color = color1
    else:
        darker_color = color1
        lighter_color = color2

    adjusted_lighter_color = lighter_color.lighten(lighter_advance)
    adjusted_darker_color = darker_color.darken(darker_advance)
    gradient = blend(adjusted_darker_color, adjusted_lighter_color)

    if is_reversed:
        return reverse(gradient)
    else:
        return gradient

def complementary_fiducial(entropy):
    spectrum1 = entropy.next_frac()
    spectrum2 = modulo(spectrum1 + 0.5, 1)
    is_tint = entropy.next()
    is_reversed = entropy.next()
    neutral_color_bias = entropy.next()

    neutral_color = Colors.white if is_tint else Colors.black
    color1 = spectrum_cmyk_safe(spectrum1)
    color2 = spectrum_cmyk_safe(spectrum2)

    biased_neutral_color = neutral_color.lerp_to(color1 if neutral_color_bias else color2, 0.2).burn(0.1)
    gradient = blend_many([
        adjust_for_luminance(color1, biased_neutral_color),
        biased_neutral_color,
        adjust_for_luminance(color2, biased_neutral_color),
    ])
    if is_reversed:
        return reverse(gradient)
    else:
        return gradient

def triadic(entropy, hue_generator):
    spectrum1 = entropy.next_frac()
    spectrum2 = modulo(spectrum1 + 1.0 / 3, 1)
    spectrum3 = modulo(spectrum1 + 2.0 / 3, 1)
    lighter_advance = entropy.next_frac() * 0.3
    darker_advance = entropy.next_frac() * 0.3
    is_reversed = entropy.next()

    color1 = hue_generator(spectrum1)
    color2 = hue_generator(spectrum2)
    color3 = hue_generator(spectrum3)
    colors = [color1, color2, color3]

    def comparison(a, b):
        return a.luminance() < b.luminance()

    colors = sorted(colors, key=functools.cmp_to_key(comparison))

    darker_color = colors[0]
    middle_color = colors[1]
    lighter_color = colors[2]

    adjusted_lighter_color = lighter_color.lighten(lighter_advance)
    adjusted_darker_color = darker_color.darken(darker_advance)

    gradient = blend_many([adjusted_lighter_color, middle_color, adjusted_darker_color])
    if is_reversed:
        return reverse(gradient)
    else:
        return gradient

def triadic_fiducial(entropy):
    spectrum1 = entropy.next_frac()
    spectrum2 = modulo(spectrum1 + 1.0 / 3, 1)
    spectrum3 = modulo(spectrum1 + 2.0 / 3, 1)
    is_tint = entropy.next()
    neutral_insert_index = entropy.next_uint8() % 2 + 1
    is_reversed = entropy.next()

    neutral_color = Colors.white if is_tint else Colors.black

    colors = [spectrum_cmyk_safe(spectrum1), spectrum_cmyk_safe(spectrum2), spectrum_cmyk_safe(spectrum3)]
    if neutral_insert_index == 1:
        colors[0] = adjust_for_luminance(colors[0], neutral_color)
        colors[1] = adjust_for_luminance(colors[1], neutral_color)
        colors[2] = adjust_for_luminance(colors[2], colors[1])
    elif neutral_insert_index == 2:
        colors[1] = adjust_for_luminance(colors[1], neutral_color)
        colors[2] = adjust_for_luminance(colors[2], neutral_color)
        colors[0] = adjust_for_luminance(colors[0], colors[1])
    else:
        raise Exception("Internal error.")

    colors.insert(neutral_insert_index, neutral_color)
    gradient = blend_many(colors)
    if is_reversed:
        return reverse(gradient)
    else:
        return gradient

def analogous(entropy, hue_generator):
    spectrum1 = entropy.next_frac()
    spectrum2 = modulo(spectrum1 + 1.0 / 12, 1)
    spectrum3 = modulo(spectrum1 + 2.0 / 12, 1)
    spectrum4 = modulo(spectrum1 + 3.0 / 12, 1)
    advance = entropy.next_frac() * 0.5 + 0.2
    is_reversed = entropy.next()

    color1 = hue_generator(spectrum1)
    color2 = hue_generator(spectrum2)
    color3 = hue_generator(spectrum3)
    color4 = hue_generator(spectrum4)

    (darkest_color, dark_color, light_color, lightest_color) = (None, None, None, None)

    if color1.luminance() < color4.luminance():
        darkest_color = color1
        dark_color = color2
        light_color = color3
        lightest_color = color4
    else:
        darkest_color = color4
        dark_color = color3
        light_color = color2
        lightest_color = color1

    adjusted_darkest_color = darkest_color.darken(advance)
    adjusted_dark_color = dark_color.darken(advance / 2)
    adjusted_light_color = light_color.lighten(advance / 2)
    adjusted_lightest_color = lightest_color.lighten(advance)

    gradient = blend_many([adjusted_darkest_color, adjusted_dark_color, adjusted_light_color, adjusted_lightest_color])
    if is_reversed:
        return reverse(gradient)
    else:
        return gradient

def analogous_fiducial(entropy):
    spectrum1 = entropy.next_frac()
    spectrum2 = modulo(spectrum1 + 1.0 / 10, 1)
    spectrum3 = modulo(spectrum1 + 2.0 / 10, 1)
    is_tint = entropy.next()
    neutral_insert_index = entropy.next_uint8() % 2 + 1
    is_reversed = entropy.next()

    neutral_color = Colors.white if is_tint else Colors.black

    colors = [spectrum_cmyk_safe(spectrum1), spectrum_cmyk_safe(spectrum2), spectrum_cmyk_safe(spectrum3)]

    if neutral_insert_index == 1:
        colors[0] = adjust_for_luminance(colors[0], neutral_color)
        colors[1] = adjust_for_luminance(colors[1], neutral_color)
        colors[2] = adjust_for_luminance(colors[2], colors[1])
    elif neutral_insert_index == 2:
        colors[1] = adjust_for_luminance(colors[1], neutral_color)
        colors[2] = adjust_for_luminance(colors[2], neutral_color)
        colors[0] = adjust_for_luminance(colors[0], colors[1])
    else:
        raise Exception("Internal error")

    colors.insert(neutral_insert_index, neutral_color)

    gradient = blend_many(colors)
    if is_reversed:
        return reverse(gradient)
    else:
        return gradient

def select_gradient(entropy: "BitEnumerator", version):
    """
    A function that takes a deterministic source of bits and selects a gradient
    used to color a particular Lifehash version. This function itself returns
    another function.
    """

    if version == LifeHashVersion.grayscale_fiducial:
        return select_grayscale(entropy)

    value = entropy.next_uint2()

    if value == 0:
        if version == LifeHashVersion.version1:
            return monochromatic(entropy, make_hue)
        elif version == LifeHashVersion.version2 or version == LifeHashVersion.detailed:
            return monochromatic(entropy, spectrum_cmyk_safe)
        elif version == LifeHashVersion.fiducial:
            return monochromatic_fiducial(entropy)
        elif version == LifeHashVersion.grayscale_fiducial:
            return grayscale;
    elif value == 1:
        if version == LifeHashVersion.version1:
            return complementary(entropy, spectrum)
        elif version == LifeHashVersion.version2 or version == LifeHashVersion.detailed:
            return complementary(entropy, spectrum_cmyk_safe)
        elif version == LifeHashVersion.fiducial:
            return complementary_fiducial(entropy)
        elif version == LifehashVersion.grayscale_fiducial:
            return grayscale
    elif value == 2:
        if version == LifeHashVersion.version1:
            return triadic(entropy, spectrum)
        elif version == LifeHashVersion.version2 or version == LifeHashVersion.detailed:
            return triadic(entropy, spectrum_cmyk_safe)
        elif version == LifeHashVersion.fiducial:
            return triadic_fiducial(entropy)
        elif version == LifehashVersion.grayscale_fiducial:
            return grayscale
    elif value == 3:
        if version == LifeHashVersion.version1:
            return analogous(entropy, spectrum)
        elif version == LifeHashVersion.version2 or version == LifeHashVersion.detailed:
            return analogous(entropy, spectrum_cmyk_safe)
        elif version == LifeHashVersion.fiducial:
            return analogous_fiducial(entropy)
        elif version == LifehashVersion.grayscale_fiducial:
            return grayscale

    return grayscale

class Image:
    width: int
    height: int
    colors: list

    def __init__(self, width, height, colors):
        self.width = width
        self.height = height
        self.colors = colors

    @staticmethod
    def make_image(width, height, colors, module_size, has_alpha):
        if module_size == 0:
            raise Exception("Invalid module size.")

        scaled_width = width * module_size
        scaled_height = height * module_size
        result_components = None
        if has_alpha:
            result_components = 4
        else:
            result_components = 3
        scaled_capacity = scaled_width * scaled_height * result_components;

        result_colors = {}
        for target_y in range(0, scaled_width):
            for target_x in range(0, scaled_height):
                source_x = target_x / module_size
                source_y = target_y / module_size
                source_offset = (source_y * width + source_x) * 3
                target_offset = (target_y * scaled_width + target_x) * result_components

                source_offset = int(source_offset)

                result_colors[target_offset] = math.floor(clamped(colors[source_offset]) * 255)
                result_colors[target_offset + 1] = math.floor(clamped(colors[source_offset + 1]) * 255)
                result_colors[target_offset + 2] = math.floor(clamped(colors[source_offset + 2]) * 255)

                if has_alpha:
                    result_colors[target_offset + 3] = 255

        return Image(scaled_width, scaled_height, list(result_colors.values()))

# An enum of the versions of LifeHash that are available
class LifeHashVersion:
    version1 = 1
    version2 = 2
    detailed = 3
    fiducial = 4
    grayscale_fiducial = 5

class LifeHash:

    @classmethod
    def make_from(cls, data, version=LifeHashVersion.version2, module_size=1, has_alpha=False):
        """
        Make a lifehash from raw data that hasn't been hashed yet.
        """
        if isinstance(data, str):
            data = data.encode()

        if not isinstance(data, bytes):
            raise Exception("data must be utf-8 string or bytes")

        digest = sha256(data).digest()
        return cls.make_from_digest(digest, version=version, module_size=module_size, has_alpha=has_alpha)

    @staticmethod
    def make_from_digest(digest: bytes, version=LifeHashVersion.version2, module_size=1, has_alpha=False):
        """
        Make a lifehash from a 32-byte hash digest.
        """
        if len(digest) != 32:
            raise Exception("Digest must be 32 bytes.")

        length: int = None
        max_generations: int = None

        if version in [LifeHashVersion.version1, LifeHashVersion.version2]:
            length = 16
            max_generations = 150
        elif version in [LifeHashVersion.detailed, LifeHashVersion.fiducial, LifeHashVersion.grayscale_fiducial]:
            length = 32
            max_generations = 300
        else:
            raise Exception("Invalid version.")

        size = Size(length, length)

        current_cell_grid = CellGrid(size)
        next_cell_grid = CellGrid(size)
        current_change_grid = ChangeGrid(size)
        next_change_grid = ChangeGrid(size)

        history_set = set()
        history = []

        if version == LifeHashVersion.version1:
            next_cell_grid.set_data(digest)
        elif version == LifeHashVersion.version2:
            # ensure that .version 2 in no way resembles .version1
            next_cell_grid.set_data(sha256(digest).digest())
        else:
            digest1 = digest

            # ensure that grayscale fiducials in no way resemble the regular color fiducials
            if version == LifeHashVersion.grayscale_fiducial:
                digest1 = sha256(digest1)

            digest2 = sha256(digest1)
            digest3 = sha256(digest2)
            digest4 = sha256(digest3)
            digest_final = digest1

            digest_final += digest2
            digest_final += digest3
            digest_final += digest4
            next_cell_grid.set_data(digest_final.digest())

        next_change_grid.set_all(True)

        while len(history) < max_generations:
            (current_cell_grid, next_cell_grid) = (next_cell_grid, current_cell_grid)
            (current_change_grid, next_change_grid) = (next_change_grid, current_change_grid)

            data = current_cell_grid.get_data()
            _hash = sha256(data)
            if _hash.digest() in history_set:
                break

            history_set.add(_hash.digest())
            history.append(data)

            current_cell_grid.next_generation(current_change_grid, next_cell_grid, next_change_grid)

        frac_grid = FracGrid(size)
        for (i, history_item) in enumerate(history):
            current_cell_grid.set_data(history[i])
            frac = clamped(lerp_from(0, len(history), i+1))
            frac_grid.overlay(current_cell_grid, frac)

        # Normalizing the frac_grid to the range 0..1 was a step left out of
        # version1. In some cases it can cause the full range of the gradient
        # to go unused. This fixes the problem for the other versions, while
        # remaining compatible with version1.
        if version != LifeHashVersion.version1:
            min_value = None
            max_value = None

            values = []
            for point in frac_grid.get_points():
                value = frac_grid.get_value(point)
                values.append(value)

            min_value = min(values)
            max_value = max(values)

            frac_grid_points = 0
            for point in frac_grid.get_points():
                current_value = frac_grid.get_value(point)
                value = lerp_from(min_value, max_value, current_value)
                frac_grid.set_value(value, point)
                frac_grid_points += 1

        entropy = BitEnumerator(digest)

        if version == LifeHashVersion.detailed:
            # Throw away a bit of entropy to ensure we generate different
            # colors and patterns from .version1.
            ##entropy = entropy[1:]
            #next(entropy)
            entropy.next()
        elif version == LifeHashVersion.version2:
            # Throw away two bits of entropy to ensure we generate different
            # colors and patterns from .version1 or .detailed.
            ##entropy = entropy[2:]
            #next(entropy)
            val = entropy.next()
            val = entropy.next()

        gradient = select_gradient(entropy, version)
        pattern = Pattern.select_pattern(entropy, version)
        color_grid = ColorGrid(frac_grid, gradient, pattern)
        colors = color_grid.colors()

        image = Image.make_image(color_grid.size.width, color_grid.size.height, colors, module_size, has_alpha)

        return image

class LifeHashTestCase(unittest.TestCase):
    def test_size(self):
        size = Size(50, 60)
        self.assertEqual(size.width, 50)
        self.assertEqual(size.height, 60)

    def test_point(self):
        point = Point(5, 6)
        self.assertEqual(point.x, 5)
        self.assertEqual(point.y, 6)

    def test_point_equality(self):
        p1 = Point(5, 6)
        p2 = Point(5, 6)
        p3 = Point(5, 7)
        self.assertEqual(p1, p2)
        self.assertEqual(p2, p1)
        self.assertNotEqual(p1, p3)
        self.assertNotEqual(p2, p3)
        self.assertNotEqual(p3, p1)
        self.assertNotEqual(p3, p2)

    def test_grid(self):
        size = Size(180, 60)
        grid = Grid(size=size)

    def test_lifehash(self):
        image = LifeHash.make_from(b"Hello")
        self.assertEqual(image.width, 32)
        self.assertEqual(image.height, 32)
        expected = [146, 126, 130, 178, 104, 92, 182, 101, 87, 202, 88, 64, 199, 89, 66, 197, 90, 69, 182, 101, 87, 180, 102, 89, 159, 117, 114, 210, 82, 54]
        self.assertEqual(image.colors[:30], expected)

    def test_lifehash_with_alpha(self):
        image = LifeHash.make_from(b"Hello", version=LifeHashVersion.version2, module_size=1, has_alpha=True)
        self.assertEqual(image.width, 32)
        self.assertEqual(image.height, 32)
        expected = [146, 126, 130, 255, 178, 104, 92, 255, 182, 101, 87, 255, 202, 88, 64, 255, 199, 89, 66, 255, 197, 90, 69, 255, 182, 101, 87, 255, 180, 102, 89, 255, 159, 117, 114, 255, 210, 82, 54, 255]
        self.assertEqual(image.colors[:40], expected)


if __name__ == "__main__":
    unittest.main()
