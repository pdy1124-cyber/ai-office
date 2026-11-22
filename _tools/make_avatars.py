#!/usr/bin/env python3
"""Park Lab AI Office v2.1 — 캐릭터 아바타 생성기.

1) 생성·보관 이미지에서 배경을 떼어낸다(테두리에서 이어진 배경만 + 작은 조각·내부구멍 정리)
2) 브랜드 색조의 원형 배경 위에 합성해 경량 webp 아바타를 만든다.

외부 CDN 없음 — 결과물은 assets/ 로컬 파일만 사용한다.
usage: python3 make_avatars.py
"""
import os
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "_src")
OUT = os.path.join(HERE, "..", "assets")
WORK = 640      # 배경 제거 작업 해상도
FINAL = 256     # 최종 아바타 해상도


def load_small(path, size=WORK):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = size / max(w, h)
    if s < 1:
        im = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
    return im


def _grow(seed, allowed, h, w):
    """seed에서 allowed 영역만 4방향으로 확장."""
    seen = seed.copy()
    dq = deque(zip(*np.where(seed)))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and allowed[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                dq.append((ny, nx))
    return seen


def cutout(path, tol=26.0, eat_shadow=False, floor_kill=False, keep_holes=True, key_all=False):
    im = load_small(path)
    a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]], axis=0)
    bgcol = np.median(border, axis=0)
    dist = np.sqrt(((a - bgcol.reshape(1, 1, 3)) ** 2).sum(axis=2))
    allowed = dist <= tol
    if eat_shadow:
        # 회색 그림자·반짝임도 배경으로 흡수 (검은 눈은 mean 가드로 보존)
        mx = a.max(axis=2)
        mn = a.min(axis=2)
        gray = ((mx - mn) < 22) & (a.mean(axis=2) > 95)
        allowed = allowed | gray
    if key_all:
        # 배경과 같은 색은 위치와 무관하게 지운다 (ㅂ 카운터 같은 내부 구멍)
        bg = allowed.copy()
    else:
        seed = np.zeros((h, w), dtype=bool)
        seed[0, :] = allowed[0, :]
        seed[-1, :] = allowed[-1, :]
        seed[:, 0] = allowed[:, 0]
        seed[:, -1] = allowed[:, -1]
        bg = _grow(seed, allowed, h, w)

    fg = ~bg
    if floor_kill:
        ys, xs = np.where(fg)
        if len(ys):
            y0, y1 = ys.min(), ys.max()
            band = np.zeros_like(fg)
            band[int(y1 - 0.22 * (y1 - y0)):, :] = True
            fg &= ~(band & (dist < 45))
    # 가장 큰 덩어리만 유지 (떠 있는 반짝임·노이즈 제거)
    lab = np.zeros((h, w), dtype=np.int32)
    best, best_n, cur = 0, 0, 0
    for y in range(h):
        row = fg[y]
        x = 0
        while x < w:
            if row[x] and lab[y, x] == 0:
                cur += 1
                mask = _grow(_seed_point(y, x, h, w), fg, h, w)
                lab[mask] = cur
                n = int(mask.sum())
                if n > best_n:
                    best, best_n = cur, n
            x += 1
    fg = (lab == best) if best else fg
    if keep_holes:
        # 내부 구멍 메우기 (눈동자 하이라이트 등 유지)
        outside = _grow(seed_border(~fg, h, w), ~fg, h, w)
        fg = fg | (~fg & ~outside)

    alpha = Image.fromarray((fg * 255).astype(np.uint8))
    alpha = alpha.filter(ImageFilter.MinFilter(3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(1.0))
    rgba = im.convert("RGBA")
    rgba.putalpha(alpha)
    return rgba


def _seed_point(y, x, h, w):
    m = np.zeros((h, w), dtype=bool)
    m[y, x] = True
    return m


def seed_border(mask, h, w):
    m = np.zeros((h, w), dtype=bool)
    m[0, :] = mask[0, :]
    m[-1, :] = mask[-1, :]
    m[:, 0] = mask[:, 0]
    m[:, -1] = mask[:, -1]
    return m


def square_tight(rgba, margin=0.06):
    a = np.asarray(rgba.getchannel("A"))
    ys, xs = np.where(a > 12)
    if len(xs) == 0:
        return rgba
    sub = rgba.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    w, h = sub.size
    side = int(max(w, h) * (1 + margin * 2))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(sub, ((side - w) // 2, (side - h) // 2))
    return canvas


def tint_bg(size, hexcolor):
    c = tuple(int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    base = Image.new("RGB", (size, size), (10, 16, 26))
    glow = Image.new("RGB", (size, size), c)
    mask = Image.new("L", (size, size), 0)
    px = mask.load()
    cx, cy = size / 2, size * 0.42
    r = size * 0.72
    for y in range(size):
        for x in range(size):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / r
            px[x, y] = int(255 * (max(0.0, 1.0 - d) ** 1.5) * 0.85)
    base = Image.composite(glow, base, mask)
    circle = Image.new("L", (size, size), 0)
    ImageDraw.Draw(circle).ellipse((0, 0, size - 1, size - 1), fill=255)
    base.putalpha(circle)
    return base


def compose(subject_rgba, color, out_path, scale=0.94):
    bg = tint_bg(FINAL, color)
    s = int(FINAL * scale)
    sub = subject_rgba.resize((s, s), Image.LANCZOS)
    bg.alpha_composite(sub, ((FINAL - s) // 2, (FINAL - s) // 2))
    bg.save(out_path, "WEBP", quality=90, method=6)
    return out_path


def photo_avatar(path, out_path, box, bright=1.02, contrast=1.04):
    from PIL import ImageEnhance
    im = Image.open(path).convert("RGB").crop(box)
    im = im.resize((FINAL, FINAL), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))
    im = ImageEnhance.Brightness(im).enhance(bright)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    base = im.convert("RGBA")
    circle = Image.new("L", (FINAL, FINAL), 0)
    ImageDraw.Draw(circle).ellipse((0, 0, FINAL - 1, FINAL - 1), fill=255)
    base.putalpha(circle)
    base.save(out_path, "WEBP", quality=90, method=6)
    return out_path


# src, out, brand color, tol, scale, eat_shadow, floor_kill
JOBS = [
    ("gen_bro4.png",        "avatar_bro.webp",      "#5aa2ff", 26, 0.92, True,  True, False, True),
    ("gen_instinct.png",    "avatar_instinct.webp", "#8b8cff", 30, 0.92, True,  True),
    ("gen_dict.png",        "avatar_dict.webp",     "#7fb0ff", 30, 0.92, False, True),
    ("gen_sound.png",       "avatar_sound.webp",    "#b18cff", 30, 0.92, False, True),
    ("gen_ssada.png",       "avatar_ssada.webp",    "#ff8ac2", 30, 0.92, True,  True),
    ("gen_meet2.png",       "avatar_meet.webp",     "#37e0c6", 22, 0.86, False, False),
    ("gen_lounge2.png",     "avatar_lounge.webp",   "#ffc36b", 22, 0.86, False, False),
    ("ppajji_clean_01.png", "avatar_tips.webp",     "#ffd166", 30, 0.92, False, True),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for job in JOBS:
        src, out, color, tol, scale, eat, floor = job[:7]
        holes = job[7] if len(job) > 7 else True
        key_all = job[8] if len(job) > 8 else False
        cut = square_tight(cutout(os.path.join(SRC, src), tol=tol, eat_shadow=eat,
                                  floor_kill=floor, keep_holes=holes, key_all=key_all))
        p = compose(cut, color, os.path.join(OUT, out), scale=scale)
        print(out, os.path.getsize(p) // 1024, "KB")
    golf = photo_avatar(
        os.path.join(HERE, "..", "..", "golflab_models", "profile_square.png"),
        os.path.join(OUT, "avatar_golf.webp"),
        box=(212, 212, 848, 848),
    )
    print("avatar_golf.webp", os.path.getsize(golf) // 1024, "KB")


if __name__ == "__main__":
    main()
