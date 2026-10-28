"""Localize Quarto's shared navigation at build time, including partial renders.

The localized links work without JavaScript. Never edit generated HTML by hand.
"""

import html
import os
from pathlib import Path
import posixpath
import re


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "docs")
PAGES = {
    "ホーム": ("Home", "index.html"),
    "プロフィール": ("Profile", "about.html"),
    "業績": ("Publications", "publications.html"),
    "講演": ("Presentations", "presentations.html"),
    "セミナー歴": ("Seminars", "seminars.html"),
    "ノート": ("Notes", "notes.html"),
}
ANCHOR = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.S)
MENU = re.compile(r'(<span class="menu-text">)(.*?)(</span>)', re.S)
NAVBAR = re.compile(r'<nav class="navbar\b.*?</nav>', re.S)


def localize(page):
    relative = page.relative_to(OUTPUT).as_posix()
    english = relative.startswith("en/")
    local_page = relative.removeprefix("en/") if english else relative
    counterpart = local_page if english else "en/" + local_page
    # Untranslated future notes can still switch to the other notes index.
    if not (ROOT / counterpart).with_suffix(".qmd").exists():
        counterpart = "notes.html" if english else "en/notes.html"

    def href(target):
        return posixpath.relpath(target, posixpath.dirname(relative) or ".")

    def anchor(match):
        attrs, body = match.groups()
        classes = re.search(r'\bclass="([^"]*)"', attrs)
        if not classes:
            return match.group(0)
        class_names = classes[1].split()
        if "navbar-brand" in class_names:
            target = "en/index.html" if english else "index.html"
        elif "nav-link" in class_names:
            label = MENU.search(body)
            if not label:
                return match.group(0)
            label = html.unescape(label[2])
            if label in ("English", "日本語"):
                target = counterpart
                new_label = "日本語" if english else "English"
                attrs = re.sub(r'\s+(?:hreflang|lang)="[^"]*"', "", attrs)
                lang = "ja" if english else "en"
                attrs += f' hreflang="{lang}" lang="{lang}"'
            else:
                item = PAGES.get(label)
                if item is None:
                    item = next((v for v in PAGES.values() if v[0] == label), None)
                if item is None:
                    return match.group(0)
                new_label = item[0] if english else next(k for k, v in PAGES.items() if v == item)
                target = ("en/" if english else "") + item[1]
            body = MENU.sub(lambda m: m[1] + new_label + m[3], body)
            class_names = [name for name in class_names if name != "active"]
            attrs = re.sub(r'\s+aria-current="[^"]*"', "", attrs)
            active = relative == target or (
                local_page.startswith("notes/") and target == ("en/" if english else "") + "notes.html"
            )
            if active:
                class_names.append("active")
                attrs += ' aria-current="page"' if relative == target else ' aria-current="true"'
            attrs = re.sub(r'\bclass="[^"]*"', 'class="' + " ".join(class_names) + '"', attrs)
        else:
            return match.group(0)
        attrs = re.sub(r'\bhref="[^"]*"', f'href="{href(target)}"', attrs)
        return f"<a{attrs}>{body}</a>"

    content = page.read_text()
    content = NAVBAR.sub(lambda m: re.sub(r'[ \t]+\n', '\n', ANCHOR.sub(anchor, m[0])), content)
    if english:
        # Quarto already localizes the consent text using en/_metadata.yml.
        content = content.replace('"website_privacy_policy_url":"/privacy.html"',
                                  '"website_privacy_policy_url":"/en/privacy.html"')
        content = re.sub(r'<footer\b.*?</footer>', lambda m: m[0].replace(
            f'href="{href("privacy.html")}"', f'href="{href("en/privacy.html")}"'),
            content, flags=re.S)
    content = re.sub(r'\n<link rel="alternate" hreflang="(?:ja|en)"[^>]*>', "", content)
    alternate = "ja" if english else "en"
    content = content.replace("</head>",
        f'<link rel="alternate" hreflang="{alternate}" href="{href(counterpart)}">\n</head>')
    page.write_text(content)


for page in OUTPUT.rglob("*.html"):
    if (ROOT / page.relative_to(OUTPUT)).with_suffix(".qmd").exists():
        localize(page)
