#!/usr/bin/env python3
"""v3.7c — 무대 배치·라벨 정리 (이름표 한 줄, 대표 위치/높이)."""
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "index.html")


def nfd(s):
    return unicodedata.normalize("NFD", s)


src = open(PATH, encoding="utf-8").read()

# 1) 좌표: 발끝을 조금 더 아래로, 대표는 용어사전 핀을 피해 오른쪽으로
src = re.sub(r"museDesk:\{ x:25, y:88 \}", "museDesk:{ x:25, y:89 }", src)
src = re.sub(r"seconDesk:\{ x:37, y:91 \}", "seconDesk:{ x:37, y:92.5 }", src)
src = re.sub(r"broDesk:\{ x:49, y:88 \}", "broDesk:{ x:49, y:89 }", src)
src = re.sub(r"instinctDesk:\{ x:61, y:91 \}", "instinctDesk:{ x:61, y:92.5 }", src)
src = re.sub(r"ceoSpot:\{ x:73\.5, y:84 \}", "ceoSpot:{ x:77.5, y:87 }", src)
src = re.sub(r'id="ceoDesk" style="--x:73\.5%;--y:84%"', 'id="ceoDesk" style="--x:77.5%;--y:87%"', src)

# 2) 라벨: 이름 + 상태/큐 한 줄
CSS = """
/* v3.7c 라벨·배치 */
.w-plate{flex-direction:row;align-items:center;justify-content:center;gap:4px;margin-bottom:5px}
.w-cue{font-size:8.5px;padding:2px 7px}
.ceo .ceo-plate{flex-direction:row;flex-wrap:wrap;justify-content:center;gap:3px 5px;max-width:214px;padding:4px 9px 5px}
.ceo .ceo-plate b{font-size:12px}
.ceo .ceo-k{font-size:7.5px;letter-spacing:.06em}
.ceo .ceo-st{font-size:9px}
.ceo .ceo-cue{font-size:8px;margin-top:0}
"""
src = src.replace("</style>", nfd(CSS) + "\n</style>", 1)

open(PATH, "w", encoding="utf-8").write(src)
print("ok", len(src))
