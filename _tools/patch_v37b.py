#!/usr/bin/env python3
"""v3.7 후속 수정 — 상태 문자열 정규화(NFC/NFD 혼재) + 크기·표시 미세조정."""
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "index.html")


def nfd(s):
    return unicodedata.normalize("NFD", s)


src = open(PATH, encoding="utf-8").read()

NEW_SETSTATUS = """function setStatus(id, text){
  var el2, cls = "idle";
  var t = norm(text);
  busy[id] = IDLE_TXT.indexOf(t) === -1;
  if (id === "ceo"){
    el2 = document.getElementById("ceoSt");
    if (t.indexOf(K.done) >= 0 || t.slice(-2) === K.appr) cls = "ok";
    else if (t.indexOf(K.idle) >= 0 || t.indexOf(K.wait) >= 0) cls = "busy";
    if (!el2) return;
    el2.textContent = text; el2.className = "ceo-st " + cls; syncGolf(); return;
  }
  var w = walkerEls[id]; if (!w) return;
  if (t.indexOf(K.done) >= 0 || t.indexOf(K.pass) >= 0 || t.indexOf("PASS") >= 0 || t.indexOf(K.upload) >= 0) cls = "ok";
  else if (t === K.idle) cls = "idle";
  else cls = "busy";
  var s = w.querySelector(".w-st");
  s.textContent = text; s.className = "w-st " + cls;
  syncGolf();
}
"""

m = re.search(r"function setStatus\(id, text\)\{.*?\n\}\n", src, re.S)
assert m, "setStatus not found"
src = src[:m.start()] + nfd(NEW_SETSTATUS) + src[m.end():]

HELPERS = """
/* 한글 비교용 — 파일 안에서 NFC/NFD가 섞여 있어 항상 NFC로 맞춘다 */
function norm(s){ return (s == null ? "" : String(s)).normalize("NFC"); }
var K = { idle:norm("대기"), done:norm("완료"), pass:norm("통과"), upload:norm("게시"),
          wait:norm("상신"), appr:norm("승인") };
var IDLE_TXT = [K.idle, K.done, norm("승인 완료"), norm("수정 완료")];
"""
src = src.replace(nfd("/* =========================================================\n   6-b. 아이들 골프"),
                  nfd(HELPERS) + nfd("\n/* =========================================================\n   6-b. 아이들 골프"), 1)

EXTRA_CSS = """
/* v3.7.1 미세조정 */
.walker{--fh:clamp(82px,13.1vw,186px)}
.ceo{--fhc:clamp(88px,14.1vw,200px)}
.ceo.golfing .ceo-st{display:none}
.ceo.golfing .ceo-plate{border-color:rgba(74,222,128,.55);box-shadow:0 14px 30px -18px #000,0 0 22px -12px rgba(74,222,128,.8)}
"""
src = src.replace("</style>", nfd(EXTRA_CSS) + "\n</style>", 1)

open(PATH, "w", encoding="utf-8").write(src)
print("patched", len(src))
