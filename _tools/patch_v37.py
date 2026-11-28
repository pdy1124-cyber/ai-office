#!/usr/bin/env python3
"""ai-office v3.6.1 → v3.7 패치 스크립트.
index.html 은 한글이 NFD로 저장돼 있어 직접 문자열 치환이 어긋난다.
여기서도 NFD로 정규화해 치환한다.
usage: python3 _tools/patch_v37.py
"""
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "index.html")


def nfd(s):
    return unicodedata.normalize("NFD", s)


def rep(src, old, new, count=1):
    o, n = nfd(old), nfd(new)
    if old not in src and o not in src:
        raise SystemExit("NOT FOUND: " + old[:90])
    if o in src:
        return src.replace(o, n, count)
    return src.replace(old, new, count)


def resub(src, pattern, new, flags=0):
    n = nfd(new)
    out, k = re.subn(pattern, lambda m: n, src, count=1, flags=flags)
    if k == 0:
        raise SystemExit("REGEX NOT FOUND: " + pattern[:80])
    return out


src = open(PATH, encoding="utf-8").read()

# ────────────────────────────── 1. head / meta
src = resub(src, r"<title>.*?</title>",
            "<title>Park Lab AI Office v3.7 · 전신 골프모델 라운딩 · 보고 없으면 스윙 연습</title>")
src = resub(src, r'<meta name="description" content="[^"]*">',
            '<meta name="description" content="Park Lab AI 실사 오피스 v3.7 — 전신 골프웨어 모델로 세운 대표·쎄컨·빡이·인스팅트·뮤즈가 페어웨이에서 스윙 연습하며, 오더·보고가 오면 스윙을 멈추고 Google Drive 결재라인을 도는 야외 골프장 대시보드">')
src = resub(src, r'<meta property="og:title" content="[^"]*">',
            '<meta property="og:title" content="Park Lab AI Office v3.7 · 전신 골프모델 라운딩">')
src = resub(src, r'<meta property="og:description" content="[^"]*">',
            '<meta property="og:description" content="보고 없을 땐 골프 ㅋㅋ — 전신 골프웨어 모델 스윙 모션 + 대표 최종 승인 결재라인 (v3.7)">')

src = rep(src,
          '<link rel="preload" as="image" href="assets/avatar_ceo_v36.webp" type="image/webp">\n'
          '<link rel="preload" as="image" href="assets/avatar_instinct_v36.webp" type="image/webp">\n'
          '<link rel="preload" as="image" href="assets/avatar_muse_v36.webp" type="image/webp">',
          '<link rel="preload" as="image" href="assets/full/ceo.webp" type="image/webp">\n'
          '<link rel="preload" as="image" href="assets/full/secon.webp" type="image/webp">\n'
          '<link rel="preload" as="image" href="assets/full/bro.webp" type="image/webp">\n'
          '<link rel="preload" as="image" href="assets/full/instinct.webp" type="image/webp">\n'
          '<link rel="preload" as="image" href="assets/full/muse.webp" type="image/webp">')

# ────────────────────────────── 2. CSS — v3.7 블록
CSS = """
/* ══════════════════════════════════════════════════════════
   v3.7 · 전신 골프웨어 모델 + 아이들 골프 스윙
   (기존 로직·클래스는 그대로 두고 무대 위 캐릭터만 전신으로 교체)
   ══════════════════════════════════════════════════════════ */
.walker{--fh:clamp(78px,12.4vw,168px);transform:translate(-50%,-100%)}
.ceo{--fhc:clamp(84px,13.4vw,182px)}
.w-body{gap:2px}
.w-plate{display:flex;flex-direction:column;align-items:center;gap:3px;margin-bottom:4px;position:relative;z-index:3}
.w-fig{position:relative;height:var(--fh);display:flex;align-items:flex-end;justify-content:center;transform-origin:50% 100%}
.w-full{position:relative;z-index:2;height:100%;width:auto;max-width:none;display:block;transform-origin:50% 100%;
  filter:drop-shadow(0 8px 12px rgba(0,0,0,.42)) saturate(1.03) contrast(1.02);will-change:transform}
.w-fig .w-shadow{position:absolute;left:50%;bottom:-4px;width:70%;height:14px;margin-left:0;transform:translateX(-50%);
  border-radius:50%;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,.6),rgba(0,0,0,.26) 55%,rgba(0,0,0,0) 74%);
  filter:blur(2.5px);z-index:0}
.w-fig .w-doc{right:-6px;top:10%}

/* 골프 상태 큐 — 보고 없을 때 */
.w-cue{display:none;font-size:9px;font-weight:750;white-space:nowrap;padding:2px 8px;border-radius:999px;letter-spacing:0;
  color:#cdf9d6;background:rgba(9,30,18,.86);border:1px solid rgba(74,222,128,.5);box-shadow:0 6px 14px -8px #000}
.walker.golfing .w-cue,.ceo.golfing .ceo-cue{display:inline-block}
.walker.golfing .w-st{display:none}
.walker.golfing .w-name{border-color:rgba(134,239,172,.6);box-shadow:0 6px 14px -8px #000,0 0 14px -6px rgba(74,222,128,.8)}

/* 걷기 — 전신 스트라이드 */
.walker.walking .w-body{animation:none}
.walker.walking .w-fig{animation:strideBob .62s ease-in-out infinite}
@keyframes strideBob{0%,100%{transform:translateY(0) rotate(-.9deg)}25%{transform:translateY(-3px) rotate(.7deg)}50%{transform:translateY(-1px) rotate(.9deg)}75%{transform:translateY(-3px) rotate(-.6deg)}}

/* 아이들 골프 스윙 */
.walker.golfing .w-full{animation:golfSwing 5.6s cubic-bezier(.37,.03,.28,1) infinite}
@keyframes golfSwing{
  0%,34%,100%{transform:rotate(0deg) translateY(0)}
  40%{transform:rotate(-2.2deg) translateY(1px)}
  46%{transform:rotate(-6.4deg) translateY(1px) scaleX(.985)}
  51%{transform:rotate(4.6deg) translateY(-2px) scaleX(.975)}
  57%{transform:rotate(6.2deg) translateY(0) scaleX(.98)}
  64%{transform:rotate(1.4deg) translateY(0)}
  72%{transform:rotate(-.8deg)}
}
.w-arc{position:absolute;left:50%;bottom:2%;width:118%;height:58%;transform:translateX(-50%) rotate(-60deg);opacity:0;
  border-radius:50%;border:2px solid transparent;border-top-color:rgba(255,255,255,.75);z-index:1;pointer-events:none}
.walker.golfing .w-arc{animation:swingArc 5.6s ease-out infinite}
@keyframes swingArc{
  0%,42%{opacity:0;transform:translateX(-50%) rotate(-64deg) scale(.62)}
  50%{opacity:.8;transform:translateX(-50%) rotate(-14deg) scale(.82)}
  58%{opacity:.45;transform:translateX(-50%) rotate(34deg) scale(.96)}
  68%{opacity:0;transform:translateX(-50%) rotate(58deg) scale(1.02)}
  100%{opacity:0}
}
.w-ball,.ceo .ceo-ball{position:absolute;left:64%;bottom:6px;width:5px;height:5px;border-radius:50%;background:#fff;
  box-shadow:0 0 7px rgba(255,255,255,.95);opacity:0;z-index:3;pointer-events:none}
.walker.golfing .w-ball,.ceo.golfing .ceo-ball{animation:ballFly 5.6s ease-out infinite}
@keyframes ballFly{
  0%,54%{opacity:0;transform:translate(0,0) scale(.6)}
  58%{opacity:1;transform:translate(1px,-2px) scale(1)}
  84%{opacity:.85;transform:translate(26px,-52px) scale(.7)}
  96%,100%{opacity:0;transform:translate(40px,-30px) scale(.55)}
}
/* 보고·말풍선이 오면 스윙 정지 */
.walker.talking .w-full,.walker.talking .w-arc,.walker.talking .w-ball,
.ceo.talking .ceo-full,.ceo.talking .ceo-ball{animation-play-state:paused}

/* 회의실 클러스터 */
.walker.compact .w-fig{height:calc(var(--fh) * .78)}
.walker.compact .w-cue{display:none !important}
.walker.compact .w-plate .w-st{display:none}

/* 최종 승인 데스크 = 전신 대표 */
.ceo{transform:translate(-50%,-100%);padding:0;gap:0;background:none;border:0;box-shadow:none;border-radius:0;z-index:6}
.ceo .ceo-plate{display:flex;flex-direction:column;align-items:center;gap:1px;margin-bottom:5px;padding:5px 11px 6px;border-radius:12px;
  background:rgba(10,16,26,.8);border:1px solid rgba(255,209,102,.5);
  box-shadow:0 14px 30px -18px #000,0 0 24px -12px rgba(255,209,102,.85)}
.ceo .ceo-fig{position:relative;height:var(--fhc);display:flex;align-items:flex-end;justify-content:center;transform-origin:50% 100%}
.ceo .ceo-full{position:relative;z-index:2;height:100%;width:auto;display:block;transform-origin:50% 100%;
  filter:drop-shadow(0 9px 14px rgba(0,0,0,.45)) saturate(1.03)}
.ceo .ceo-shadow{position:absolute;left:50%;bottom:-4px;width:72%;height:14px;transform:translateX(-50%);border-radius:50%;
  background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,.62),rgba(0,0,0,.26) 55%,rgba(0,0,0,0) 76%);filter:blur(2.5px);z-index:0}
.ceo .ceo-cue{display:none;font-size:8.5px;font-weight:750;white-space:nowrap;padding:1px 7px;border-radius:999px;margin-top:2px;
  color:#cdf9d6;background:rgba(9,30,18,.9);border:1px solid rgba(74,222,128,.5)}
.ceo.golfing .ceo-full{animation:golfSwing 5.9s cubic-bezier(.37,.03,.28,1) infinite}
.ceo.golfing .ceo-stamp{display:none}
.ceo .ceo-stamp{right:0;top:2%}
.ceo.approved .ceo-plate{border-color:rgba(142,240,184,.75);box-shadow:0 14px 30px -18px #000,0 0 26px -10px rgba(142,240,184,.85)}
.walker.z-front{z-index:8}

/* 접근성·정지 모드 */
@media (prefers-reduced-motion:reduce){
  .walker.golfing .w-full,.ceo.golfing .ceo-full,.walker.golfing .w-arc,.walker.golfing .w-ball,
  .ceo.golfing .ceo-ball,.walker.walking .w-fig{animation:none !important}
}
body.still .w-full,body.still .ceo-full,body.still .w-arc,body.still .w-ball,body.still .ceo-ball,
body.still .walker .w-fig{animation:none !important}
@media (max-width:760px){
  .w-cue{font-size:8px;padding:1px 6px}
  .ceo .ceo-cue{font-size:7.5px}
}
"""
src = src.replace("</style>", nfd(CSS) + "\n</style>", 1)

# ────────────────────────────── 3. 헤더 문구
src = rep(src, "v3.6.1 · 야외 골프장 라운딩</b>", "v3.7 · 전신 골프모델 라운딩</b>")

# ────────────────────────────── 4. 대표 데스크 → 전신 모델
CEO_HTML = """      <button class="ceo" id="ceoDesk" style="--x:73.5%;--y:84%" data-id="ceo" aria-label="대표 최종 승인자 — 승인 데스크">
        <span class="ceo-plate">
          <span class="ceo-k">최종 승인자</span>
          <b>대표</b>
          <span class="ceo-st" id="ceoSt">대기</span>
          <span class="ceo-cue">⛳ 티샷 연습 중</span>
        </span>
        <span class="ceo-fig">
          <span class="ceo-shadow"></span>
          <img class="ceo-full" src="assets/full/ceo.webp" alt="대표 전신 골프 모델" width="265" height="640" decoding="async">
          <span class="ceo-ball"></span>
          <span class="ceo-stamp">승인</span>
        </span>
      </button>"""
src = resub(src, r'      <button class="ceo" id="ceoDesk".*?</button>', CEO_HTML, flags=re.S)

# 장면 힌트
src = rep(src, '<span class="hint">캐릭터·부스를 눌러 상세 보기</span>',
          '<span class="hint">캐릭터·부스를 누르면 상세 · 보고 없을 땐 골프 연습 ㅋㅋ</span>')

# ────────────────────────────── 5. 푸터
src = resub(src, r'<p>v3\.6\.1 .*?</p>',
            "<p>v3.7 전신 골프모델 에디션 — 대표(최종 승인)·총괄 빡이·부총괄 쎄컨과 인스팅트·뮤즈를 전신 골프웨어 모델로 세우고, 보고가 없을 때는 페어웨이를 거닐며 스윙·퍼팅 연습을 합니다. "
            "전신 모델 8인과 아바타는 새로 생성해 크로마키로 배경을 걷어낸 이미지입니다. "
            "모든 이미지는 <code>assets/*.webp</code> 로컬 파일(외부 CDN·추적 0건)입니다. 밝은 화면은 우상단 <b>밝게</b> 버튼으로 전환합니다.</p>",
            flags=re.S)

# ────────────────────────────── 6. PEOPLE 아바타 → v3.7 (전신 crop) + full
AVATAR_MAP = [("ceo", "ceo"), ("secon", "secon"), ("jjongi", "bro"), ("instinct", "instinct"),
              ("muse", "muse"), ("jjini", "c1"), ("jju", "c2"), ("sunny", "c3")]
for oldkey, key in AVATAR_MAP:
    src = rep(src, 'img:"assets/avatar_%s_v36.webp"' % oldkey,
              'img:"assets/avatar_%s_v37.webp", full:"assets/full/%s.webp"' % (key, key))

# ────────────────────────────── 7. SPOT 좌표 (전신 기준)
src = resub(src, r"var SPOT = \{.*?\};",
            """var SPOT = {
  museDesk:{ x:25, y:88 },
  seconDesk:{ x:37, y:91 },
  broDesk:{ x:49, y:88 },
  instinctDesk:{ x:61, y:91 },
  ceoSpot:{ x:73.5, y:84 },
  meet:{ x:43, y:72 },
  ninstinct:{ x:68.5, y:88 },
  nsecon:{ x:31.5, y:88 },
  nbro:{ x:43.5, y:86 }
};""", flags=re.S)

# ────────────────────────────── 8. walkerHTML — 전신 피규어
src = resub(src, r"function walkerHTML\(id\)\{.*?\n\}\n", """function walkerHTML(id){
  var p = PEOPLE[id];
  var wrap = el("div", "walker");
  wrap.setAttribute("data-id", id);
  var body = el("div", "w-body");

  var plate = el("div", "w-plate");
  plate.appendChild(el("span", "w-name", p.name));
  plate.appendChild(el("span", "w-st idle", "대기"));
  plate.appendChild(el("span", "w-cue", "⛳ 티샷 연습 중"));
  body.appendChild(plate);

  var fig = el("div", "w-fig");
  fig.appendChild(el("span", "w-shadow"));
  var im = document.createElement("img");
  im.className = "w-full"; im.src = p.full; im.alt = p.name + " 전신 골프 모델";
  im.width = 260; im.height = 640; im.decoding = "async";
  fig.appendChild(im);
  fig.appendChild(el("span", "w-arc"));
  fig.appendChild(el("span", "w-ball"));
  fig.appendChild(el("span", "w-doc",
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/><path d="M10 12h5M10 16h5"/></svg><b>Drive</b>'));
  body.appendChild(fig);

  var bub = el("div", "w-bubble");
  body.appendChild(bub);
  wrap.appendChild(body);
  wrap.style.setProperty("--c", p.color);
  return wrap;
}
""", flags=re.S)

# ────────────────────────────── 9. buildWalkers — idle 상태 초기화
src = resub(src, r"function buildWalkers\(\)\{.*?\n\}\n", """function buildWalkers(){
  var host = document.getElementById("walkers");
  WALKER_IDS.forEach(function(id){
    var w = walkerHTML(id);
    host.appendChild(w);
    walkerEls[id] = w;
    var s = SPOT[DESK_OF[id]];
    pos[id] = { x:s.x, y:s.y, doc:false, t:Date.now() };
    busy[id] = false;
    w.style.setProperty("--x", s.x + "%");
    w.style.setProperty("--y", s.y + "%");
    w.style.setProperty("--wd", "0ms");
    w.addEventListener("click", function(){ select(id); showTalk(id); });
  });
}
""", flags=re.S)

# ────────────────────────────── 10. setStatus — busy 추적
src = resub(src, r"function setStatus\(id, text\)\{.*?\n\}\n", """function setStatus(id, text){
  var el2, cls = "idle";
  busy[id] = !/^(대기|완료|승인 완료|수정 완료)$/.test(text);
  if (id === "ceo"){
    el2 = document.getElementById("ceoSt");
    if (/완료|승인$/.test(text)) cls = "ok"; else if (/대기|상신/.test(text)) cls = "busy";
    if (!el2) return;
    el2.textContent = text; el2.className = "ceo-st " + cls; syncGolf(); return;
  }
  var w = walkerEls[id]; if (!w) return;
  if (/완료|통과|PASS|게시/.test(text)) cls = "ok"; else if (/대기/.test(text)) cls = "idle"; else cls = "busy";
  var s = w.querySelector(".w-st");
  s.textContent = text; s.className = "w-st " + cls;
  syncGolf();
}
""", flags=re.S)

# ────────────────────────────── 11. moveTo — 위치 시각 기록
src = rep(src, "  pos[id].x = tx; pos[id].y = ty;\n  w.classList.toggle(\"has-doc\", !!doc);",
          "  pos[id].x = tx; pos[id].y = ty; pos[id].t = Date.now();\n  w.classList.toggle(\"has-doc\", !!doc);")

# ────────────────────────────── 12. say — 말할 땐 스윙 정지
src = resub(src, r"function say\(id, text, ms\)\{.*?\n\}\n", """function say(id, text, ms){
  var w = walkerEls[id]; if (!w) return;
  var b = w.querySelector(".w-bubble");
  b.textContent = text;
  b.style.setProperty("--shift","0px");
  b.classList.add("on");
  clampBubble(b);
  w.classList.add("talking");
  syncGolf();
  clearTimeout(b._t);
  b._t = setTimeout(function(){
    b.classList.remove("on");
    w.classList.remove("talking");
    syncGolf();
  }, ms || 3200);
}
""", flags=re.S)

# ────────────────────────────── 13. resetAll — 위치 기록
src = rep(src, "    pos[id] = { x:s.x, y:s.y, doc:false };",
          "    pos[id] = { x:s.x, y:s.y, doc:false, t:Date.now() };")

# ────────────────────────────── 14. 아이들 골프 엔진 추가
IDLE_JS = """
/* =========================================================
   6-b. 아이들 골프 — 보고 없을 땐 스윙·퍼팅 연습 (v3.7)
   ========================================================= */
var busy = { ceo:false, secon:false, bro:false, instinct:false, muse:false };
var GOLF_CUES = ["⛳ 티샷 연습 중", "🏌️ 어프로치 연습", "⛳ 퍼팅 라인 보기", "🏌️ 스윙 템포 점검", "⛳ 라운딩 중"];
var cueIdx = {}, cueTick = 0;

function reduceMotion(){
  return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
}

/* 아이들 상태면 골프 모션 ON, 보고·이동·말풍선이면 OFF */
function syncGolf(){
  WALKER_IDS.forEach(function(id){
    var w = walkerEls[id]; if (!w) return;
    var idle = !busy[id];
    var blocked = w.classList.contains("walking") || w.classList.contains("talking") ||
                  w.classList.contains("compact") || w.classList.contains("has-doc");
    w.classList.toggle("golfing", idle && !blocked && !STILL);
  });
  var c = document.getElementById("ceoDesk");
  if (c) c.classList.toggle("golfing", !busy.ceo && !c.classList.contains("talking") && !STILL);
}

/* 좌표 직접 지정 이동 (아이들 산책용) */
function walkTo(id, x, y, ms){
  var w = walkerEls[id]; if (!w) return;
  if (reduceMotion()) ms = 0;
  w.style.setProperty("--wd", ms + "ms");
  w.style.setProperty("--x", x + "%");
  w.style.setProperty("--y", y + "%");
  pos[id].x = x; pos[id].y = y; pos[id].t = Date.now();
  if (ms > 0){
    w.classList.add("walking");
    clearTimeout(w._wt);
    w._wt = setTimeout(function(){ w.classList.remove("walking"); syncGolf(); }, ms + 80);
  }
}

/* 상태 큐 문구를 천천히 돌려 쓴다 */
function rollCues(){
  WALKER_IDS.forEach(function(id){
    var w = walkerEls[id]; if (!w) return;
    cueIdx[id] = (cueIdx[id] || 0) + 1;
    var c = w.querySelector(".w-cue");
    if (c) c.textContent = GOLF_CUES[cueIdx[id] % GOLF_CUES.length];
  });
}

/* 아이들 산책 — 페어웨이를 조금씩 옮겨 다닌다 */
function strollTick(){
  if (STILL || reduceMotion()) return;
  WALKER_IDS.forEach(function(id){
    if (busy[id]) return;
    var w = walkerEls[id]; if (!w) return;
    if (w.classList.contains("walking") || w.classList.contains("compact")) return;
    if (w.querySelector(".w-bubble").classList.contains("on")) return;
    if (Date.now() - (pos[id].t || 0) < 5200) return;
    if (Math.random() > 0.5) return;
    var base = SPOT[DESK_OF[id]];
    var dx = (Math.random() < .5 ? -1 : 1) * (2.5 + Math.random() * 4.5);
    var tx = Math.max(11, Math.min(87, base.x + dx));
    var ty = Math.max(81, Math.min(93, base.y + (Math.random() - .5) * 3));
    walkTo(id, tx, ty, 3400 + Math.round(Math.random() * 900));
  });
}

function idleTick(){
  cueTick++;
  if (cueTick % 9 === 0) rollCues();
  syncGolf();
}
"""
src = rep(src, "/* =========================================================\n   7. 대시보드 렌더",
          nfd(IDLE_JS) + "\n/* =========================================================\n   7. 대시보드 렌더")

# ────────────────────────────── 15. 부팅 — STILL 처리 + 인터벌
src = resub(src, r"if \(STILL\)\{\n  moveTo\(\"bro\",\"meet\"\);", "if (STILL){\n  document.body.classList.add(\"still\");\n  moveTo(\"bro\",\"meet\");")
src = rep(src, "} else {\n  setTimeout(function(){ runStep(0); }, 900);\n}",
          "} else {\n  setTimeout(function(){ runStep(0); }, 900);\n  setInterval(idleTick, 1500);\n  setInterval(strollTick, 6500);\n}")

# ────────────────────────────── 16. 데이터 — 스냅샷·오늘 처리
src = rep(src, 'stamp: "2026-11-29 00:30"', 'stamp: "2026-11-29 01:05"')
src = rep(src, '{ t:"ai-office v3.6 골프장 라운딩 제작", d:"배경 + 8인 아바타 새 생성 · GitHub Pages 배포" }',
          '{ t:"ai-office v3.7 전신 골프모델 · 스윙 모션", d:"전신 8인 크로마키 컷아웃 · 아이들 스윙/퍼팅 연습 · 보고 오면 정지" }')

open(PATH, "w", encoding="utf-8").write(src)
print("patched", len(src), "bytes")
