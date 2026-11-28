#!/usr/bin/env python3
"""Park Lab AI Office v3.7 — 전신 골프웨어 모델 컷아웃 생성기.

생성 원본은 '크로마키 파랑' 배경(_gen/b_*.png). 파랑 우세량(dkey = B - max(R,G))으로
누끼를 따고, 가장자리 파랑 번짐(despill)을 걷어낸다. 640px 전신 webp(투명)와
같은 원본에서 뜬 얼굴 아바타 256px 을 함께 만든다.

usage: python3 make_full_body.py
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "_gen")
OUT = os.path.join(HERE, "..", "assets")
FULL_DIR = os.path.join(OUT, "full")

WORK_H = 980
BODY_H = 640
HEAD_PX = 256
K = np.ones((3, 3), np.uint8)

JOBS = [
    ("b_ceo.png", "ceo"),
    ("b_secon.png", "secon"),
    ("b_bro.png", "bro"),
    ("b_instinct.png", "instinct"),
    ("b_muse.png", "muse"),
    ("b_jjini.png", "c1"),
    ("b_jju.png", "c2"),
    ("b_sunny.png", "c3"),
]


def matte(path):
    im = Image.open(path).convert("RGB")
    w0, h0 = im.size
    s = WORK_H / h0
    im = im.resize((max(1, int(w0 * s)), WORK_H), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    h, w, _ = a.shape
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

    dkey = b - np.maximum(r, g)
    border = np.concatenate([dkey[0], dkey[-1], dkey[:, 0], dkey[:, -1]])
    bgd = float(np.median(border))
    t0 = bgd * 0.22
    t1 = bgd * 0.72 if bgd * 0.72 > t0 + 12 else t0 + 12
    alpha = 1.0 - np.clip((dkey - t0) / (t1 - t0), 0, 1)   # 파랑(키컬러)=0, 인물=1

    binm = (alpha > 0.5).astype(np.uint8)
    binm = cv2.morphologyEx(binm, cv2.MORPH_OPEN, K)
    binm = cv2.morphologyEx(binm, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    # 작은 구멍만 메운다 (다리 사이·팔 사이 배경은 살린다)
    inv = (binm == 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    limit = h * w * 0.0004
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < limit and st[i, cv2.CC_STAT_LEFT] > 1 \
                and st[i, cv2.CC_STAT_TOP] > 1 \
                and st[i, cv2.CC_STAT_LEFT] + st[i, cv2.CC_STAT_WIDTH] < w - 1 \
                and st[i, cv2.CC_STAT_TOP] + st[i, cv2.CC_STAT_HEIGHT] < h - 1:
            binm[lab == i] = 1
    # 큰 덩어리만 (알파벳·노이즈 제거)
    n, lab, st, _ = cv2.connectedComponentsWithStats(binm, connectivity=8)
    keep = np.zeros_like(binm)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= binm.sum() * 0.004:
            keep[lab == i] = 1
    binm = keep
    binm = cv2.dilate(binm, np.ones((5, 5), np.uint8))   # 실루엣 안쪽 파란 잔여는 아래 알파가 지운다

    # 최종 알파: 마스크 안이라도 파란 픽셀(잔여 배경)은 알파 0
    al = np.where(binm > 0, alpha, 0.0).astype(np.float32)
    al_im = Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    al = np.asarray(al_im).astype(np.float32) / 255.0

    # despill: 파랑 번짐 제거 (가장자리 강하게, 내부 약하게)
    excess = np.clip(dkey, 0, None)
    f = np.where(al < 0.97, 0.85, 0.35).astype(np.float32)
    a[:, :, 2] = b - excess * f

    rgba = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    rgba.putalpha(Image.fromarray((np.clip(al, 0, 1) * 255).astype(np.uint8)))
    return rgba


def body_crop(rgba):
    al = np.asarray(rgba.getchannel("A"))
    ys, xs = np.where(al > 20)
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    pad = int((x1 - x0) * 0.05)
    crop = rgba.crop((max(0, x0 - pad), max(0, y0 - pad), min(rgba.width, x1 + pad), y1))
    cw, ch = crop.size
    scale = min(1.0, BODY_H / ch)
    return crop.resize((max(1, int(cw * scale)), max(1, int(ch * scale))), Image.LANCZOS)


def head_crop(rgba):
    im = rgba
    w, h = im.size
    al = np.asarray(im.getchannel("A"))
    rgb = np.asarray(im.convert("RGB"))
    ys, xs = np.where(al > 20)
    top = int(ys.min())
    body_h = int(ys.max()) - top
    band = slice(top, top + int(body_h * 0.22))
    r = rgb[band, :, 0].astype(np.int16)
    g = rgb[band, :, 1].astype(np.int16)
    b = rgb[band, :, 2].astype(np.int16)
    skin = (r > 110) & (r - g > 16) & (r - b > 26) & (g > b - 12) & (al[band] > 200)
    sy, sx = np.where(skin)
    if len(sx) > 50:
        cx = int(np.median(sx))
        cy = int(np.median(sy)) + top
    else:
        bandm = al[top:top + int(body_h * 0.10)]
        bx = np.where(bandm > 20)[1]
        cx = int(np.median(bx)) if len(bx) else w // 2
        cy = top + int(body_h * 0.07)
    side = int(body_h * 0.27)
    x0 = max(0, min(w - side, cx - side // 2))
    y0 = max(0, min(h - side, cy - int(side * 0.44)))
    crop = im.crop((x0, y0, x0 + side, y0 + side))
    crop = crop.resize((HEAD_PX, HEAD_PX), Image.LANCZOS)
    return crop.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=3))


COLORS = {
    "ceo": "#ffd166", "secon": "#37e0c6", "bro": "#5aa2ff", "instinct": "#8b8cff",
    "muse": "#ff8ac2", "c1": "#7fb0ff", "c2": "#37e0c6", "c3": "#b18cff",
}


def glow_bg(hexcolor, size=HEAD_PX):
    c = np.array([int(hexcolor[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.float32)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    cx, cy = size / 2.0, size * 0.40
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (size * 0.72)
    w = np.clip(1.0 - d, 0, 1) ** 1.5
    base = np.array([9, 14, 24], dtype=np.float32)
    out = base * (1 - w[..., None] * 0.86) + c * (w[..., None] * 0.86)
    return Image.fromarray(out.astype(np.uint8)).convert("RGBA")


def main():
    os.makedirs(FULL_DIR, exist_ok=True)
    for src, key in JOBS:
        rgba = matte(os.path.join(SRC, src))
        body = body_crop(rgba)
        p = os.path.join(FULL_DIR, key + ".webp")
        body.save(p, "WEBP", quality=88, method=6)
        hp = os.path.join(OUT, "avatar_" + key + "_v37.webp")
        av = glow_bg(COLORS.get(key, "#5aa2ff"))
        av.alpha_composite(head_crop(rgba))
        av.save(hp, "WEBP", quality=90, method=6)
        print(f"{key:9s} {body.size[0]}x{body.size[1]} {os.path.getsize(p)//1024}KB"
              f" · avatar {os.path.getsize(hp)//1024}KB")


if __name__ == "__main__":
    main()
