#!/usr/bin/env python3
"""v3.7d — 아이들 산책 겹침 방지 · 깊이 정렬 · 대표 위치."""
import math
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "index.html")


def nfd(s):
    return unicodedata.normalize("NFD", s)


src = open(PATH, encoding="utf-8").read()

# 대표 위치: 용어사전·골프랩 핀 사이
src = re.sub(r'id="ceoDesk" style="--x:77\.5%;--y:87%"', 'id="ceoDesk" style="--x:80%;--y:87.5%"', src)
src = re.sub(r"ceoSpot:\{ x:77\.5, y:87 \}", "ceoSpot:{ x:80, y:87.5 }", src)

# 산책: 다른 캐릭터와 겹치지 않게 + 깊이(z) 정렬
OLD = """    var base = SPOT[DESK_OF[id]];
    var dx = (Math.random() < .5 ? -1 : 1) * (2.5 + Math.random() * 4.5);
    var tx = Math.max(11, Math.min(87, base.x + dx));
    var ty = Math.max(81, Math.min(93, base.y + (Math.random() - .5) * 3));
    walkTo(id, tx, ty, 3400 + Math.round(Math.random() * 900));"""
NEW = """    var base = SPOT[DESK_OF[id]];
    var tx = 0, ty = 0, ok = false;
    for (var tryN = 0; tryN < 6 && !ok; tryN++){
      var dx = (Math.random() < .5 ? -1 : 1) * (2.5 + Math.random() * 4.5);
      tx = Math.max(11, Math.min(86, base.x + dx));
      ty = Math.max(82, Math.min(93, base.y + (Math.random() - .5) * 3));
      ok = true;
      for (var j = 0; j < WALKER_IDS.length; j++){
        var o = WALKER_IDS[j];
        if (o === id || !pos[o]) continue;
        if (Math.abs(pos[o].x - tx) < 8.5 && Math.abs(pos[o].y - ty) < 7){ ok = false; break; }
      }
    }
    if (!ok) return;
    walkTo(id, tx, ty, 3400 + Math.round(Math.random() * 900));"""
assert OLD in src
src = src.replace(OLD, NEW)

# walkTo / moveTo 에서 y 기준 깊이 정렬
src = src.replace("""  pos[id].x = x; pos[id].y = y; pos[id].t = Date.now();
  if (ms > 0){
    w.classList.add("walking");""",
"""  pos[id].x = x; pos[id].y = y; pos[id].t = Date.now();
  w.style.zIndex = Math.round(y);
  if (ms > 0){
    w.classList.add("walking");""")

src = src.replace("""  pos[id].x = tx; pos[id].y = ty; pos[id].t = Date.now();
  w.classList.toggle("has-doc", !!doc);""",
"""  pos[id].x = tx; pos[id].y = ty; pos[id].t = Date.now();
  w.style.zIndex = Math.round(ty);
  w.classList.toggle("has-doc", !!doc);""")

# buildWalkers 초기 z-index
src = src.replace("""    w.style.setProperty("--wd", "0ms");
    w.addEventListener("click", function(){ select(id); showTalk(id); });""",
"""    w.style.setProperty("--wd", "0ms");
    w.style.zIndex = Math.round(s.y);
    w.addEventListener("click", function(){ select(id); showTalk(id); });""")

CSS = """
/* v3.7d */
.ceo .ceo-plate{max-width:186px}
"""
src = src.replace("</style>", nfd(CSS) + "\n</style>", 1)

open(PATH, "w", encoding="utf-8").write(src)
print("ok")
