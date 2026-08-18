# GitHub 프로필 README 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `World525` GitHub 프로필에 표시될 README와, 그 안에서 재생될 애니메이션 SVG 6개를 만든다.

**Architecture:** GitHub은 README의 `style` 속성과 `<style>`·`<script>` 태그를 제거하므로 HTML/CSS 애니메이션이 불가능하다. 대신 **저장소에 커밋한 SVG 파일**을 상대경로로 참조하면 내부 SMIL 애니메이션이 그대로 재생된다. 움직이는 요소 7곳 중 6곳을 이 방식으로 자체 제작하고, 외부 서비스는 방문자 카운터와 푸터 웨이브 2개만 쓴다.

**Tech Stack:** SVG 1.1 + SMIL(`<animate>`, `<animateTransform>`), GitHub Flavored Markdown, git. 빌드 도구·패키지 매니저·테스트 프레임워크 없음. 검증은 `bash` + `python`(표준 라이브러리 `xml.dom.minidom`) + `curl`로 수행한다.

**설계 근거:** [2026-08-18-github-profile-readme-design.md](../specs/2026-08-18-github-profile-readme-design.md)

---

## 사전 확인

이 계획은 아래를 전제한다. 다르면 멈추고 보고할 것.

- 작업 디렉터리: `C:\Users\world\Desktop\github꾸미기`
- 이미 git 저장소이며 브랜치는 `main`, 커밋 2개(`de54492`, `f3fa727`) 존재
- `.gitignore`에 `.superpowers/`가 이미 들어 있음
- 스크래치패드: `C:\Users\world\AppData\Local\Temp\claude\C--Users-world-Desktop-github---\861edb10-ea1e-453f-9fab-47137a7fb30e\scratchpad`

**중요:** 검증 스크립트와 로고 생성 스크립트는 **저장소에 커밋하지 않는다.** 스펙 §4가 저장소 구조를 확정했고 §9가 빌드 도구 커밋을 범위 밖으로 두었다. 두 스크립트는 스크래치패드에만 둔다.

## 파일 구조

| 파일 | 책임 |
|---|---|
| `assets/header.svg` | 이름 표시. 그라데이션 흐름 · 발광 · 입자 |
| `assets/divider.svg` | 헤더와 터미널 사이 구분. 빛이 훑고 지나감 |
| `assets/terminal.svg` | 창 UI + 4단계 타이핑. 개발자 정체성 표현 |
| `assets/ticker.svg` | 상태 문구 무한 순환 |
| `assets/stack.svg` | 기술 뱃지 8종. 공식 로고 + 순차 점등 |
| `assets/pulse.svg` | 뱃지와 카운터 사이 구분. 심전도 파형 |
| `README.md` | 위 6개를 순서대로 배치 + 소개 문구 + 외부 위젯 2개 + 통계 주석 블록 |
| `<scratchpad>/verify.sh` | 검증 하네스 (커밋 안 함) |
| `<scratchpad>/gen-stack.sh` | 로고 임베드 SVG 생성기 (커밋 안 함) |

각 SVG는 독립적으로 열어서 확인할 수 있고, 하나가 깨져도 나머지에 영향이 없다. README는 배치만 담당한다.

## SVG 공통 규칙

모든 자체 제작 SVG가 지켜야 하는 것:

- 애니메이션은 **SMIL만** — `<animate>`, `<animateTransform>`. CSS·JS 금지
- 폰트는 시스템 폰트만 — `ui-monospace,SFMono-Regular,Menlo,Consolas,monospace`
- 배경 `#0D1117` 고정
- `viewBox` 너비 760 (단 `terminal.svg`는 여백 포함 800)
- 파일 안에 `<script>` 없음

---

## Task 1: 검증 하네스 구축

먼저 검증 스크립트를 만들어 **전부 실패하는 것을 확인**한다. 이후 각 태스크가 검사 항목을 하나씩 통과시킨다.

**Files:**
- Create: `<scratchpad>/verify.sh`

- [ ] **Step 1: 검증 스크립트 작성**

`<scratchpad>/verify.sh` 생성:

```bash
#!/usr/bin/env bash
# World525 프로필 README 검증 — 스펙 §8
REPO="C:/Users/world/Desktop/github꾸미기"
cd "$REPO" || exit 1
PASS=0; FAIL=0
ok(){ echo "  PASS  $1"; PASS=$((PASS+1)); }
ng(){ echo "  FAIL  $1"; FAIL=$((FAIL+1)); }
SVGS="header divider terminal ticker stack pulse"

echo "[1] 파일 존재"
for f in README.md .gitignore; do
  [ -f "$f" ] && ok "$f" || ng "$f 없음"
done
for s in $SVGS; do
  [ -f "assets/$s.svg" ] && ok "assets/$s.svg" || ng "assets/$s.svg 없음"
done

echo "[2] SVG XML 유효성"
for s in $SVGS; do
  if [ -f "assets/$s.svg" ]; then
    python -c "import xml.dom.minidom,sys; xml.dom.minidom.parse('assets/$s.svg')" 2>/dev/null \
      && ok "$s.svg 파싱" || ng "$s.svg 파싱 실패"
  else ng "$s.svg 없어서 파싱 불가"; fi
done

echo "[3] 애니메이션 존재"
for s in $SVGS; do
  if [ -f "assets/$s.svg" ]; then
    grep -q '<animate' "assets/$s.svg" && ok "$s.svg 애니메이션" || ng "$s.svg 애니메이션 없음"
  else ng "$s.svg 없어서 확인 불가"; fi
done

echo "[4] stack.svg 로고 무결성"
if [ -f assets/stack.svg ]; then
  n=$(grep -o '<path d=' assets/stack.svg | wc -l | tr -d ' ')
  [ "$n" -eq 8 ] && ok "path 8개" || ng "path ${n}개 (8개여야 함)"
  for c in E34F26 663399 F7DF1E 61DAFB 3776AB F03C2E F24E1E ffffff; do
    grep -qi "#$c" assets/stack.svg && ok "색상 #$c" || ng "색상 #$c 없음"
  done
else ng "stack.svg 없음"; fi

echo "[5] 금지 요소 부재"
for f in README.md assets/*.svg; do
  [ -f "$f" ] || continue
  grep -qi '<script' "$f" && ng "$f 에 <script>" || ok "$f script 없음"
done
if [ -f README.md ]; then
  grep -q 'style=' README.md && ng "README.md 에 style= 속성" || ok "README.md style= 없음"
  grep -qi '<style' README.md && ng "README.md 에 <style>" || ok "README.md <style> 없음"
fi

echo "[6] README 경로 참조 정확성"
if [ -f README.md ]; then
  for s in $SVGS; do
    grep -q "assets/$s.svg" README.md && ok "참조 assets/$s.svg" || ng "참조 assets/$s.svg 없음"
  done
fi

echo "[7] 외부 URL 생존"
for u in "https://komarev.com/ghpvc/?username=World525&style=flat-square&color=8E2DE2&label=visitors" \
         "https://capsule-render.vercel.app/api?type=waving&color=0:8E2DE2,100:00F0FF&height=70&section=footer"; do
  c=$(curl -s -o /dev/null -w "%{http_code}" -m 20 "$u")
  [ "$c" = "200" ] && ok "$c $(echo "$u" | cut -c1-42)…" || ng "$c $(echo "$u" | cut -c1-42)…"
done

echo
echo "PASS $PASS  /  FAIL $FAIL"
[ "$FAIL" -eq 0 ]
```

- [ ] **Step 2: 실행해서 실패를 확인**

Run:
```bash
bash "C:/Users/world/AppData/Local/Temp/claude/C--Users-world-Desktop-github---/861edb10-ea1e-453f-9fab-47137a7fb30e/scratchpad/verify.sh"
```

Expected: `FAIL`이 20개 이상. `README.md`와 `assets/*.svg`가 아직 없으므로 [1]~[6]이 대부분 실패한다. `.gitignore`와 [7] 외부 URL 2건은 PASS여야 한다. **[7]이 FAIL이면 네트워크 문제이므로 멈추고 보고할 것.**

- [ ] **Step 3: assets 디렉터리 생성**

```bash
mkdir -p "C:/Users/world/Desktop/github꾸미기/assets"
```

커밋하지 않는다 (빈 디렉터리는 git이 추적하지 않음).

---

## Task 2: header.svg — 히어로 헤더

이름 위로 보라→시안 그라데이션이 4.5초 주기로 흐르고, 발광이 걸리며, 입자 5개가 서로 다른 속도로 떠오른다.

**Files:**
- Create: `assets/header.svg`

- [ ] **Step 1: 파일 작성**

`assets/header.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 185" role="img" aria-label="World525">
  <defs>
    <linearGradient id="sweep" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="60" y2="0">
      <stop offset="0" stop-color="#8E2DE2"/>
      <stop offset="0.5" stop-color="#00F0FF"/>
      <stop offset="1" stop-color="#8E2DE2"/>
      <animate attributeName="x1" values="-300;760" dur="4.5s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="60;1120" dur="4.5s" repeatCount="indefinite"/>
    </linearGradient>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="7" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="760" height="185" fill="#0D1117"/>
  <g fill="#00F0FF">
    <circle cx="88" cy="185" r="2">
      <animate attributeName="cy" values="190;15" dur="7s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.7;0" dur="7s" repeatCount="indefinite"/>
    </circle>
    <circle cx="215" cy="185" r="1.6">
      <animate attributeName="cy" values="190;15" dur="9s" begin="1.5s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.6;0" dur="9s" begin="1.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="520" cy="185" r="1.5" fill="#A855F7">
      <animate attributeName="cy" values="190;15" dur="10s" begin="0.8s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.55;0" dur="10s" begin="0.8s" repeatCount="indefinite"/>
    </circle>
    <circle cx="640" cy="185" r="2.2" fill="#A855F7">
      <animate attributeName="cy" values="190;15" dur="8s" begin="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.7;0" dur="8s" begin="3s" repeatCount="indefinite"/>
    </circle>
    <circle cx="700" cy="185" r="1.7">
      <animate attributeName="cy" values="190;15" dur="6.5s" begin="4.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.6;0" dur="6.5s" begin="4.2s" repeatCount="indefinite"/>
    </circle>
  </g>
  <text x="380" y="95" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="54" font-weight="700" fill="url(#sweep)" filter="url(#glow)">World525</text>
  <text x="380" y="132" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="14" fill="#8b949e" letter-spacing="3.5">code &#183; build &#183; learn
    <animate attributeName="opacity" values="0.45;1;0.45" dur="3.5s" repeatCount="indefinite"/>
  </text>
</svg>
```

- [ ] **Step 2: 검증 실행**

Run: `bash "<scratchpad>/verify.sh"`

Expected: `[1] assets/header.svg` PASS, `[2] header.svg 파싱` PASS, `[3] header.svg 애니메이션` PASS. 나머지 SVG는 여전히 FAIL.

- [ ] **Step 3: 브라우저에서 육안 확인**

파일을 브라우저로 열어 다음을 확인:
- "World525" 글자 위로 색이 좌→우로 흐른다
- 글자에 발광이 있다
- 아래에서 위로 작은 점들이 떠오른다
- 부제 "code · build · learn"이 은은하게 밝아졌다 어두워진다

하나라도 안 보이면 멈추고 보고할 것.

- [ ] **Step 4: 커밋**

```bash
cd "C:/Users/world/Desktop/github꾸미기" && git add assets/header.svg && git commit -m "Add animated hero header SVG"
```

---

## Task 3: divider.svg — 흐르는 구분선

빛 덩어리가 3.2초마다 좌→우로 훑고 지나간다.

**Files:**
- Create: `assets/divider.svg`

- [ ] **Step 1: 파일 작성**

`assets/divider.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 10" role="presentation">
  <defs>
    <linearGradient id="base" gradientUnits="userSpaceOnUse" x1="0" x2="760">
      <stop offset="0" stop-color="#8E2DE2" stop-opacity="0.12"/>
      <stop offset="0.5" stop-color="#00F0FF" stop-opacity="0.3"/>
      <stop offset="1" stop-color="#8E2DE2" stop-opacity="0.12"/>
    </linearGradient>
    <linearGradient id="pulse" gradientUnits="userSpaceOnUse" x1="-160" x2="0">
      <stop offset="0" stop-color="#00F0FF" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#00F0FF" stop-opacity="1"/>
      <stop offset="1" stop-color="#00F0FF" stop-opacity="0"/>
      <animate attributeName="x1" values="-160;760" dur="3.2s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="0;920" dur="3.2s" repeatCount="indefinite"/>
    </linearGradient>
  </defs>
  <rect width="760" height="10" fill="#0D1117"/>
  <rect y="4" width="760" height="2" fill="url(#base)"/>
  <rect y="3.5" width="760" height="3" fill="url(#pulse)"/>
</svg>
```

- [ ] **Step 2: 검증 실행**

Run: `bash "<scratchpad>/verify.sh"`

Expected: `divider.svg` 관련 3개 검사가 PASS로 바뀐다.

- [ ] **Step 3: 브라우저에서 육안 확인**

가는 선을 따라 밝은 빛이 왼쪽에서 오른쪽으로 반복해서 지나가는지 확인.

- [ ] **Step 4: 커밋**

```bash
cd "C:/Users/world/Desktop/github꾸미기" && git add assets/divider.svg && git commit -m "Add flowing divider SVG"
```

---

## Task 4: terminal.svg — 터미널 창

창 UI(테두리·타이틀바·신호등 3점)와 4단계 타이핑. 8초 주기.

타이핑은 텍스트 위에 `clipPath` 사각형의 `width`를 0에서 전체 폭까지 애니메이션해 좌→우로 드러내는 방식이다.

**Files:**
- Create: `assets/terminal.svg`

- [ ] **Step 1: 파일 작성**

`assets/terminal.svg` (viewBox 너비 800 — 창 좌우에 20px 여백):

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 246" role="img" aria-label="터미널">
  <defs>
    <clipPath id="win"><rect x="21" y="18" width="758" height="210" rx="9"/></clipPath>
    <clipPath id="line1"><rect x="44" y="63" height="22" width="0">
      <animate attributeName="width" values="0;80;80;80" keyTimes="0;0.10;0.98;1" dur="8s" repeatCount="indefinite"/>
    </rect></clipPath>
    <clipPath id="line3"><rect x="44" y="127" height="22" width="0">
      <animate attributeName="width" values="0;0;152;152;152" keyTimes="0;0.22;0.40;0.98;1" dur="8s" repeatCount="indefinite"/>
    </rect></clipPath>
  </defs>
  <rect width="800" height="246" fill="#0D1117"/>
  <g clip-path="url(#win)">
    <rect x="21" y="18" width="758" height="210" fill="#010409"/>
    <rect x="21" y="18" width="758" height="34" fill="#161b22"/>
  </g>
  <rect x="21" y="18" width="758" height="210" rx="9" fill="none" stroke="#30363d" stroke-width="1.5"/>
  <line x1="21" y1="52" x2="779" y2="52" stroke="#30363d" stroke-width="1"/>
  <circle cx="40" cy="35" r="6" fill="#ff5f56"/>
  <circle cx="60" cy="35" r="6" fill="#ffbd2e"/>
  <circle cx="80" cy="35" r="6" fill="#27c93f"/>
  <text x="102" y="40" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12" fill="#8b949e">world525@github: ~</text>
  <g clip-path="url(#line1)">
    <text x="44" y="79" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="15" fill="#e6edf3"><tspan fill="#00FF41">$</tspan> whoami</text>
  </g>
  <g opacity="0">
    <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.14;0.16;0.98;1" dur="8s" repeatCount="indefinite"/>
    <text x="44" y="105" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="15" fill="#A855F7">World525</text>
  </g>
  <g clip-path="url(#line3)">
    <text x="44" y="143" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="15" fill="#e6edf3"><tspan fill="#00FF41">$</tspan> cat status.txt</text>
  </g>
  <g opacity="0">
    <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.44;0.46;0.98;1" dur="8s" repeatCount="indefinite"/>
    <text x="44" y="169" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="15" fill="#8b949e">still learning. still building.</text>
  </g>
  <g opacity="0">
    <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.54;0.56;0.98;1" dur="8s" repeatCount="indefinite"/>
    <text x="44" y="201" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="15" fill="#00FF41">$</text>
    <rect x="62" y="188" width="9" height="17" fill="#00F0FF">
      <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.45;0.5;0.95;1" dur="1.1s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>
```

- [ ] **Step 2: 검증 실행**

Run: `bash "<scratchpad>/verify.sh"`

Expected: `terminal.svg` 관련 3개 검사가 PASS.

- [ ] **Step 3: 브라우저에서 육안 확인**

8초 주기로 아래 순서가 재생되는지 확인:
1. `$ whoami`가 좌→우로 타이핑됨
2. 보라색 `World525` 출력
3. `$ cat status.txt` 타이핑
4. 회색 `still learning. still building.` 출력
5. `$` 뒤에 시안색 커서가 깜빡임
6. 리셋 후 반복

- [ ] **Step 4: 커밋**

```bash
cd "C:/Users/world/Desktop/github꾸미기" && git add assets/terminal.svg && git commit -m "Add animated terminal window SVG"
```

---

## Task 5: ticker.svg — 상태 티커

문구가 끊김 없이 무한 순환한다. 텍스트를 2벌 두고 **복제 간격(980)과 이동 거리(-980)를 일치**시켜 이음매가 보이지 않게 한다. 양끝은 배경색 그라데이션으로 덮어 자연스럽게 사라지게 한다.

**Files:**
- Create: `assets/ticker.svg`

- [ ] **Step 1: 파일 작성**

`assets/ticker.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 40" role="img" aria-label="상태">
  <defs>
    <clipPath id="clip"><rect width="760" height="40"/></clipPath>
    <linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="0" x2="760">
      <stop offset="0" stop-color="#0D1117" stop-opacity="1"/>
      <stop offset="0.08" stop-color="#0D1117" stop-opacity="0"/>
      <stop offset="0.92" stop-color="#0D1117" stop-opacity="0"/>
      <stop offset="1" stop-color="#0D1117" stop-opacity="1"/>
    </linearGradient>
  </defs>
  <rect width="760" height="40" fill="#0D1117"/>
  <g clip-path="url(#clip)">
    <g>
      <animateTransform attributeName="transform" type="translate" from="0 0" to="-980 0" dur="16s" repeatCount="indefinite"/>
      <text x="0" y="26" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="15" fill="#8b949e"><tspan fill="#00FF41">&gt;</tspan> building things <tspan fill="#30363d">/</tspan> learning in public <tspan fill="#30363d">/</tspan> one commit at a time <tspan fill="#30363d">/</tspan> still curious <tspan fill="#30363d">/</tspan></text>
      <text x="980" y="26" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="15" fill="#8b949e"><tspan fill="#00FF41">&gt;</tspan> building things <tspan fill="#30363d">/</tspan> learning in public <tspan fill="#30363d">/</tspan> one commit at a time <tspan fill="#30363d">/</tspan> still curious <tspan fill="#30363d">/</tspan></text>
    </g>
  </g>
  <rect width="760" height="40" fill="url(#fade)"/>
</svg>
```

- [ ] **Step 2: 검증 실행**

Run: `bash "<scratchpad>/verify.sh"`

Expected: `ticker.svg` 관련 3개 검사가 PASS.

- [ ] **Step 3: 브라우저에서 육안 확인**

문구가 오른쪽에서 왼쪽으로 흐르고, **한 바퀴 돌 때 튐이나 빈 구간의 갑작스러운 점프가 없는지** 확인. 양끝에서 글자가 배경으로 서서히 사라지는지 확인.

이음매가 튄다면 두 `<text>`의 `x` 간격(980)과 `animateTransform`의 `to`(-980)가 일치하는지 확인할 것.

- [ ] **Step 4: 커밋**

```bash
cd "C:/Users/world/Desktop/github꾸미기" && git add assets/ticker.svg && git commit -m "Add infinite status ticker SVG"
```

---

## Task 6: stack.svg — 기술 뱃지 8종

공식 로고 경로를 임베드한 뱃지가 순차 점등되고 스캔광이 지나간다.

**경로 데이터를 손으로 옮기지 않는다.** Simple Icons에서 받아 스크립트로 추출한다 — 로고 path는 수백 자라 오타가 나면 그림이 깨지는데, 눈으로는 원인을 찾기 어렵다.

**Files:**
- Create: `<scratchpad>/gen-stack.sh` (커밋 안 함)
- Create: `<scratchpad>/icons/*.svg` (커밋 안 함)
- Create: `assets/stack.svg`

- [ ] **Step 1: 로고 8종 내려받기**

```bash
cd "C:/Users/world/AppData/Local/Temp/claude/C--Users-world-Desktop-github---/861edb10-ea1e-453f-9fab-47137a7fb30e/scratchpad" && mkdir -p icons && for slug in html5 css javascript react python git figma github; do
  code=$(curl -s -o "icons/$slug.svg" -w "%{http_code}" -m 20 "https://cdn.simpleicons.org/$slug")
  echo "$code  $slug"
done
```

Expected: 8줄 전부 `200`. 하나라도 `404`면 Simple Icons에서 해당 아이콘이 제거된 것이므로 멈추고 보고할 것.

> `visualstudiocode`는 Microsoft 상표 정책으로 제거되어 `404`다. 그래서 `github`으로 대체했다 — 스펙 §5.3 참조.

- [ ] **Step 2: 생성 스크립트 작성**

`<scratchpad>/gen-stack.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ICONS=icons
OUT="${1:-stack.svg}"

# slug|라벨|색상(비우면 아이콘 원본색)
ROW1="html5|HTML5| css|CSS3| javascript|JavaScript| react|React| python|Python|"
ROW2="git|Git| figma|Figma| github|GitHub|#ffffff"

CHAR=7.8; PADL=13; LOGO=18; GAP=9; PADR=13; CHIPH=38; CHIPGAP=11; VBW=760

getd(){ sed -n 's/.*<path d="\([^"]*\)".*/\1/p' "$ICONS/$1.svg"; }
getfill(){ sed -n 's/.*fill="\(#[0-9A-Fa-f]*\)".*/\1/p' "$ICONS/$1.svg" | head -1; }
chipw(){ awk -v n="${#1}" -v c=$CHAR -v a=$PADL -v b=$LOGO -v g=$GAP -v d=$PADR 'BEGIN{printf "%.1f", a+b+g+n*c+d}'; }

rowwidth(){ local t=0 n=0 e s l
  for e in $1; do IFS='|' read -r s l _ <<<"$e"; t=$(awk -v t=$t -v w=$(chipw "$l") 'BEGIN{print t+w}'); n=$((n+1)); done
  awk -v t=$t -v n=$n -v g=$CHIPGAP 'BEGIN{printf "%.1f", t+(n-1)*g}'; }

emit_row(){ # $1=entries $2=rowY $3=index_offset
  local entries="$1" rowy="$2" idx="$3" rw sx e slug label col d w cy A B ty
  rw=$(rowwidth "$entries"); sx=$(awk -v v=$VBW -v r=$rw 'BEGIN{printf "%.1f",(v-r)/2}')
  for e in $entries; do
    IFS='|' read -r slug label col <<<"$e"
    [ -z "$col" ] && col=$(getfill "$slug")
    d=$(getd "$slug"); w=$(chipw "$label")
    cy=$(awk -v y=$rowy -v h=$CHIPH 'BEGIN{printf "%.1f", y+h/2}')
    A=$(awk -v i=$idx 'BEGIN{printf "%.3f", 0.02+i*0.03}')
    B=$(awk -v i=$idx 'BEGIN{printf "%.3f", 0.07+i*0.03}')
    ty=$(awk -v c=$cy 'BEGIN{printf "%.1f", c-9}')
    cat <<EOF
  <g opacity="0">
    <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;$A;$B;0.94;1" dur="8s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0 7;0 7;0 0;0 0;0 0" keyTimes="0;$A;$B;0.94;1" dur="8s" repeatCount="indefinite"/>
    <rect x="$sx" y="$rowy" width="$w" height="$CHIPH" rx="8" fill="#0D1117" stroke="#30363d" stroke-width="1"/>
    <g transform="translate($(awk -v x=$sx -v p=$PADL 'BEGIN{printf "%.1f",x+p}'),$ty) scale(0.75)"><path d="$d" fill="$col"/></g>
    <text x="$(awk -v x=$sx -v p=$PADL -v l=$LOGO -v g=$GAP 'BEGIN{printf "%.1f",x+p+l+g}')" y="$(awk -v c=$cy 'BEGIN{printf "%.1f",c+4.6}')" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="13" fill="#c9d1d9">$label</text>
  </g>
EOF
    sx=$(awk -v x=$sx -v w=$w -v g=$CHIPGAP 'BEGIN{printf "%.1f", x+w+g}')
    idx=$((idx+1))
  done
}

{
cat <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 190" role="img" aria-label="기술 스택">
  <defs>
    <linearGradient id="scan" gradientUnits="userSpaceOnUse" x1="-200" x2="-60">
      <stop offset="0" stop-color="#00F0FF" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#00F0FF" stop-opacity="0.14"/>
      <stop offset="1" stop-color="#00F0FF" stop-opacity="0"/>
      <animate attributeName="x1" values="-200;760;760" keyTimes="0;0.55;1" dur="8s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-60;900;900" keyTimes="0;0.55;1" dur="8s" repeatCount="indefinite"/>
    </linearGradient>
  </defs>
  <rect width="760" height="190" fill="#0D1117"/>
  <text x="380" y="20" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11" fill="#8b949e" letter-spacing="2.6">LEARNING</text>
EOF
emit_row "$ROW1" 32 0
cat <<'EOF'
  <text x="380" y="112" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11" fill="#8b949e" letter-spacing="2.6">TOOLS</text>
EOF
emit_row "$ROW2" 124 5
cat <<'EOF'
  <rect width="760" height="190" fill="url(#scan)"/>
</svg>
EOF
} > "$OUT"

echo "생성: $OUT ($(wc -c < "$OUT" | tr -d ' ')B, 칩 $(grep -c '<rect x=' "$OUT")개)"
```

- [ ] **Step 3: 생성 후 저장소로 복사**

```bash
cd "C:/Users/world/AppData/Local/Temp/claude/C--Users-world-Desktop-github---/861edb10-ea1e-453f-9fab-47137a7fb30e/scratchpad" && bash gen-stack.sh stack.svg && cp stack.svg "C:/Users/world/Desktop/github꾸미기/assets/stack.svg"
```

Expected: `생성: stack.svg (약 14900B, 칩 8개)`

- [ ] **Step 4: 검증 실행**

Run: `bash "<scratchpad>/verify.sh"`

Expected: `[4] stack.svg 로고 무결성` 섹션에서 `path 8개` PASS와 색상 8건 PASS. `stack.svg` 파싱·애니메이션도 PASS.

- [ ] **Step 5: 브라우저에서 육안 확인**

- LEARNING 행에 HTML5 · CSS3 · JavaScript · React · Python 5개
- TOOLS 행에 Git · Figma · GitHub 3개
- **로고가 각각 알아볼 수 있는 형태인지** (뭉개지거나 검은 덩어리로 보이면 path 추출 실패)
- GitHub 로고가 흰색으로 보이는지 (원본 `#181717`이면 배경에 묻혀 안 보임)
- 8개가 왼쪽부터 차례로 떠오르며 나타나고, 그 뒤 옅은 시안색 빛이 가로로 훑고 지나가는지

- [ ] **Step 6: 커밋**

```bash
cd "C:/Users/world/Desktop/github꾸미기" && git add assets/stack.svg && git commit -m "Add animated tech stack SVG with embedded official logos"
```

---

## Task 7: pulse.svg — 심전도 구분선

심박 파형을 따라 초록 빛이 흐른다. `stroke-dasharray`로 짧은 실선 구간을 만들고 `stroke-dashoffset`을 움직여 빛이 경로를 따라가는 것처럼 보이게 한다.

**Files:**
- Create: `assets/pulse.svg`

- [ ] **Step 1: 파일 작성**

`assets/pulse.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 26" role="presentation">
  <rect width="760" height="26" fill="#0D1117"/>
  <path d="M0 13 H300 l14 -9 l13 18 l13 -22 l14 26 l13 -13 H760" fill="none" stroke="#30363d" stroke-width="1.6"/>
  <path d="M0 13 H300 l14 -9 l13 18 l13 -22 l14 26 l13 -13 H760" fill="none" stroke="#00FF41" stroke-width="1.8" stroke-dasharray="90 860" stroke-linecap="round">
    <animate attributeName="stroke-dashoffset" values="950;0" dur="3.4s" repeatCount="indefinite"/>
  </path>
</svg>
```

- [ ] **Step 2: 검증 실행**

Run: `bash "<scratchpad>/verify.sh"`

Expected: `pulse.svg` 관련 3개 검사가 PASS. 이 시점에서 `[1]`~`[4]`가 전부 PASS이고, `[6] README 경로 참조`만 남아 FAIL이어야 한다.

- [ ] **Step 3: 브라우저에서 육안 확인**

회색 심박 파형 위로 초록 빛 조각이 왼쪽에서 오른쪽으로 반복해서 흐르는지 확인.

- [ ] **Step 4: 커밋**

```bash
cd "C:/Users/world/Desktop/github꾸미기" && git add assets/pulse.svg && git commit -m "Add ECG pulse divider SVG"
```

---

## Task 8: README.md 조립

SVG 6개를 순서대로 배치하고, 소개 문구 · 외부 위젯 2개 · 통계 주석 블록을 넣는다.

**GitHub 제약 때문에 지켜야 할 것:**
- `style` 속성 금지 — 제거된다. 가운데 정렬은 `<div align="center">`로만 한다 (`align`은 허용 속성)
- `<style>`, `<script>` 금지
- 허용 속성은 `href, src, title, alt, width, height, align, target, lang` 등

**Files:**
- Create: `README.md`

- [ ] **Step 1: 파일 작성**

`README.md`:

```markdown
<div align="center">

<img src="assets/header.svg" width="100%" alt="World525">

<img src="assets/divider.svg" width="100%" alt="">

<img src="assets/terminal.svg" width="100%" alt="터미널: whoami, cat status.txt">

여러 분야를 기웃거리며 배우는 중입니다.<br>
만들면서 배우고, 배우면서 또 만듭니다.

<img src="assets/ticker.svg" width="100%" alt="building things / learning in public / one commit at a time / still curious">

<img src="assets/stack.svg" width="100%" alt="기술 스택: HTML5, CSS3, JavaScript, React, Python, Git, Figma, GitHub">

<img src="assets/pulse.svg" width="100%" alt="">

<img src="https://komarev.com/ghpvc/?username=World525&style=flat-square&color=8E2DE2&label=visitors" alt="방문자 수">

<!--
  📊 통계 위젯 — 공개 저장소가 생기면 이 주석의 첫 줄과 마지막 줄만 지우세요.

  주의: github-readme-stats 공용 인스턴스는 GitHub API 시간당 한도를 전체
  사용자와 공유해서, 과부하 시 카드 대신 에러 이미지가 뜹니다 (2026-08-18
  확인 당시 503). 계속 실패하면 본인 Vercel 계정에 직접 배포하고 PAT_1
  환경변수를 등록하세요: https://github.com/anuraghazra/github-readme-stats

  트로피(github-profile-trophy)는 넣지 않았습니다 — 2026-08-18 기준 402
  Payment Required로 무료 인스턴스가 중단된 상태입니다.

<img src="https://github-readme-stats.vercel.app/api?username=World525&show_icons=true&hide_border=true&bg_color=0D1117&title_color=A855F7&icon_color=00F0FF&text_color=c9d1d9" alt="GitHub 통계">

<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=World525&layout=compact&hide_border=true&bg_color=0D1117&title_color=A855F7&text_color=c9d1d9" alt="많이 쓴 언어">

<img src="https://streak-stats.demolab.com/?user=World525&hide_border=true&background=0D1117&ring=A855F7&fire=00F0FF&currStreakLabel=c9d1d9" alt="연속 커밋">

-->

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:8E2DE2,100:00F0FF&height=70&section=footer" width="100%" alt="">

</div>
```

- [ ] **Step 2: 검증 실행 — 전부 통과해야 함**

Run: `bash "<scratchpad>/verify.sh"`

Expected: 마지막 줄이 `FAIL 0`. 하나라도 FAIL이면 멈추고 원인을 보고할 것.

- [ ] **Step 3: 금지 요소 직접 재확인**

```bash
cd "C:/Users/world/Desktop/github꾸미기" && grep -n 'style=\|<style\|<script' README.md assets/*.svg || echo "금지 요소 없음 ✅"
```

Expected: `금지 요소 없음 ✅`

- [ ] **Step 4: 커밋**

```bash
cd "C:/Users/world/Desktop/github꾸미기" && git add README.md && git commit -m "Add profile README assembling six animated SVGs"
```

---

## Task 9: 최종 확인 및 push 안내

- [ ] **Step 1: 저장소 상태 확인**

```bash
cd "C:/Users/world/Desktop/github꾸미기" && git status --short && echo "--- 추적 파일 ---" && git ls-files && echo "--- 커밋 ---" && git log --oneline
```

Expected:
- `git status --short`가 비어 있음 (미커밋 변경 없음)
- 추적 파일: `.gitignore`, `README.md`, `assets/` 6개, `docs/` 2개 — 총 10개
- `.superpowers/`가 목록에 **없어야** 함
- 커밋 9개 (기존 2개 + Task 2~8의 7개)

- [ ] **Step 2: 검증 최종 실행**

Run: `bash "<scratchpad>/verify.sh"`

Expected: `FAIL 0`

- [ ] **Step 3: 사용자에게 push 안내**

**에이전트는 push하지 않는다.** 원격 저장소 생성은 사용자 권한이다. 아래를 안내한다:

1. <https://github.com/new> 에서 저장소 생성
   - Repository name: `World525` (계정명과 **정확히** 일치해야 프로필에 표시됨. 대문자 `W` 주의)
   - Public 선택
   - README·`.gitignore`·license 추가 **체크하지 않음** (로컬과 충돌)

2. 생성 후 아래 실행:

```bash
cd "C:/Users/world/Desktop/github꾸미기" && git remote add origin https://github.com/World525/World525.git && git push -u origin main
```

3. <https://github.com/World525> 접속해서 확인할 것:
   - 프로필 상단에 README가 표시되는가
   - 6개 SVG가 **모두 움직이는가** (정지 이미지로 보이면 보고)
   - 방문자 카운터와 푸터 웨이브가 뜨는가 (외부 서비스라 지연 가능)
   - 로고가 알아볼 수 있는 형태인가

- [ ] **Step 4: 완료 보고**

무엇이 만들어졌고, 검증에서 무엇을 확인했고, 사용자가 직접 해야 할 일(저장소 생성 + push)이 무엇인지 보고한다. push를 대신 했다고 말하지 않는다.

---

## 자체 검토 결과

**스펙 커버리지** — §5 블록 9개 전부 Task 2~8에 대응. §5.2 SVG 6종 각각 태스크 있음. §5.3 로고 임베드는 Task 6. §5.4 소개 문구는 Task 8. §7 주석 블록은 Task 8 Step 1에 실제 코드로 포함(트로피 제외 및 사유 명시). §8 검증 9항목은 Task 1의 `verify.sh`가 7항목을 자동화하고, 육안 확인(§8-5)은 각 태스크 Step 3에, git 상태(§8-9)는 Task 9에 배치.

**범위 밖 준수** — 뱀 애니메이션·GitHub Actions·라이트모드 분기·Vercel 배포 없음. 생성 스크립트와 검증 스크립트는 스크래치패드에만 두어 §4 저장소 구조를 그대로 유지.

**식별자 일관성** — SVG의 `id`는 파일마다 독립이므로 이름 중복이 문제되지 않는다(`divider.svg`의 `pulse` 그라데이션과 `pulse.svg` 파일명은 별개). `verify.sh`의 `SVGS` 목록과 Task 2~7의 파일명, Task 8 README의 `src` 경로가 모두 `header/divider/terminal/ticker/stack/pulse`로 일치한다.
