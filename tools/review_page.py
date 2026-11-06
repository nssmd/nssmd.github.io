"""Interactive review copy of the COMPASS article (embedded in Colab).

The review copy shows only the article: no site header/footer, no links back to the homepage or the blog index.
It is written in English (/review/compass/) and Chinese (/review/compass/zh/), with a language switch on both.
Chinese text comes from tools/compass_strings_zh.json (visible English text node -> Chinese).
"""
import json, re, html
from pathlib import Path

SWITCH = ('<nav class="lang-switch" aria-label="Language"><a href="/review/compass/"{en}>EN</a>'
          '<a href="/review/compass/zh/"{zh}>中文</a></nav>')
STYLE = ('<style>.lang-switch{position:fixed;top:14px;right:16px;z-index:50;display:flex;gap:2px;padding:3px;'
         'border-radius:999px;background:rgba(255,255,255,.92);box-shadow:0 1px 6px rgba(0,0,0,.12);font:600 13px/1 system-ui,sans-serif}'
         '.lang-switch a{padding:6px 11px;border-radius:999px;color:#555;text-decoration:none}'
         '.lang-switch a[aria-current]{background:#222;color:#fff}</style>')


def strip_site(page):
    """Remove everything that leads away from the article."""
    page = re.sub(r'<header class="site-header">.*?</header>', '', page, count=1, flags=re.S)
    page = re.sub(r'<footer class="site-footer">.*?</footer>', '', page, count=1, flags=re.S)
    page = re.sub(r'<section class="article-end">.*?</section>', '', page, count=1, flags=re.S)
    page = re.sub(r'<a href="/blog/" class="back-link">.*?</a>', '', page, flags=re.S)
    page = re.sub(r'<link rel="alternate"[^>]*>', '', page)
    # no code link in the review copy
    page = re.sub(r'<a href="https://github\.com/[^"]*">[^<]*</a>(\s*&nbsp;\s*·\s*&nbsp;\s*)?', '', page)
    # any remaining internal link to the homepage or the blog index becomes plain text
    page = re.sub(r'<a [^>]*href="/(?:#[^"]*|blog/|blog/feed\.xml)?"[^>]*>(.*?)</a>', r'\1', page, flags=re.S)
    return page


def translate(page, table):
    out, skip = [], 0
    for part in re.split(r'(<[^>]+>)', page):
        if part.startswith('<'):
            m = re.match(r'<(/?)(script|style|pre|code)\b', part)
            if m: skip += -1 if m.group(1) else 1
            out.append(part); continue
        key = html.unescape(part.strip())
        if skip or not key or key not in table:
            out.append(part); continue
        lead, trail = part[:len(part) - len(part.lstrip())], part[len(part.rstrip()):]
        out.append(lead + html.escape(table[key], quote=False) + trail)
    return ''.join(out)


def write_review(root, page, origin, url):
    root = Path(root)
    page = page.replace(f'<link rel="canonical" href="{origin}{url}">',
                        f'<meta name="robots" content="noindex"><link rel="canonical" href="{origin}/review/compass/">')
    page = strip_site(page).replace('<title>', '<title>Interactive review — ', 1)
    en = page.replace('</head>', STYLE + '</head>', 1).replace('<body>', '<body>' + SWITCH.format(en=' aria-current="true"', zh=''), 1)
    d = root / 'review/compass'; d.mkdir(parents=True, exist_ok=True); (d / 'index.html').write_text(en)
    tf = root / 'tools/compass_strings_zh.json'
    if not tf.exists(): return
    zh = translate(page, json.loads(tf.read_text()))
    zh = zh.replace('1H76U3hDNDe5E_JY4HZYSGUGbulYV-CGbZnrcT1s-fow', '1JTHE2NCcWe6QY0voh2jcGmbtoJjS3zIg-uTa3eb6qGc')   # Chinese Doc
    zh = zh.replace('<html lang="en">', '<html lang="zh-CN">', 1)
    zh = zh.replace('</head>', STYLE + '</head>', 1).replace('<body>', '<body>' + SWITCH.format(en='', zh=' aria-current="true"'), 1)
    z = d / 'zh'; z.mkdir(exist_ok=True); (z / 'index.html').write_text(zh)
