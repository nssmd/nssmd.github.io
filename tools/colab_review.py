"""Editable Colab copy of the COMPASS review page.

Turns review/compass/index.html (English) and review/compass/zh/index.html (Chinese) into two `%%html` cells whose
source IS the page HTML, so the page can be edited directly in Colab (edit the cell, run it, save). Assets, CSS and
blog.js load from https://nssmd.github.io (blog.js reads <meta name="compass-base">). Saved outputs let the notebook
display without starting a runtime.  usage: python tools/colab_review.py OUT.ipynb
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nssmd.github.io'
EN_DOC = 'https://docs.google.com/document/d/1H76U3hDNDe5E_JY4HZYSGUGbulYV-CGbZnrcT1s-fow/edit'
ZH_DOC = 'https://docs.google.com/document/d/1JTHE2NCcWe6QY0voh2jcGmbtoJjS3zIg-uTa3eb6qGc/edit'


def fragment(page):
    head = page[page.index('<head>') + 6:page.index('</head>')]
    body = page[page.index('<body>') + 6:page.rindex('</body>')]
    metas = ''.join(re.findall(r'<meta name="compass-[^"]+" content="[^"]*">', head))
    css = ''.join(re.findall(r'<link rel="stylesheet"[^>]*>', head)) + ''.join(re.findall(r'<style>.*?</style>', head, flags=re.S))
    js = ''.join(re.findall(r'<script src="[^"]+"[^>]*></script>', head))
    body = re.sub(r'<nav class="lang-switch".*?</nav>', '', body, flags=re.S)
    body = re.sub(r'<a class="skip-link"[^>]*>.*?</a>', '', body, flags=re.S)
    out = f'<meta name="compass-base" content="{ORIGIN}">{metas}{css}\n<div class="colab-compass">\n{body}\n</div>\n{js}'
    out = re.sub(r'(src|href|poster|data-src|content)="/(?!/)', rf'\1="{ORIGIN}/', out)
    out = re.sub(r'url\(/(?!/)', f'url({ORIGIN}/', out)
    return out.replace(' defer>', '>')


def cell(cid, title, html):
    src = '%%html\n' + html
    return {'cell_type': 'code', 'metadata': {'id': cid, 'cellView': 'code'}, 'execution_count': None,
            'source': src.splitlines(True),
            'outputs': [{'output_type': 'display_data', 'metadata': {}, 'data': {'text/html': html.splitlines(True), 'text/plain': ['<IPython.core.display.HTML object>']}}]}


def build(out):
    en = fragment((ROOT / 'review/compass/index.html').read_text())
    zh = fragment((ROOT / 'review/compass/zh/index.html').read_text())
    intro = ('# COMPASS — interactive review / 交互版\n\n'
             '**中文版**在下方第二个格子，**English** in the first cell below.\n\n'
             '直接修改：展开格子里的 HTML，改文字后点 ▶ 运行，再“文件 → 保存”。不需要 GPU，连接默认运行时即可。\n'
             'To edit: change the HTML in a cell, press ▶ to re-render, then File → Save.\n\n'
             f'Doc（English）：{EN_DOC}  \nDoc（中文）：{ZH_DOC}')
    nb = {'nbformat': 4, 'nbformat_minor': 0,
          'metadata': {'colab': {'name': 'COMPASS — Interactive HTML Review.ipynb', 'provenance': [], 'toc_visible': True},
                       'kernelspec': {'name': 'python3', 'display_name': 'Python 3'}, 'language_info': {'name': 'python'}},
          'cells': [{'cell_type': 'markdown', 'metadata': {'id': 'compass-review-intro'}, 'source': intro.splitlines(True)},
                    {'cell_type': 'markdown', 'metadata': {'id': 'compass-en-title'}, 'source': ['## English']},
                    cell('compass-interactive-html', 'English', en),
                    {'cell_type': 'markdown', 'metadata': {'id': 'compass-zh-title'}, 'source': ['## 中文']},
                    cell('compass-interactive-html-zh', '中文', zh)]}
    Path(out).write_text(json.dumps(nb, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    build(sys.argv[1])
