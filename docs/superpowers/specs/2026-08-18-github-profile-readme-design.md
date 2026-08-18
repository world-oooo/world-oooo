# GitHub 프로필 README 설계 — world-oooo

작성일: 2026-08-18
대상 계정: [`world-oooo`](https://github.com/world-oooo)
프로필: <https://github.com/world-oooo>  ·  저장소: <https://github.com/world-oooo/world-oooo>

> 최초 설계는 `World525`를 대상으로 했다. 그 계정은 2017년에 만든 뒤 사용하지 않은 계정이었고, 실제 사용 계정은 `world-oooo`임이 뒤늦게 확인되어 전환했다 — §3, §11 참조.
미리보기: <https://claude.ai/code/artifact/1ed9706c-333b-462b-9787-7e964d1b5b23>

## 1. 배경과 목적

사용자가 Instagram [@gitskins](https://www.instagram.com/gitskins) 계정의 화려한 GitHub 프로필 영상을 보고 동일한 수준의 프로필을 원함.

리서치 결과, 해당 영상들의 프로필은 특별한 기술이 아니라 **외부 서비스가 실시간 생성하는 SVG를 마크다운 이미지로 삽입한 것**이었다. 재현 난이도는 낮으나 서비스 가용성과 GitHub의 HTML 필터링이라는 제약이 존재하며, 이 설계는 그 제약을 **자체 제작 SVG**로 우회한다.

**목적**: 개인 기록/취미용 프로필. 취업·채용 목적 아님. 사용자가 "애니메이션을 최대한 넣어달라"고 명시적으로 요청함.

## 2. 결정 사항

| 항목 | 결정 | 근거 |
|---|---|---|
| 비주얼 컨셉 | 네온 × 터미널 융합, 균형형(50:50) | 사용자가 A/C 혼합 요청 후 3개 비율안 중 2번 선택 |
| 팔레트 | 강조 보라 `#A855F7` / **그라데이션 보라 `#8E2DE2`** / 시안 `#00F0FF` / 그린 `#00FF41` / 배경 `#0D1117` | 배경을 GitHub 다크모드와 일치시켜 이미지 경계 제거 |
| 애니메이션 분량 | **최대치** — 움직이는 요소 7곳 | 사용자 명시 요청 |
| 구현 방식 | **자체 제작 SVG 6개 + 외부 서비스 2개** | 외부 서비스 장애 내성 확보 (§6) |
| 기술 뱃지 | **자체 SVG에 공식 로고 경로 임베드** | 로고와 애니메이션은 양자택일이 아님 (§5.3) |
| 전달 형태 | 로컬 git 저장소 구성 후 사용자가 push (B안) | 반복 수정이 예상되므로 로컬 관리가 유리 |
| 통계 위젯 | **제외**하되 완성 코드를 HTML 주석으로 보존 (트로피는 코드 자체를 넣지 않음 — §7) | 공개 저장소 0개 + 서비스 장애 (§6) |
| 뱀 애니메이션 | **포함** (`Platane/snk/svg-only@v3`) | 대상 계정 변경으로 잔디 데이터 확보 (§11) |
| 라이트모드 | **대응하지 않음** (다크 고정) | `<picture>` 분기 시 에셋 2배. 개인용이며 개발자 다수가 다크모드 사용 |
| 언어 | 본문 한국어, SVG 내부 영문 | 모노스페이스 폰트에서 한글 자간이 불안정 |

## 3. 계정 현황 — `World525` 기준 (2026-08-18 확인, 이후 전환됨)

```
공개 저장소: 0     팔로워: 0     기존 프로필 README: 없음     bio: 없음     잔디 활동: 없음
```

GitHub 데이터에 의존하는 위젯(통계·스트릭·트로피·활동 그래프·뱀)은 **전부 사용 불가**. 따라서 README의 시각적 무게 중심 전체를 **자체 제작 SVG**가 담당한다.

> **이후 변경**: 대상 계정이 `world-oooo`로 바뀌면서 이 전제가 무효화됐다. 해당 계정은 컨트리뷰션 활동이 있어 뱀 애니메이션이 가능해졌다 — §11 참조. 통계 위젯은 서비스 장애(§6)라는 별개 사유가 남아 여전히 주석 보관 상태다.

## 4. 파일 구조

작업 폴더 `github꾸미기/`를 그대로 git 저장소로 사용하고, 원격 저장소 `world-oooo/world-oooo`에 push한다.

```
github꾸미기/                          ← git 저장소 (원격: world-oooo/world-oooo)
├─ README.md                          ← 프로필 본문
├─ assets/
│  ├─ header.svg                      ← 히어로 헤더
│  ├─ divider.svg                     ← 흐르는 구분선
│  ├─ terminal.svg                    ← 터미널 창
│  ├─ ticker.svg                      ← 상태 티커
│  ├─ stack.svg                       ← 기술 뱃지 8종
│  └─ pulse.svg                       ← 심전도 구분선
├─ docs/superpowers/specs/
│  └─ 2026-08-18-github-profile-readme-design.md
└─ .gitignore                         ← .superpowers/ 제외
```

> 프로필 저장소는 `README.md`만 프로필 페이지에 렌더링되므로 `docs/`, `assets/`가 함께 있어도 노출에 영향이 없다.

## 5. README 구성

위에서 아래로 12개 블록:

| # | 블록 | 구현 | 움직임 | 의존 |
|---|---|---|---|---|
| 1 | 히어로 헤더 | `assets/header.svg` | ✅ | 없음 |
| 2 | 흐르는 구분선 | `assets/divider.svg` | ✅ | 없음 |
| 3 | 터미널 창 | `assets/terminal.svg` | ✅ | 없음 |
| 4 | 소개 문구 | 마크다운 텍스트 (가운데 정렬) | — | 없음 |
| 5 | 상태 티커 | `assets/ticker.svg` | ✅ | 없음 |
| 6 | 기술 뱃지 | `assets/stack.svg` | ✅ | 없음 |
| 7 | 심전도 구분선 | `assets/pulse.svg` | ✅ | 없음 |
| 8 | 방문자 카운터 | komarev | — | 외부 |
| 9 | 푸터 웨이브 | capsule-render | ✅ | 외부 |

블록 11과 12 사이에 **통계 위젯 주석 블록**(§7)이 위치한다.

**외부 의존은 komarev와 capsule-render 두 개뿐이다.** 둘 다 실패해도 README의 뼈대(헤더·터미널·뱃지)는 그대로 유지된다.

### 5.1 자체 제작 SVG 공통 규칙

**자체 제작하는 이유**: GitHub은 README의 HTML을 필터링하며 `style` 속성과 `<style>`·`<script>` 태그를 제거한다. 허용 속성은 `href, src, title, alt, width, height, align, target, lang` 등으로 제한된다. 따라서 터미널 창이나 애니메이션 뱃지를 HTML/CSS로 구현할 수 없다. 반면 **저장소에 커밋한 SVG 파일은 내부 애니메이션을 포함한 채 상대경로로 렌더링된다.**

**보라가 두 종류인 이유**: `#8E2DE2`는 시안 `#00F0FF`와 짝을 이루는 **그라데이션 양 끝점** 전용이다(`header.svg` 이름 스윕, `divider.svg` 바탕선, 방문자 카운터, 푸터 웨이브). `#A855F7`는 단색으로 칠하는 **강조색**이다(`header.svg` 입자, 터미널의 `world-oooo` 출력, Python·Figma 로고 색). 그라데이션에서 `#A855F7`은 시안과 대비가 약해 띠가 흐릿해지므로 더 진한 `#8E2DE2`를 쓴다.

모든 자체 SVG는 다음을 지킨다:

- **애니메이션은 SMIL만 사용** (`<animate>`, `<animateTransform>`). CSS·JavaScript 미사용 — 필터링을 확실히 통과시키기 위함
- **폰트는 시스템 폰트만**: `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`. 웹폰트는 로드되지 않음
- **주기는 8초로 통일** (`divider`/`pulse`는 자체 리듬 유지). 여러 요소가 8초에 맞춰 함께 리셋되어 화면 전체가 한 호흡으로 움직인다
- **배경은 `#0D1117`로 고정** — GitHub 다크모드와 일치
- `viewBox` 너비는 **760** 통일 (`terminal.svg`만 여백 포함 800)

### 5.2 SVG별 사양

| 파일 | 내용 | 기법 | 주기 |
|---|---|---|---|
| `header.svg` | 이름 위로 보라→시안 그라데이션이 흐르고, 발광 효과, 입자 5개가 서로 다른 속도로 떠오름. 부제 명멸 | `linearGradient`의 `x1`/`x2` 애니메이션 + `feGaussianBlur` 발광 + `circle`의 `cy`/`opacity` | 4.5s |
| `divider.svg` | 빛 덩어리가 좌→우로 훑고 지나감 | 그라데이션 좌표 이동 | 3.2s |
| `terminal.svg` | 창 UI(테두리·타이틀바·신호등) + 4단계 타이핑 | `clipPath` 폭 애니메이션 + `opacity` | 8.0s |
| `ticker.svg` | 상태 문구가 끊김 없이 무한 순환, 양끝 페이드 | `animateTransform` + 텍스트 2벌 복제(간격 980 = 이동거리) | 16.0s |
| `stack.svg` | 뱃지 8개가 순차 점등 + 스캔광 통과 | `opacity`/`translate` 스태거 + 이동 그라데이션 | 8.0s |
| `pulse.svg` | 심박 파형을 따라 초록 빛이 흐름 | `stroke-dashoffset` | 3.4s |

**`terminal.svg` 타임라인** (8초 주기)

| 시점 | 내용 | 색 |
|---|---|---|
| 0.0–0.8s | `$ whoami` 타이핑 | `$`=그린, 명령=`#e6edf3` |
| 1.2s | `world-oooo` 출력 | `#A855F7` |
| 1.8–3.2s | `$ cat status.txt` 타이핑 | 동일 |
| 3.6s | `still learning. still building.` | `#8b949e` |
| 4.4s~ | `$` + 커서 블록 깜빡임(1.1초 주기) | 커서=`#00F0FF` |

**`ticker.svg` 문구**: `> building things / learning in public / one commit at a time / still curious /`

> 초기안은 티커에도 기술 이름을 넣었으나, `stack.svg`가 로고와 함께 같은 정보를 보여주게 되어 **내용이 중복**됐다. 티커를 상태 문구로 바꿔 중복을 제거했다.

### 5.3 stack.svg — 로고와 애니메이션 양립

초기 설계에서는 "공식 로고를 쓰려면 shields.io 외부 이미지가 필요하고, 외부 이미지에는 애니메이션을 넣을 수 없다"고 판단해 **정지 뱃지**로 두었다. **이 전제는 틀렸다.** 로고의 SVG 경로 데이터를 받아와 자체 SVG 안에 직접 넣으면 둘 다 성립한다.

- **출처**: [Simple Icons](https://simpleicons.org) — `https://cdn.simpleicons.org/<slug>`. 아이콘 파일은 CC0 1.0(퍼블릭 도메인)이며, 상표권은 각 소유자에게 있다. 임베드는 shields.io도 사용하는 일반적 방식이다
- **추출 방식**: 경로 데이터를 손으로 옮기지 않고 **생성 스크립트로 자동 추출**해 오타 가능성을 제거했다. 원본은 모두 단일 `<path>`, `viewBox="0 0 24 24"`이며 `scale(0.75)`로 18px에 맞춘다
- **효과**: shields.io 의존이 사라져 **외부 의존이 3개에서 2개로 감소**

**뱃지 구성 및 색상**

초기안은 사용자의 자기신고("프론트+백엔드+입문 단계")에서 추론했으나, 실제 저장소 21개를 조사하니 어긋났다 — 최다 언어인 TypeScript(7개)가 빠져 있고, 주 언어로 쓰인 적 없는 Python이 들어가 있었다. 실측 분포로 교체했다.

| 행 | 뱃지 | 슬러그 | logoColor | 근거·비고 |
|---|---|---|---|---|
| LANGUAGES | TypeScript | `typescript` | `#3178C6` | 저장소 7개 — 최다 |
| | HTML5 | `html5` | `#E34F26` | 3개 |
| | Wolfram | `wolfram` | `#DD1100` | 3개 |
| | C# | `dotnet` | `#512BD4` | 2개. `csharp` 슬러그가 `404`라 .NET 마크로 대체 |
| | JavaScript | `javascript` | `#F7DF1E` | 2개 |
| TOOLS | Godot | `godotengine` | `#478CBF` | GDScript 저장소 |
| | Roblox | `robloxstudio` | `#00A2FF` | Luau 저장소. `roblox`는 `#000000`이라 어두운 배경에서 소실되어 Studio 마크 사용 |
| | Git | `git` | `#F03C2E` | 브랜드 원본 |
| | Figma | `figma` | `#F24E1E` | 브랜드 원본 |
| | GitHub | `github` | `#FFFFFF` | 원본 `#181717`은 어두운 배경에서 보이지 않아 흰색으로 변경 |

**VS Code 제외 사유**: Simple Icons가 Microsoft 상표 정책으로 아이콘을 제거해 `cdn.simpleicons.org/visualstudiocode`가 `404`를 반환한다. **GitHub 로고로 대체**했다. 대체 가능 후보(모두 `200` 확인): Node.js, Docker, TypeScript, Next.js, Tailwind CSS, Notion.

칩 규격: 높이 38, 모서리 `rx=8`, 배경 `#0D1117`, 테두리 `#30363d`, 라벨 `#c9d1d9` 13px. 좌우 패딩 13, 로고 18px, 로고-라벨 간격 9, 칩 간격 11. 행 전체를 가로 중앙 정렬.

### 5.4 확정 콘텐츠

**소개 문구**
```
여러 분야를 기웃거리며 배우는 중입니다.
만들면서 배우고, 배우면서 또 만듭니다.
```

> 사용자가 기술 스택 질문에 프론트엔드·백엔드·입문 단계·기타를 모두 선택했다. 상호 모순되는 조합이므로 **"여러 분야를 탐색 중인 학습자"**로 해석하고, 뱃지 행 제목을 `LEARNING`으로 두어 과장을 피했다. 사용자가 승인함.

## 6. 외부 서비스 실측 (2026-08-18)

`curl`로 직접 확인한 HTTP 응답 코드:

| 서비스 | 용도 | 코드 | 판정 |
|---|---|---|---|
| capsule-render | 푸터 웨이브 | `200` | 채택 |
| komarev | 방문자 카운터 | `200` | 채택 |
| cdn.simpleicons.org | 로고 경로 (빌드 시 1회) | `200` | 채택 |
| streak-stats.demolab.com | 연속 커밋 | `200` | 주석 보관용으로 유효 |
| shields.io | 기술 뱃지 | `200` | **불채택** — §5.3로 대체 |
| **github-readme-stats** | 커밋 통계 카드 | **`503`** | **현재 장애** |
| **github-profile-trophy** | 트로피 | **`402`** | **Payment Required — 무료 인스턴스 사실상 중단** |

`github-readme-stats`의 `503`은 알려진 고질적 문제다. 공용 인스턴스가 GitHub API 시간당 5,000회 한도를 전체 사용자와 공유하기 때문에 과부하 시 실패한다 ([이슈 #3226](https://github.com/anuraghazra/github-readme-stats/issues/3226) 외 다수). `github-profile-trophy`의 `402`는 Vercel 요금 문제로 서비스 측 조치 없이는 복구되지 않는다.

**이 실측이 "자체 제작 우선" 방침을 뒷받침한다.** 저장소가 0개라 숫자가 0으로 나오는 문제 이전에, 서비스가 응답하지 않아 **깨진 이미지 아이콘**이 표시되었을 상황이었다.

## 7. 통계 위젯 주석 블록

README 하단(블록 8과 9 사이)에 **완성된 코드를 HTML 주석 안에 보관**한다. 주석은 **두 개로 분리**한다:

1. **안내 주석** — 왜 꺼두었는지, 어떻게 켜는지, §6의 서비스 불안정성 경고. 영구히 주석으로 남는다.
2. **`STATS-BLOCK` 주석** — 이미지 태그 3개만 들어간다. 여는 줄과 닫는 줄 두 줄을 지우면 활성화된다.

> 초기 구현은 설명문과 이미지 태그를 **한 주석 안에** 넣고 "첫 줄과 마지막 줄을 지우라"고 안내했다. 문법적으로는 동작하지만, 그렇게 하면 한국어 유지보수 메모(503 설명·PAT_1 안내·트로피 402 사유)까지 프로필 페이지에 **본문 텍스트로 노출**된다. 검토에서 발견되어 두 주석으로 분리했다. 분리 후 활성화 시뮬레이션에서 노출되는 텍스트는 소개 문구 2줄뿐임을 확인했다.

HTML 주석은 중첩되지 않고 내부의 `--` 시퀀스가 조기 종료를 유발할 수 있으므로, 주석 안의 대시는 전부 em 대시(`—`, U+2014)를 쓴다.

포함 대상:
1. 커밋 통계 카드 (`github-readme-stats`)
2. 언어 비율 (`top-langs`)
3. 연속 커밋 스트릭 (`streak-stats.demolab.com` — herokuapp 구 도메인 아님)

**트로피는 포함하지 않는다.** `402`로 서비스가 중단된 상태이며 복구 시점을 알 수 없어, 주석으로 남겨도 오작동 코드를 방치하는 셈이 된다. 주석 안에 트로피 제외 사유와 §6의 서비스 불안정성 경고를 함께 적는다.

## 8. 검증 방법

구현 완료의 판정 기준:

1. **파일 존재**: `README.md`, `assets/` 아래 SVG 6개, `.gitignore` 생성 확인
2. **SVG 유효성**: 6개 파일 전부 XML 파서로 파싱하여 오류 없음 확인
3. **애니메이션 존재**: 6개 파일 전부에 `<animate` 또는 `<animateTransform` 요소가 1개 이상 존재
4. **로고 무결성**: `stack.svg`에 `<path>` 8개와 지정된 8개 색상이 모두 존재
5. **육안 확인**: 브라우저에서 각 SVG를 열어 의도한 움직임이 재생되는지 확인
6. **외부 URL 생존**: README의 외부 이미지 URL 2개(komarev, capsule-render)에 `curl` 요청하여 `200` 확인
7. **금지 요소 부재**: `README.md`에 `style=` 속성과 `<style>`·`<script>` 태그가 없음을 grep으로 확인. SVG 파일에도 `<script>`가 없음을 확인
8. **경로 정확성**: README의 SVG 참조 경로 6개가 실제 파일과 일치 (대소문자 포함)
9. **git 상태**: 커밋 완료, `.superpowers/`가 추적되지 않음

**저장소 생성과 push** — 최종적으로 사용자 허가를 받아 에이전트가 `gh`로 수행했다. 단 한 가지 함정이 있었다:

> `gh repo create`로 **빈 저장소**를 만든 뒤 push하면 GitHub이 이를 **프로필 README 저장소로 등록하지 않는다.** 공식 문서의 네 조건(계정명 일치·Public·기본 브랜치 루트의 `README.md`·내용 있음)을 모두 만족해도 프로필에 표시되지 않는다. 웹 UI에서 **"Add a README file"을 체크해 생성**해야 등록된다. 재push·인덱싱 대기·가시성 토글은 모두 효과가 없었고, 웹 UI로 재생성한 직후 아직 GitHub 기본 README뿐이던 시점에 이미 표시되기 시작한 것으로 확인했다.
>
> 이 때문에 최종 push는 강제 덮어쓰기 대신 `git merge --allow-unrelated-histories -X ours`를 써서 **GitHub이 만든 초기 커밋을 뿌리로 보존**했다.

## 9. 범위 밖 (하지 않는 것)

- ~~뱀 애니메이션~~ — **§11로 이동해 구현됨**
- 라이트모드 `<picture>` 분기 — §2 결정
- 자체 Vercel 인스턴스 배포 — 통계 위젯을 쓰지 않으므로 불필요
- 로고 생성 스크립트 커밋 — 일회성 빌드 도구이며, 재생성이 필요하면 §10 참조
- 원격 저장소 생성 및 push — 사용자 권한 영역

## 10. 향후 작업

| 시점 | 할 일 |
|---|---|
| 공개 저장소 생성 후 | README의 `STATS-BLOCK` 주석에서 여는 줄과 닫는 줄 2줄만 삭제 (안내 주석은 그대로 둘 것 — §7) |
| 통계 카드가 계속 `503`일 때 | 본인 Vercel 계정에 `github-readme-stats` 배포 + `PAT_1` 환경변수 등록 |
| 뱃지 교체 시 | `cdn.simpleicons.org/<slug>`에서 경로를 받아 `stack.svg`의 해당 `<path d>`와 라벨·칩 폭을 교체. 슬러그는 simpleicons.org에서 확인 |
| 문구 변경 시 | `terminal.svg`(status.txt 줄), `ticker.svg`(2벌 모두), `README.md` 소개 문구 |

## 11. 뱀 애니메이션 (추가 구현)

초기 설계는 대상 계정 `World525`의 잔디 활동이 0이라 이 기능을 §9(범위 밖)에 두었다. 대상이 실제 사용 계정 `world-oooo`로 바뀌면서 전제가 사라져 구현했다.

| 항목 | 값 |
|---|---|
| 액션 | `Platane/snk/svg-only@v3` (SVG 전용, GIF 인코딩 생략) |
| 워크플로우 | `.github/workflows/snake.yml` |
| 트리거 | 12시간 주기 cron + `workflow_dispatch` + `main` push |
| 권한 | `contents: write` (job 레벨) |
| 산출물 | `output` 브랜치의 `snake.svg` |
| README 참조 | `raw.githubusercontent.com/world-oooo/world-oooo/output/snake.svg` |

**배포 방식**: 흔히 쓰이는 `crazy-max/ghaction-github-pages` 대신 워크플로우 안에서 `git push`를 직접 실행한다. 서드파티 액션 의존을 하나 줄이기 위함이며, 이 프로젝트 전반의 "외부 의존 최소화" 방침과 같은 이유다.

**색상**: 프로필 팔레트에 맞춘다.

```
color_snake=#00FF41
color_dots=#161b22,#3B1F6B,#6B2AB8,#8E2DE2,#00F0FF
```

빈 칸은 GitHub 다크모드 기본값 `#161b22`, 기여도가 올라갈수록 보라(`#3B1F6B`→`#8E2DE2`)를 거쳐 시안 `#00F0FF`에 도달한다. 뱀은 터미널 그린.

**SMIL 규칙의 예외**: §5.1은 자체 제작 SVG에 SMIL만 쓰도록 정했다. 이 파일은 생성물이며 CSS `@keyframes` 19개로 애니메이션한다. SVG 파일 내부에 포함된 CSS는 GitHub이 그대로 재생하므로 문제없다 — 제거되는 것은 README **본문**의 `<style>`과 `style` 속성이다.

**검증 (2026-08-18)**: 워크플로우 실행 성공 → `output` 브랜치에 `snake.svg` 23,911B 생성 → XML 파싱 통과, `rect` 374개, `<script>` 0개, 지정 색상 6개 전부 적용 → 프로필에서 880×192로 로드 확인.

## 12. 언어 분포 차트 (추가 구현)

공개 저장소의 **언어 바이트 수**를 합산해 GitHub 자체 언어바와 같은 기준으로 그린다. 저장소 개수가 아니라 바이트 기준이라 보조 언어까지 반영된다.

| 항목 | 값 |
|---|---|
| 생성기 | `.github/scripts/gen-languages.py` (표준 라이브러리만 — 워크플로우에 설치 단계 불필요) |
| 워크플로우 | `.github/workflows/languages.yml`, 매주 월요일 + 수동 |
| 산출물 | `assets/languages.svg` |
| 데이터 | `/repos/{owner}/{repo}/languages` 합산, 포크·아카이브 제외 |
| 표시 | 상위 6종 + `Other`, 누적 막대 + 범례 |
| 색상 | GitHub linguist 색상 (로고에 브랜드 색을 쓴 것과 같은 이유 — 이미 통용되는 색을 따른다) |
| 애니메이션 | 막대가 좌→우로 채워지고 범례가 순차 등장. 8초 주기로 다른 SVG와 통일 |

**서드파티 없음**: 액션을 쓰지 않고 저장소 안의 스크립트만 돌린다.

**한계**: Actions의 `GITHUB_TOKEN`은 저장소 범위라 **비공개 저장소를 볼 수 없다.** 따라서 공개 저장소 기준이며, 라벨도 `PUBLIC REPOSITORIES BY LANGUAGE`로 명시했다. 전체를 포함하려면 사용자 범위 PAT를 시크릿으로 등록해야 한다.

**실측 (2026-08-18)**: 총 1,595,635바이트 / 9종 — C# 57.7%, TypeScript 22.8%, GDScript 14.6%, CSS 2.0%, Wolfram 1.0%, PLpgSQL 1.0%, Other 0.9%.

## 13. 3D 잔디 그래프 (추가 구현)

| 항목 | 값 |
|---|---|
| 액션 | `yoshi389111/github-profile-3d-contrib@latest` |
| 워크플로우 | `.github/workflows/contrib-3d.yml`, 매일 + 수동 |
| 산출물 | `profile-3d-contrib/` 아래 10종 변형 |
| 채택 | `profile-night-green.svg` |

**변형 선택 근거**: 생성되는 10종 중 `night` 계열만 밝은 글자색(`#eeeeff`, `#aaaaaa`)을 쓴다. 나머지는 어두운 글자라 우리 다크 배경에서 읽히지 않는다. 배경이 투명이라 GitHub 다크 테마에 그대로 얹힌다. 나머지 9종도 저장소에 남으므로 README의 파일명 한 단어만 바꾸면 교체된다.

## 14. 향후 여지

| 항목 | 내용 |
|---|---|
| **비공개 기여 공개** | Settings → Profile → Contribution settings에서 활성화하면 잔디가 63 → 약 403으로 늘어난다. 뱀·3D 그래프가 훨씬 조밀해진다. 저장소명·커밋 메시지·코드는 노출되지 않는다 |
| 언어 차트 전체 범위 | 사용자 범위 PAT를 시크릿으로 등록하면 비공개 저장소까지 집계 가능 |
| 통계 위젯 | §7 주석 블록. 서비스가 `503`인 상태 |
| 티커 여백 | 텍스트 실측 651.5px vs 간격 980px → 328.5px 공백 |
| 라이트모드 | 현재 다크 고정 |
