"""Build the static homepage: python build.py (standard library only)."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
profile = json.loads((ROOT / 'data/profile.json').read_text())
papers = json.loads((ROOT / 'data/publications.json').read_text())
updates = json.loads((ROOT / 'data/news.json').read_text())
experience = json.loads((ROOT / 'data/experience.json').read_text())
community = json.loads((ROOT / 'data/community.json').read_text())
e = escape

ICONS = {
    'github': '<path fill="currentColor" d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.86c-2.78.6-3.37-1.18-3.37-1.18-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.89 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.64-1.34-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02A9.5 9.5 0 0 1 12 6.82a9.5 9.5 0 0 1 2.5.34c1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.69-4.57 4.94.36.31.68.92.68 1.85v2.75c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"/>',
    'scholar': '<path d="m2 9 10-6 10 6-10 6L2 9Zm4 3v6c4 3 8 3 12 0v-6M22 9v8"/>',
    'paper': '<path d="M5 2h9l5 5v15H5V2Zm9 0v6h5M8 12h8M8 16h8"/>',
    'website': '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
    'agent': '<rect x="4" y="7" width="16" height="14" rx="3"/><path d="M12 7V3M10 3h4M2 12h2m16 0h2M9 16h6"/><circle cx="8" cy="12" r="1"/><circle cx="16" cy="12" r="1"/>',
    'image': '<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8" cy="8" r="2"/><path d="m3 17 6-6 4 4 3-3 5 5"/>',
    'chart': '<path d="M3 3v18h18M6 16l4-7 4 4 6-8"/>',
    'video': '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="m10 8 6 4-6 4V8Z"/>',
}

def icon(name, cls=''):
    return f'<svg class="icon {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

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
    equal_count = p.get('equal_contribution_count', 0)
    authors = ', '.join(
        e(name).replace('Zimo Wen', '<strong>Zimo Wen</strong>').replace('Z Wen', '<strong>Z Wen</strong>').replace('...', 'et al.')
        + ('<sup title="Equal contribution">*</sup>' if i < equal_count else '')
        for i, name in enumerate(p['authors'].split(', '))
    )
    if equal_count:
        authors += ' <span class="equal-contribution-note">(* equal contribution)</span>'
    url = p['paper']
    links = external(url, icon('paper')+e(p.get('paper_label', 'Paper')))
    for key, label in [('website', 'Website'), ('code', 'Code'), ('models', 'Models'), ('video_url', 'Video')]:
        if p.get(key):
            links += external(p[key], icon({'website':'website', 'code':'github', 'models':'website', 'video_url':'video'}[key])+label)
    if p.get('scholar'):
        links += external(p['scholar'], icon('scholar')+'Scholar')
    if p.get('video'):
        media = f'<div class="paper-media"><video class="paper-video publogo" controls muted loop playsinline preload="metadata" poster="{e(p["poster"])}" aria-label="{e(p["title"])} — official project video"><source src="{e(p["video"])}" type="video/mp4">{external(p["video"], "Watch project video")}</video><span class="media-caption">{e(p.get("video_note", "Project video"))}</span></div>'
    else:
        img = p.get('image', f'assets/{p["id"]}.svg')
        media = f'<a class="paper-image" href="{e(p.get("website", url))}" target="_blank" rel="noopener noreferrer" aria-label="View {e(p["title"])}"><img class="publogo" src="{e(img)}" width="520" height="340" alt="{e(p["id"])} research overview" loading="lazy"></a>'
    badge_style = 'techreport' if 'Report' in p['badge'] else ('submitted' if p['badge'].startswith('arXiv') else 'accepted')
    return f'''<article class="publication paper" id="{e(p['id'])}" data-year="{p['year']}">
      {media}
      <div class="pub-content"><strong class="paper-title">{external(url, e(p['title']))}</strong><div class="authors">{authors}</div><div class="affiliation"><span>{e(p['topic'])}</span><span class="venue-badge {badge_style}">{e(p['badge'])}</span></div><div class="links paper-links">{links}</div></div>
    </article>'''

groups = []
for i, category in enumerate(dict.fromkeys(p['category'] for p in papers), 1):
    items = [p for p in papers if p['category'] == category]
    cat_icon = {'Agentic Systems':'agent', 'Robotics':'agent', 'Multimodal Learning':'image', 'Time Series & Dynamics':'chart', 'Technical Reports':'paper'}[category]
    groups.append(f'<details class="category" open><summary class="category-title">{icon(cat_icon, "cat-icon")}<span>{e(category)}</span><span class="category-count count">{len(items)}</span><span class="chevron" aria-hidden="true">›</span></summary><div class="category-body">{"".join(card(p) for p in items)}</div></details>')

news = []
for update in updates:
    p = next(p for p in papers if p['id'] == update['id'])
    news.append(f'<li><time class="news-date" datetime="{e(update["date"])}">{e(update["date"].replace("-", "/"))}</time><span>{external(p["paper"], "<strong>"+e(update["title"])+"</strong>")} {e(update["text"])}</span></li>')

experience_rows = ''.join(f'<li class="experience-item"><div class="exp-details"><strong>{e(item["place"])}</strong><span>{e(item["role"])}</span><span class="exp-focus">{e(item["focus"])}</span></div><div class="exp-date">{e(item["date"])}</div></li>' for item in experience)
community_rows = ''.join(f'<li class="experience-item"><div class="exp-details"><strong>{external(item["url"],e(item["name"]))}{", "+e(item["role"]) if item["role"] else ""}</strong><span class="community-description">{e(item["description"])}</span></div></li>' for item in community)

social = external(profile['github'], icon('github')+'GitHub', 'social-link') + external(profile['scholar'], icon('scholar')+'Google Scholar', 'social-link')
contact = ''
if profile.get('email'):
    contact = f'<div class="contact-info">Email: <a href="mailto:{e(profile["email"], quote=True)}">{e(profile["email"])}</a></div>'

html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(profile['name'])} ({e(profile['handle'])}) | Academic Homepage</title>
  <meta name="description" content="Zimo Wen (nssmd), Shanghai Jiao Tong University. Research in embodied AI, agentic systems, multimodal learning, and time-series modeling.">
  <meta name="theme-color" content="#ffffff"><meta property="og:title" content="Zimo Wen · nssmd"><meta property="og:description" content="Research, publications, and projects at Shanghai Jiao Tong University."><meta property="og:type" content="website"><meta property="og:url" content="https://nssmd.github.io/"><meta property="og:image" content="https://nssmd.github.io/assets/avatar.png"><link rel="canonical" href="https://nssmd.github.io/">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="custom.css"><script src="script.js" defer></script>
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Merriweather:ital,wght@0,300;0,700;1,300&display=swap" rel="stylesheet">
</head>
<body id="top">
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="container">
    <header class="profile-header">
      <div class="bio-text"><h1>{e(profile['name'].upper())}</h1><div class="role-title"><b>{e(profile['role'])}</b><br>{external(profile['affiliation_url'], e(profile['affiliation']))}<br><span class="profile-program">{e(profile['program'])}</span></div>{contact}<div class="social-links">{social}</div><nav class="section-nav" aria-label="Main navigation"><a href="#research">Research</a><a href="#experience">Experience</a><a href="#community">Community</a><span>@{e(profile['handle'])}</span></nav></div>
      <div class="profile-image-container"><img class="profile-photo" src="assets/avatar.png" alt="{e(profile['name'])}'s GitHub avatar" width="300" height="300"></div>
    </header>
    <main id="main">
      <section id="about" aria-labelledby="about-title"><h2 id="about-title" class="section-title">Biography</h2><p class="biography">{e(profile['bio'])}</p></section>
      <section id="news" aria-labelledby="news-title"><h2 id="news-title" class="section-title">News</h2><ul class="news-scroll">{''.join(news)}</ul></section>
      <section id="research" aria-labelledby="research-title"><h2 id="research-title" class="section-title">Selected Projects</h2>
        <div class="research-tools" hidden><div class="year-filters" role="group" aria-label="Filter publications by year"><button class="active" data-year="all" aria-pressed="true">All years</button><button data-year="2026" aria-pressed="false">2026</button><button data-year="2025" aria-pressed="false">2025</button></div><label class="search-label"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><span class="sr-only">Search publications</span><input type="search" id="paper-search" placeholder="Search publications…" autocomplete="off"></label></div>
        <p class="sr-only" id="filter-status" role="status" aria-live="polite"></p><div id="publication-list">{''.join(groups)}</div><p id="no-results" hidden>No publications match your search. Try another keyword or year.</p>
      </section>
      <section id="experience" aria-labelledby="experience-title"><h2 id="experience-title" class="section-title">Experience</h2><ul class="experience-list">{experience_rows}</ul></section>
      <section id="community" aria-labelledby="community-title"><h2 id="community-title" class="section-title">Community Contribution</h2><ul class="experience-list">{community_rows}</ul></section>
    </main>
    <footer><p>{e(profile['name'])} · @{e(profile['handle'])}<br>Updated {e(profile['updated'])}</p><p>Website adapted from {external('https://github.com/WayneJin0918/home', 'Weiyang Jin')} · <a href="#top">Back to top ↑</a></p></footer>
  </div>
</body>
</html>
'''
(ROOT / 'index.html').write_text(html)
print(f'Built index.html with {len(papers)} research entries and {len(updates)} news items.')
