#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs'
OUT.mkdir(exist_ok=True)

PAGES = {
    75: ROOT / 'keyser bitcoin -3_1.jpg',
    76: ROOT / 'keyser bitcoin -4_1.jpg',
    77: ROOT / 'keyser bitcoin -5_1.jpg',
    78: ROOT / 'keyser bitcoin -6_1.jpg',
    79: ROOT / 'keyser bitcoin -7_1.jpg',
}


def fit(img, size):
    return img.convert('RGB').resize(size)


def overlay_pair(left_page, right_page):
    base = Image.open(PAGES[left_page]).convert('RGB')
    reflected = Image.open(PAGES[right_page]).convert('RGB').transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    reflected = fit(reflected, base.size)

    blend = Image.blend(base, reflected, 0.45)
    diff = ImageChops.difference(base, reflected)
    diff = ImageEnhance.Contrast(diff).enhance(2.0)

    blend.save(OUT / f'overlay_{left_page}_{right_page}_hflip.png')
    diff.save(OUT / f'diff_{left_page}_{right_page}_hflip.png')


def main():
    for pair in [(75, 79), (76, 78), (75, 78), (76, 79)]:
        overlay_pair(*pair)
        print(f'wrote overlay/diff for {pair[0]} {pair[1]}')


if __name__ == '__main__':
    main()
