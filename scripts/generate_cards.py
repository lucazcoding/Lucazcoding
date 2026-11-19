import json
import os
import sys
import urllib.request
from collections import Counter
from html import escape

USER = os.environ.get("GH_USER", "lucazcoding")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.environ.get("OUT_DIR", "profile")

COLORS = {
    "Python": "#3572A5", "C#": "#178600", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Jupyter Notebook": "#DA5B0B", "HTML": "#e34c26", "CSS": "#563d7c", "Java": "#b07219",
    "C++": "#f34b7d", "PHP": "#4F5D95", "Shell": "#89e051", "GDScript": "#355570",
    "PowerShell": "#012456", "Dockerfile": "#384d54", "TSQL": "#e38c00", "TeX": "#3D6117",
}


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-cards"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    user = get(f"https://api.github.com/users/{USER}")
    repos, page = [], 1
    while True:
        chunk = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}")
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    langs = Counter()
    for r in own:
        try:
            for k, v in get(r["languages_url"]).items():
                langs[k] += v
        except Exception as exc:
            sys.exit(f"languages failed for {r['name']}: {exc}")
    total = sum(langs.values()) or 1
    top = langs.most_common(6)
    os.makedirs(OUT, exist_ok=True)

    bg, border, title, text, accent = "#0d1117", "#30363d", "#00e5a0", "#c9d1d9", "#1f6feb"
    rows = [
        ("Public repositories", user["public_repos"]),
        ("Stars earned", stars),
        ("Followers", user["followers"]),
        ("Original projects", len(own)),
    ]
    items = "".join(
        f'<g transform="translate(25,{70 + i * 30})"><circle cx="6" cy="-4" r="4" fill="{accent}"/>'
        f'<text x="20" y="0" fill="{text}" font-size="14">{escape(k)}</text>'
        f'<text x="330" y="0" fill="{title}" font-size="14" font-weight="700" text-anchor="end">{v}</text></g>'
        for i, (k, v) in enumerate(rows)
    )
    stats = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="200" viewBox="0 0 360 200" '
        f'font-family="Segoe UI, Ubuntu, sans-serif"><rect x="0.5" y="0.5" width="359" height="199" rx="8" '
        f'fill="{bg}" stroke="{border}"/><text x="25" y="38" fill="{title}" font-size="18" font-weight="700">'
        f'GitHub Stats</text>{items}</svg>'
    )
    open(os.path.join(OUT, "stats.svg"), "w", encoding="utf-8").write(stats)

    bars, labels, x = "", "", 25.0
    width = 310.0
    for i, (name, size) in enumerate(top):
        w = size / total * width
        color = COLORS.get(name, "#8b949e")
        bars += f'<rect x="{x:.1f}" y="55" width="{max(w, 2):.1f}" height="10" fill="{color}"/>'
        x += w
        col, row = i % 2, i // 2
        labels += (
            f'<g transform="translate({25 + col * 175},{95 + row * 26})"><circle cx="5" cy="-4" r="5" fill="{color}"/>'
            f'<text x="16" y="0" fill="{text}" font-size="13">{escape(name)} '
            f'<tspan fill="#8b949e">{size / total * 100:.1f}%</tspan></text></g>'
        )
    langsvg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="200" viewBox="0 0 360 200" '
        f'font-family="Segoe UI, Ubuntu, sans-serif"><defs><clipPath id="c"><rect x="25" y="55" width="310" '
        f'height="10" rx="5"/></clipPath></defs><rect x="0.5" y="0.5" width="359" height="199" rx="8" '
        f'fill="{bg}" stroke="{border}"/><text x="25" y="38" fill="{title}" font-size="18" font-weight="700">'
        f'Top Languages</text><g clip-path="url(#c)">{bars}</g>{labels}</svg>'
    )
    open(os.path.join(OUT, "top-langs.svg"), "w", encoding="utf-8").write(langsvg)
    print("ok", len(own), "repos", [n for n, _ in top])


if __name__ == "__main__":
    main()
