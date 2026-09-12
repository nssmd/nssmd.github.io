"""Build the static homepage: python build.py (standard library only)."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
profile = json.loads((ROOT / 'data/profile.json').read_text())
papers = json.loads((ROOT / 'data/publications.json').read_text())
posts = json.loads((ROOT / 'data/blog.json').read_text())
e = escape

def external(url, label, cls=''):
    return f'<a class="{cls}" href="{e(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label}</a>'

def thumbnail(p):
    if p.get('image') or p.get('video'):
        return
    colors = {'Embodied AI & Agents': ('#edf3f8', '#2c638a'), 'Multimodal Learning': ('#f4eff7', '#79608f'), 'Time Series & Dynamics': ('#edf5f1', '#487b65')}
    bg, ink = colors[p['category']]
    label = {'argus':'ARGUS', 'resource2skill':'RESOURCE2SKILL', 'force':'FORCE × VLA', 'tri-marf':'Tri-MARF', 'unig2u':'UniG2U-Bench', 'mage-flow':'Mage-Flow', 'pi-gnn':'PI-GNN', 'danet':'DANet', 'past':'PAST'}[p['id']]
    if p['category'] == 'Embodied AI & Agents':
        drawing = '<path d="M64 72H112M148 72H196M130 54V35M78 38L113 60M147 84L180 108"/><rect x="36" y="57" width="28" height="28" rx="7"/><rect x="112" y="54" width="36" height="36" rx="10"/><rect x="196" y="57" width="28" height="28" rx="7"/><circle cx="130" cy="27" r="8"/><circle cx="70" cy="33" r="8"/><circle cx="188" cy="112" r="8"/><path d="m123 72 5 5 10-11"/>'
    elif p['category'] == 'Multimodal Learning':
        drawing = '<rect x="37" y="37" width="70" height="64" rx="8"/><circle cx="86" cy="53" r="6"/><path d="m43 93 21-28 17 19 9-10 11 19M118 63H151m-8-7 8 7-8 7M151 84H118m8-7-8 7 8 7"/><rect x="164" y="37" width="59" height="64" rx="8"/><path d="M176 54H211M176 65H205M176 76H211M176 87H196"/>'
    else:
        drawing = '<path d="M35 35V106H228" opacity=".35"/><path d="m40 87 17-9 17 12 17-34 17 9 17-20 17 36 17-14 17 6 17-31 17 13 14-20"/><path d="M40 96C65 96 71 56 98 72S137 103 158 69 197 67 224 40" stroke-dasharray="4 5" opacity=".4"/><circle cx="91" cy="56" r="4"/><circle cx="142" cy="81" r="4"/><circle cx="193" cy="42" r="4"/>'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="520" height="340" viewBox="0 0 260 170"><rect width="260" height="170" rx="10" fill="{bg}"/><g stroke="{ink}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round">{drawing}</g><text x="130" y="146" text-anchor="middle" font-family="Arial,sans-serif" font-weight="700" font-size="15" letter-spacing="1" fill="{ink}">{e(label)}</text></svg>'
    (ROOT / f'assets/{p["id"]}.svg').write_text(svg)

def card(p):
    thumbnail(p)
    authors = e(p['authors']).replace('Zimo Wen', '<strong>Zimo Wen</strong>').replace('Z Wen', '<strong>Z Wen</strong>').replace('...', 'et al.')
    url = p['paper']
    links = external(url, 'Paper <span aria-hidden="true">↗</span>')
    for key, label in [('website', 'Website'), ('code', 'Code'), ('video_url', 'Video')]:
        if p.get(key):
            links += external(p[key], label+' <span aria-hidden="true">↗</span>')
    links += external(p['scholar'], 'Scholar <span aria-hidden="true">↗</span>')
    if p.get('video'):
        media = f'<div class="paper-media"><video class="paper-video" controls muted loop playsinline preload="metadata" poster="{e(p["poster"])}" aria-label="{e(p["title"])} — official project video"><source src="{e(p["video"])}" type="video/mp4">{external(p["video"], "Watch project video")}</video><span class="media-caption">{e(p.get("video_note", "Project video"))}</span></div>'
    else:
        img = p.get('image', f'assets/{p["id"]}.svg')
        media = f'<a class="paper-image" href="{e(p.get("website", url))}" target="_blank" rel="noopener noreferrer" aria-label="View {e(p["title"])}"><img src="{e(img)}" width="520" height="340" alt="{e(p["id"])} research overview" loading="lazy"></a>'
    return f'''<article class="paper" data-year="{p['year']}">
      {media}
      <div class="paper-content"><div class="paper-meta"><span class="venue {'conference' if not p['badge'].startswith('arXiv') else ''}">{e(p['badge'])}</span><span class="topic">{e(p['topic'])}</span></div>
      <h3>{external(url, e(p['title']))}</h3><p class="authors">{authors}</p><p class="paper-summary">{e(p['summary'])}</p><div class="paper-links">{links}</div></div>
    </article>'''

groups = []
for i, category in enumerate(dict.fromkeys(p['category'] for p in papers), 1):
    items = [p for p in papers if p['category'] == category]
    groups.append(f'<details class="category" open><summary><span class="category-number">0{i}</span><span>{e(category)}</span><span class="count">{len(items)}</span><span class="chevron" aria-hidden="true">⌄</span></summary><div class="category-body">{"".join(card(p) for p in items)}</div></details>')

blog_cards = []
for post in posts:
    blog_cards.append(f'''<article class="blog-entry">
      <div class="paper-media"><video class="paper-video" controls muted loop playsinline preload="metadata" poster="{e(post['poster'])}" aria-label="{e(post['title'])} — official project video"><source src="{e(post['video'])}" type="video/mp4">{external(post['video'], 'Watch project video')}</video><span class="media-caption">{e(post['video_caption'])}</span></div>
      <div class="blog-content"><div class="paper-meta"><span class="venue conference">{e(post['label'])}</span><span class="blog-publisher">{e(post['publisher'])}</span></div><h3>{external(post['url'], e(post['title']))}</h3><p>{e(post['summary'])}</p><div class="paper-links">{external(post['url'], 'Read Blog <span aria-hidden="true">↗</span>')}{external(post['code'], 'Code <span aria-hidden="true">↗</span>')}</div></div>
    </article>''')

news = []
for pid, date, title in [('argus', '2026 / 08', 'Argus'), ('mage-flow', '2026 / 07', 'Mage-Flow'), ('resource2skill', '2026 / 06', 'RESOURCE2SKILL'), ('unig2u', '2026 / 03', 'UniG2U-Bench')]:
    p = next(p for p in papers if p['id'] == pid)
    news.append(f'<li><time datetime="{date.replace(" / ", "-")}">{date}</time><span>{external("https://arxiv.org/abs/"+p["arxiv"], "<strong>"+title+"</strong>")} preprint is available on arXiv.</span></li>')

github_icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.86c-2.78.6-3.37-1.18-3.37-1.18-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.89 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.64-1.34-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02A9.5 9.5 0 0 1 12 6.82a9.5 9.5 0 0 1 2.5.34c1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.69-4.57 4.94.36.31.68.92.68 1.85v2.75c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"/></svg>'
scholar_icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m2 9 10-6 10 6-10 6L2 9Zm4 3v6c4 3 8 3 12 0v-6M22 9v8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
social = external(profile['scholar'], scholar_icon+'Google Scholar', 'social-link') + external(profile['github'], github_icon+'GitHub', 'social-link')
if profile.get('email'):
    social += f'<a class="social-link" href="mailto:{e(profile["email"], quote=True)}">Email ↗</a>'

html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(profile['name'])} ({e(profile['handle'])}) | Academic Homepage</title>
  <meta name="description" content="Zimo Wen (nssmd), Shanghai Jiao Tong University. Research in embodied AI, agentic systems, multimodal learning, and time-series modeling.">
  <meta name="theme-color" content="#ffffff"><meta property="og:title" content="Zimo Wen · nssmd"><meta property="og:description" content="Research, publications, and projects at Shanghai Jiao Tong University."><meta property="og:type" content="website"><meta property="og:url" content="https://nssmd.github.io/"><meta property="og:image" content="https://nssmd.github.io/assets/avatar.png"><link rel="canonical" href="https://nssmd.github.io/">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"><script src="script.js" defer></script>
</head>
<body id="top">
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="container">
    <nav class="top-nav" aria-label="Main navigation"><a class="wordmark" href="#top">{e(profile['handle'])}<span>.</span></a><div><a href="#about">About</a><a href="#news">News</a><a href="#blog">Blog</a><a href="#research">Research</a></div></nav>
    <header class="profile-header">
      <div class="profile-copy"><p class="eyebrow">RESEARCH · LEARNING · EXPLORATION</p><h1>{e(profile['name'])}</h1><p class="handle">@{e(profile['handle'])}</p><p class="affiliation">{external(profile['affiliation_url'], e(profile['affiliation']))}</p><p class="research-line">Embodied AI &amp; beyond.</p><div class="social-links">{social}</div></div>
      <div class="portrait-wrap"><img class="portrait" src="assets/avatar.png" alt="{e(profile['name'])}'s GitHub avatar" width="260" height="260"><span class="portrait-caption">Stay curious. Keep building.</span></div>
    </header>
    <main id="main">
      <section id="about" aria-labelledby="about-title"><h2 id="about-title" class="section-title">Biography</h2><p class="biography">{e(profile['bio'])}</p><div class="interests">{''.join('<span>'+e(x)+'</span>' for x in profile['interests'])}</div></section>
      <section id="news" aria-labelledby="news-title"><h2 id="news-title" class="section-title">News <span class="section-note">Recent research updates</span></h2><ul class="news-list">{''.join(news)}</ul></section>
      <section id="blog" aria-labelledby="blog-title"><h2 id="blog-title" class="section-title">Blog <span class="section-note">Research in practice</span></h2>{''.join(blog_cards)}</section>
      <section id="research" aria-labelledby="research-title"><h2 id="research-title" class="section-title">Research &amp; Publications <span class="section-note">2025 — 2026</span></h2><div class="research-intro"><p>A selection of questions I’ve been working on.</p>{external(profile['scholar'], 'Full list on Scholar ↗')}</div>
        <div class="research-tools" hidden><div class="year-filters" role="group" aria-label="Filter publications by year"><button class="active" data-year="all" aria-pressed="true">All years</button><button data-year="2026" aria-pressed="false">2026</button><button data-year="2025" aria-pressed="false">2025</button></div><label class="search-label"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><span class="sr-only">Search publications</span><input type="search" id="paper-search" placeholder="Search publications…" autocomplete="off"></label></div>
        <p class="sr-only" id="filter-status" role="status" aria-live="polite"></p><div id="publication-list">{''.join(groups)}</div><p id="no-results" hidden>No publications match your search. Try another keyword or year.</p>
      </section>
    </main>
    <footer><div><a class="footer-name" href="#top">{e(profile['name'])}<span> / {e(profile['handle'])}</span></a><p>Last updated · {e(profile['updated'])}</p></div><a class="back-top" href="#top">Back to top ↑</a></footer>
  </div>
</body>
</html>
'''
(ROOT / 'index.html').write_text(html)
print(f'Built index.html with {len(papers)} publications and {len(posts)} blog posts.')
