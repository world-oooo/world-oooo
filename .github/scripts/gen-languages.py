#!/usr/bin/env python3
"""공개 저장소의 언어 바이트 수를 합산해 애니메이션 SVG 막대그래프를 만든다.

GitHub 자체 언어바와 같은 기준(바이트 수)을 쓴다. 표준 라이브러리만 사용하므로
워크플로우에서 pip install 없이 바로 돌아간다.

환경변수: GITHUB_TOKEN(필수), USERNAME(필수), OUTPUT(기본 assets/languages.svg)
"""
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
TOP_N = 6          # 나머지는 Other로 묶는다
BAR_X, BAR_Y, BAR_W, BAR_H = 40, 34, 680, 14
VB_W = 760
CYCLE = "8s"       # 다른 SVG들과 같은 주기

# GitHub linguist 색상. 로고 뱃지에서 브랜드 색을 쓴 것과 같은 이유로,
# 언어는 사람들이 이미 아는 색을 그대로 쓴다.
COLORS = {
    "C#": "#178600", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "GDScript": "#355570", "CSS": "#663399", "HTML": "#e34c26",
    "Python": "#3572A5", "Shell": "#89e051", "PLpgSQL": "#336790",
    "Wolfram Language": "#dd1100", "Lua": "#000080", "Luau": "#00A2FF",
    "C++": "#f34b7d", "C": "#555555", "Java": "#b07219", "Go": "#00ADD8",
    "Rust": "#dea584", "Ruby": "#701516", "PHP": "#4F5D95", "Swift": "#F05138",
    "Kotlin": "#A97BFF", "Dart": "#00B4AB", "Vue": "#41b883", "Svelte": "#ff3e00",
    "Jupyter Notebook": "#DA5B0B", "Dockerfile": "#384d54", "Makefile": "#427819",
}
OTHER_COLOR = "#6e7681"


def api(path, token):
    req = urllib.request.Request(API + path, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "gen-languages",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect(user, token):
    """소유한 공개 저장소(포크 제외)의 언어 바이트를 합산한다."""
    totals, page = {}, 1
    while True:
        repos = api("/users/%s/repos?per_page=100&type=owner&page=%d" % (user, page), token)
        if not repos:
            break
        for repo in repos:
            if repo.get("fork") or repo.get("archived"):
                continue
            try:
                for lang, size in api("/repos/%s/%s/languages" % (user, repo["name"]), token).items():
                    totals[lang] = totals.get(lang, 0) + size
            except urllib.error.HTTPError as e:
                print("  건너뜀 %s (%s)" % (repo["name"], e.code), file=sys.stderr)
        if len(repos) < 100:
            break
        page += 1
    return totals


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(totals):
    total = sum(totals.values())
    if not total:
        raise SystemExit("언어 데이터가 없습니다")

    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    top = ranked[:TOP_N]
    rest = sum(v for _, v in ranked[TOP_N:])
    if rest:
        top.append(("Other", rest))

    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d 118" role="img" '
        'aria-label="공개 저장소 언어 분포">' % VB_W,
        '  <defs>',
        '    <clipPath id="round"><rect x="%d" y="%d" width="%d" height="%d" rx="%d"/></clipPath>'
        % (BAR_X, BAR_Y, BAR_W, BAR_H, BAR_H // 2),
        '    <clipPath id="reveal"><rect x="%d" y="%d" height="%d" width="0">' % (BAR_X, BAR_Y, BAR_H),
        '      <animate attributeName="width" values="0;%d;%d;%d" keyTimes="0;0.18;0.96;1" '
        'dur="%s" repeatCount="indefinite"/>' % (BAR_W, BAR_W, BAR_W, CYCLE),
        '    </rect></clipPath>',
        '  </defs>',
        '  <rect width="%d" height="118" fill="#0D1117"/>' % VB_W,
        '  <text x="%d" y="20" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,'
        'Consolas,monospace" font-size="11" fill="#8b949e" letter-spacing="2.6">'
        'PUBLIC REPOSITORIES BY LANGUAGE</text>' % (VB_W // 2),
        '  <rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="#161b22"/>'
        % (BAR_X, BAR_Y, BAR_W, BAR_H, BAR_H // 2),
        '  <g clip-path="url(#round)"><g clip-path="url(#reveal)">',
    ]

    x = float(BAR_X)
    for name, size in top:
        w = BAR_W * size / total
        color = OTHER_COLOR if name == "Other" else COLORS.get(name, OTHER_COLOR)
        out.append('    <rect x="%.2f" y="%d" width="%.2f" height="%d" fill="%s"/>'
                   % (x, BAR_Y, w, BAR_H, color))
        x += w
    out.append('  </g></g>')

    # 범례: 한 줄에 최대 4개, 가운데 정렬
    per_row, item_w, row_h = 4, 168, 24
    for i, (name, size) in enumerate(top):
        row, col = divmod(i, per_row)
        in_row = min(per_row, len(top) - row * per_row)
        start = (VB_W - in_row * item_w) / 2
        cx = start + col * item_w
        cy = 74 + row * row_h
        color = OTHER_COLOR if name == "Other" else COLORS.get(name, OTHER_COLOR)
        pct = size * 100.0 / total
        delay = 0.18 + i * 0.04
        out += [
            '  <g opacity="0">',
            '    <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;%.3f;%.3f;0.96;1" '
            'dur="%s" repeatCount="indefinite"/>' % (delay, delay + 0.04, CYCLE),
            '    <circle cx="%.1f" cy="%.1f" r="5" fill="%s"/>' % (cx + 6, cy - 4, color),
            '    <text x="%.1f" y="%.1f" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'
            'monospace" font-size="12" fill="#c9d1d9">%s</text>' % (cx + 18, cy, esc(name)),
            '    <text x="%.1f" y="%.1f" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'
            'monospace" font-size="12" fill="#6e7681">%.1f%%</text>'
            % (cx + 18 + len(name) * 7.2 + 8, cy, pct),
            '  </g>',
        ]

    out.append('</svg>')
    return "\n".join(out) + "\n", total, top


def main():
    token = os.environ.get("GITHUB_TOKEN")
    user = os.environ.get("USERNAME")
    if not token or not user:
        raise SystemExit("GITHUB_TOKEN 과 USERNAME 이 필요합니다")
    dest = os.environ.get("OUTPUT", "assets/languages.svg")

    totals = collect(user, token)
    svg, total, top = build(totals)
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)

    print("생성: %s (%d바이트)" % (dest, len(svg)))
    print("집계: %d바이트 / 언어 %d종" % (total, len(totals)))
    for name, size in top:
        print("  %-20s %5.1f%%" % (name, size * 100.0 / total))


if __name__ == "__main__":
    main()
