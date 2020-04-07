#!/usr/bin/env python3
from argparse import ArgumentParser
from math import sqrt

from PIL import Image, ImageDraw


def _sgn(x):
    if x < 0:
        return -1
    if x > 0:
        return 1
    return 0


def _make_triangle_mask(triangle) -> Image:
    (ax, ay), (bx, by), (cx, cy) = triangle
    min_x = min(ax, bx, cx)
    ax -= min_x
    bx -= min_x
    cx -= min_x
    min_y = min(ay, by, cy)
    ay -= min_y
    by -= min_y
    cy -= min_y
    max_x = max(ax, bx, cx)
    max_y = max(ay, by, cy)
    img = Image.new('1', (max_x + 1, max_y + 1), 0)
    draw = ImageDraw.Draw(img)
    draw.polygon((ax, ay, bx, by, cx, cy, ax, ay), fill=1, outline=1)
    return img


def _get_triangle_top_left(triangle):
    (ax, ay), (bx, by), (cx, cy) = triangle
    return min(ax, bx, cx), min(ay, by, cy)


def _get_image_slice_rect(img, index):
    assert 0 <= index < 6
    # Get x-bounds
    if index % 3 == 0:
        left = img.width // 4
        right = img.width * 3 // 4
    elif index < 3:
        left = img.width // 2
        right = img.width
    else:
        left = 0
        right = img.width // 2
    # Get y-bounds
    if index < 2 or index == 5:
        top = 0
        bottom = img.height // 2
    else:
        top = img.height // 2
        bottom = img.height
    return left, top, right, bottom


class Hexaflex:
    def __init__(self, size=1024, gap=16, line_width=16, line_fill=(0, 0, 0, 255), both_sides=True, six_sided=True,
                 texture_gap=False, textures=None):
        num_textures = 6 if six_sided else 3
        if textures is None:
            textures = [None] * num_textures
        elif len(textures) != num_textures:
            textures += [None] * (num_textures - len(textures))
        self.size = size
        self.gap = gap
        self.line_width = line_width
        self.line_fill = line_fill
        self.double_sided = both_sides
        self.six_sided = six_sided
        self.texture_gap = texture_gap
        self.textures = textures

    @property
    def num_triangles(self):
        return 19 if self.six_sided else 10

    @property
    def image_width(self):
        return self.width + self.line_width

    @property
    def image_height(self):
        tri = self.num_triangles
        return int(self.size * (tri + 1) / 2 + self.line_width * (tri - 1))

    @property
    def triangle_width(self):
        return int(sqrt(3) / 2 * self.size)

    @property
    def width(self):
        width = self.triangle_width
        if self.double_sided:
            width *= 2
        return int(width)

    def _get_triangles(self, left_x: int, right_x: int, shrink=False):
        if shrink:
            if left_x < right_x:
                left_x += int(self.gap * sqrt(3) - self.gap / 2)
                right_x -= self.gap // 2
            else:
                left_x -= int(self.gap * sqrt(3) - self.gap / 2)
                right_x += self.gap // 2
            dy = self.gap
            box = 0, 0, abs(right_x - left_x), self.size
        else:
            diff = int((sqrt(3) - 1) / 2 * self.gap)
            if left_x < right_x:
                left_x += diff
                right_x += diff
            else:
                left_x -= diff
                right_x -= diff
            box = diff, 0, abs(right_x - left_x) - diff, self.size
            dy = 0

        right = self.line_width // 2
        left = right + self.size // 2
        for i in range(self.num_triangles):
            if left < right:
                yield ((left_x, left + dy), (right_x, right), (left_x, left + self.size - dy)), box
                left += self.size
            else:
                yield ((right_x, right + dy), (left_x, left), (right_x, right + self.size - dy)), box
                right += self.size

    def _get_triangles_left(self, shrink=0):
        left_x = self.line_width // 2
        right_x = left_x + self.triangle_width
        return self._get_triangles(left_x, right_x, shrink)

    def _get_triangles_right(self, shrink=0):
        if not self.double_sided:
            return
        left_x = self.line_width // 2 + 2 * self.triangle_width
        right_x = left_x - self.triangle_width
        return self._get_triangles(left_x, right_x, shrink)

    @property
    def shrunk_triangles(self):
        yield from self._get_triangles_left(shrink=self.gap)
        yield from self._get_triangles_right(shrink=self.gap)

    @property
    def triangles(self):
        if self.texture_gap:
            yield from self.shrunk_triangles
        else:
            yield from self._get_triangles_left()
            yield from self._get_triangles_right()

    @property
    def patterns(self):
        if self.six_sided:
            yield from [
                (1, 5, 5),
                (2, 5, 4),
                (0, 0, 0),
                (1, 0, 5),
                (2, 0, 0),
                (0, 1, 0),
                (1, 1, 1),
                (2, 1, 0),
                (0, 2, 2),
                (1, 2, 1),
                (2, 2, 2),
                (0, 3, 2),
                (1, 3, 3),
                (2, 3, 2),
                (0, 4, 4),
                (1, 4, 3),
                (2, 4, 4),
                (0, 5, 4),
                (None, None, None),
            ]
            yield from [
                (None, None, None),
                (5, 5, 3),
                (4, 5, 4),
                (4, 0, 4),
                (3, 0, 5),
                (3, 1, 5),
                (5, 0, 5),
                (5, 1, 5),
                (4, 1, 0),
                (4, 2, 0),
                (3, 2, 1),
                (3, 3, 1),
                (5, 2, 1),
                (5, 3, 1),
                (4, 3, 2),
                (4, 4, 2),
                (3, 4, 3),
                (3, 5, 3),
                (5, 4, 3),
            ]
        else:
            yield from [
                (2, 5, 1),
                (1, 5, 0),
                (1, 4, 0),
                (0, 4, 5),
                (0, 3, 5),
                (2, 2, 3),
                (2, 1, 3),
                (1, 1, 2),
                (1, 0, 2),
                (0, 0, 1),
            ]
            yield from [
                (None, None, None),
                (0, 5, 1),
                (2, 4, 5),
                (2, 3, 5),
                (1, 3, 4),
                (1, 2, 4),
                (0, 2, 3),
                (0, 1, 3),
                (2, 0, 1),
                (None, None, None),
            ]

    def to_image(self):
        img = Image.new('RGBA', (self.image_width, self.image_height), (0, 0, 0, 0))
        masks = None
        draw = ImageDraw.Draw(img)
        line_opts = dict(width=self.line_width, fill=self.line_fill)
        for (tri, box), (tex_index, tex_slice, tex_rot) in zip(self.triangles, self.patterns):
            if tex_index is not None and self.textures[tex_index] is not None:
                if masks is None:
                    mask = _make_triangle_mask(tri)
                    # Assert that this is a right-pointing triangle
                    assert tri[0][0] == tri[2][0]
                    masks = [
                        mask.transpose(Image.ROTATE_90),
                        mask.transpose(Image.ROTATE_270),
                    ]
                mask = masks[tex_slice % 2]
                rect = _get_image_slice_rect(self.textures[tex_index], tex_slice)
                slice = self.textures[tex_index].resize(mask.size, box=rect)
                slice.putalpha(mask)
                slice = slice.rotate(30 + tex_rot * 60, expand=True)
                slice = slice.crop(slice.getbbox())
                slice_mask = _make_triangle_mask(tri)
                slice = slice.resize(slice_mask.size)
                # Take only the part of slice_mask inside box
                slice_mask_2 = Image.new('1', slice_mask.size)
                slice_mask_2.paste(slice_mask.crop(box), box=box)
                img.paste(slice, box=_get_triangle_top_left(tri), mask=slice_mask_2)
        if self.line_width > 0:
            for (tri, _) in self.shrunk_triangles:
                draw.line((*tri, tri[0]), **line_opts)
        return img


def main():
    parser = ArgumentParser(description='Create a hexaflexagon template')
    parser.add_argument('-s', '--size', dest='size', action='store', type=int, default=1024,
                        help='(pixels) triangle side length (default: 1024)')
    parser.add_argument('-g', '--gap', dest='gap', action='store', type=int, default=32,
                        help='(pixels) gap between triangles (default: 32)')
    parser.add_argument('-l', '--line-width', dest='line_width', action='store', type=int, default=16,
                        help='(pixels) thickness of lines (default: 16)')
    parser.add_argument('-x', '--hexa', dest='six_sided', action='store_true',
                        help='use hexahexaflexagon (6 sides) (default: trihexaflexagon (3 sides))')
    parser.add_argument('-o', '--output', dest='output', action='store', default='hexaflex.png',
                        help='output filename (default: hexaflex.png)')
    parser.add_argument('--texture-gap', dest='texture_gap', action='store_true',
                        help='also apply gap to textures (default: off)')
    parser.add_argument('texture', type=str, nargs='*',
                        help='image files to use as textures (default: none)')
    args = parser.parse_args()
    Hexaflex(
        size=args.size,
        gap=args.gap,
        line_width=args.line_width,
        six_sided=args.six_sided,
        texture_gap=args.texture_gap,
        textures=list(map(Image.open, args.texture)),
    ).to_image().save(args.output)


if __name__ == '__main__':
    main()
