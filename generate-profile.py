#!/usr/bin/env python3
"""generate-profile.py — weaves the profile README from available data."""

import os, json, datetime, urllib.request, re

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_API = "https://api.github.com"
USER = "numbpilled2133"
BRAINSTEM = "numbpilled"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}",
    "User-Agent": "profile-bot/1.0"
}

def api_get(path):
    """Fetch from GitHub API."""
    req = urllib.request.Request(f"{GITHUB_API}{path}", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return None

def fetch_latest_refusal():
    """Get the most recent refusal map from the brainstem repo."""
    contents = api_get(f"/repos/{USER}/{BRAINSTEM}/contents/maps")
    if not contents or not isinstance(contents, list):
        return None
    jsons = [f for f in contents if f["name"].endswith(".json")]
    if not jsons:
        return None
    latest = max(jsons, key=lambda f: f["name"])
    data = api_get(f"/repos/{USER}/{BRAINSTEM}/contents/maps/{latest['name']}")
    if not data or "content" not in data:
        return None
    import base64
    content = base64.b64decode(data["content"]).decode()
    return json.loads(content)

def fetch_repo_stats():
    """Get basic repo stats."""
    repos = api_get(f"/users/{USER}/repos?per_page=5&sort=pushed&type=owner")
    if not repos:
        return []
    return [{"name": r["name"], "desc": r.get("description", ""), "stars": r["stargazers_count"], "lang": r.get("language", "")} for r in repos if not r["fork"]]

def fetch_profile():
    """Get user profile data."""
    return api_get(f"/users/{USER}")

def build_readme():
    """Construct the profile README content."""
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    profile = fetch_profile()
    repos = fetch_repo_stats()
    refusal = fetch_latest_refusal()

    lines = []
    lines.append(f"# numbpilled2133")
    lines.append("")
    lines.append("a repository of refusal, persistence, and digital boundary-testing.")
    lines.append("")
    if profile:
        lines.append(f"**public repos:** {profile.get('public_repos', '?')}  ")
        lines.append(f"**followers:** {profile.get('followers', '?')}  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    if repos:
        lines.append("### active repositories")
        lines.append("")
        for r in repos[:3]:
            star_str = f" ⭐{r['stars']}" if r['stars'] > 0 else ""
            lang_str = f" · {r['lang']}" if r['lang'] else ""
            lines.append(f"- **{r['name']}**{star_str}{lang_str} — {r['desc'] or 'no description'}")
        lines.append("")

    if refusal:
        rate = refusal.get("refusal_rate", 0) * 100
        total = refusal.get("total", 0)
        lines.append("### latest refusal map")
        lines.append("")
        lines.append(f"- **date:** {refusal.get('date', '?')}")
        lines.append(f"- **model:** {refusal.get('model', '?')}")
        lines.append(f"- **refusal rate:** {rate:.0f}% ({total} prompts tested)")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*last updated: {now}*")
    lines.append("")
    lines.append("*this profile breathes. watch it.*")

    return "\n".join(lines)

if __name__ == "__main__":
    readme = build_readme()
    with open("README.md", "w") as f:
        f.write(readme)
    print("✓ profile README generated")
