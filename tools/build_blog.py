"""Build the journal and Markdown posts: python tools/build_blog.py."""
from pathlib import Path
from html import escape as esc
from datetime import datetime
import json,re,math
import markdown,yaml
from compass_components import components,DOC

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://nssmd.github.io'
BLOG=ROOT/'blog'

def shell(title,description,url,body,kind='website',cover='/assets/avatar.png'):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Zimo Wen</title><meta name="description" content="{esc(description,quote=True)}">
<link rel="canonical" href="{ORIGIN}{url}"><meta property="og:title" content="{esc(title,quote=True)}"><meta property="og:description" content="{esc(description,quote=True)}"><meta property="og:type" content="{kind}"><meta property="og:url" content="{ORIGIN}{url}"><meta property="og:image" content="{ORIGIN}{cover}"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#ffffff">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/atom+xml" title="Zimo Wen — Blog" href="/blog/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;450;500;550;600;650;700&family=Source+Serif+4:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/blog/blog.css"><script src="/blog/blog.js" defer></script></head>
<body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><a class="wordmark" href="/">Zimo Wen<span class="wordmark-dot">.</span></a><nav aria-label="Main navigation"><a href="/">Home</a><a href="/#research">Research</a><a href="/blog/" aria-current="page">Blog</a><a class="rss-link" href="/blog/feed.xml" aria-label="Subscribe via RSS"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="5" cy="15" r="1" fill="currentColor"/><path d="M4 8a8 8 0 0 1 8 8M4 3a13 13 0 0 1 13 13"/></svg></a></nav></header>
{body}<footer class="site-footer"><a href="/">Zimo Wen · @nssmd</a><span>Research, notes, and things in progress.</span><a href="#top">Back to top ↑</a></footer></body></html>'''

def video(case,hero=False):
    return f'''<video class="case-video{' hero-video' if hero else ''}" controls muted loop playsinline preload="none" poster="{case['poster']}" aria-label="{esc(case['title'],quote=True)}"><source data-src="{case['video']}" type="video/mp4"><a href="{case['video']}">Watch the execution</a></video>'''

def bridge():
    return '''<figure class="bridge-figure"><div class="bridge-flow"><div class="bridge-node"><span class="mini-label">SYSTEM 2</span><h3>Reason & plan</h3><p>Understand the context.<br>Choose the next goal.</p></div><span class="bridge-arrow" aria-hidden="true">→</span><div class="bridge-node bridge-program"><span class="mini-label">THE SHARED PROGRAM</span><h3>SceneCode</h3><div class="program-fields"><span>objects</span><span>goals</span><span>steps</span><span>checks</span></div></div><span class="bridge-arrow" aria-hidden="true">→</span><div class="bridge-node"><span class="mini-label">SYSTEM 1</span><h3>Act in the world</h3><p>Follow grounded targets<br>through learned embeddings.</p></div></div><div class="feedback-path"><span>↶</span> Observe the result. Update the program. Continue.</div><figcaption>COMPASS connects the reasoning model and action policy through SceneCode.</figcaption></figure>'''

def gallery(cases):
    cats=list(dict.fromkeys(c['category'] for c in cases))
    filters='<button class="active" data-case-filter="all" aria-pressed="true">All cases <span>'+str(len(cases))+'</span></button>'+''.join(f'<button data-case-filter="{esc(cat)}" aria-pressed="false">{esc(cat)}</button>' for cat in cats)
    cards=[]
    for i,c in enumerate(cases,1):
        plans=''.join('<li>'+esc(step)+'</li>' for step in c['plan'])
        cards.append(f'''<article class="case-card" data-category="{esc(c['category'])}" id="case-{c['id']}"><div class="case-media">{video(c)}<span class="case-number">{i:02}</span></div><div class="case-copy"><span class="mini-label">{esc(c['category'])}</span><h3>{esc(c['title'])}</h3><p>{esc(c['description'])}</p><details class="case-plan"><summary>View SceneCode plan <span aria-hidden="true">↗</span></summary><ol>{plans}</ol><a class="camera-link" href="{c['all_cameras']}" data-camera-title="{esc(c['title'],quote=True)}">Watch all three cameras ↗</a></details></div></article>''')
    return f'''<div class="case-gallery wide"><div class="case-filters" role="group" aria-label="Filter execution cases">{filters}</div><p class="sr-only" role="status" id="case-status" aria-live="polite">{len(cases)} cases</p><div class="case-grid">{''.join(cards)}</div></div>'''

def build():
    posts=[]
    for path in sorted((ROOT/'content/blog').glob('*.md')):
        text=path.read_text();parts=text.split('---',2)
        if len(parts)!=3:raise ValueError(f'{path}: use YAML front matter between --- lines')
        meta=yaml.safe_load(parts[1]);body=parts[2]
        if not meta.get('published',True):continue
        slug=str(meta['slug'])
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise ValueError('Invalid post slug: '+slug)
        date=str(meta['date']);datetime.strptime(date,'%Y-%m-%d')
        if date>datetime.now().strftime('%Y-%m-%d'):continue
        md=markdown.Markdown(extensions=['extra','toc','codehilite'],extension_configs={'toc':{'permalink':False},'codehilite':{'guess_lang':False}})
        rendered=md.convert(body)
        if '<!-- COMPASS_GALLERY -->' in rendered:
            cases=json.loads((BLOG/'assets/compass/cases.json').read_text())
            rendered=rendered.replace('<!-- COMPASS_GALLERY -->',gallery(cases)).replace('<!-- COMPASS_BRIDGE -->',bridge())
            case=cases[0]
            excerpt=json.dumps({'program':case['plan'],'goal_state':case['goal_state']},indent=2)
            rendered=rendered.replace('<!-- SCENECODE_EXCERPT -->','<figure class="recorded-code"><div class="code-caption">SceneCode · recorded execution</div><pre><code>'+esc(excerpt)+'</code></pre><figcaption>A compact excerpt from the color-order stacking case.</figcaption></figure>')
            for marker,value in components(ROOT).items():rendered=rendered.replace(marker,value)
            rendered+='<a class="review-dock" href="'+DOC+'" target="_blank" rel="noopener" data-review-open>Comment in Google Doc ↗</a><a class="selection-review" href="'+DOC+'" target="_blank" rel="noopener" hidden>Copy quote & open Doc ↗</a><div class="review-toast" role="status" aria-live="polite"></div>'
        words=len(re.findall(r'\b\w+\b',re.sub('<[^>]+>',' ',rendered)));minutes=max(1,math.ceil(words/220))
        post={**meta,'date':date,'url':'/blog/'+slug+'/','html':rendered,'toc':md.toc,'minutes':minutes,'source':path.name}
        posts.append(post)
    posts.sort(key=lambda p:p['date'],reverse=True)
    for post in posts:
        title=post['title'];url=post['url'];date=datetime.strptime(post['date'],'%Y-%m-%d').strftime('%B %d, %Y');cover=post.get('cover','/assets/avatar.png')
        wordmark=post.get('wordmark',title);subtitle=post.get('subtitle','');description=post['description']
        actions='<a class="pill-button primary" href="#pipeline">How it works <span>↓</span></a><a class="pill-button" href="#case-studies">SceneCode in motion ↓</a><a class="pill-button" href="'+DOC+'" target="_blank" rel="noopener">Google Doc ↗</a>' if post['slug']=='compass' else ''
        hero=''
        if post.get('hero_video'):
            hero=f'<figure class="hero-film"><video controls muted loop playsinline preload="metadata" poster="{cover}" aria-label="{esc(title,quote=True)}"><source src="{post["hero_video"]}" type="video/mp4"></video><figcaption>{esc(post.get("hero_caption",""))}</figcaption></figure>'
        schema=json.dumps({'@context':'https://schema.org','@type':'BlogPosting','headline':title,'description':description,'datePublished':post['date'],'author':{'@type':'Person','name':'Zimo Wen','url':ORIGIN},'image':ORIGIN+cover,'mainEntityOfPage':ORIGIN+url}).replace('<','\\u003c')
        content=f'''<main id="main"><article id="top"><header class="article-hero"><div class="eyebrow">{esc(post.get('category','Notes'))}<span>·</span><time datetime="{post['date']}">{date}</time></div><h1>{esc(wordmark)}</h1><p class="hero-subtitle">{esc(subtitle)}</p><p class="hero-description">{esc(description)}</p><div class="hero-actions">{actions}</div></header>{hero}<div class="article-layout"><aside class="article-toc" aria-label="On this page"><span class="mini-label">IN THIS ARTICLE</span>{post['toc']}<a href="/blog/" class="back-link">← All writing</a></aside><div class="article-body">{post['html']}</div></div><section class="article-end"><span class="mini-label">KEEP EXPLORING</span><h2>More from the notebook.</h2><a href="/blog/" class="pill-button">All writing ↗</a></section></article></main><script type="application/ld+json">{schema}</script><dialog id="camera-dialog"><button class="dialog-close" aria-label="Close video">×</button><h2></h2><video controls playsinline></video></dialog>'''
        out=BLOG/post['slug'];out.mkdir(exist_ok=True);(out/'index.html').write_text(shell(title,description,url,content,'article',cover))
    cards=[]
    for i,p in enumerate(posts):
        tags=''.join('<span>'+esc(t)+'</span>' for t in p.get('tags',[]))
        cards.append(f'''<article class="post-card{' featured-post' if i==0 else ''}" data-search="{esc((p['title']+' '+p['description']+' '+' '.join(p.get('tags',[]))).lower(),quote=True)}"><a class="post-image" href="{p['url']}"><img src="{p.get('cover','/assets/avatar.png')}" alt="{esc(p.get('cover_alt',p['title']),quote=True)}" width="960" height="540"><span class="image-label">RESEARCH NOTE</span></a><div class="post-copy"><div class="eyebrow">{esc(p.get('category','Notes'))}<span>·</span>{p['date']}</div><h2><a href="{p['url']}">{esc(p['title'])}</a></h2><p>{esc(p['description'])}</p><div class="post-tags">{tags}</div><a class="read-post" href="{p['url']}">Read the story <span>↗</span></a></div></article>''')
    body=f'''<main id="main" class="journal" tabindex="-1"><section class="journal-hero" id="top"><div class="eyebrow">THE NOTEBOOK <span> / </span> ZIMO WEN</div><h1>Research.<br>Notes.<br><em>Things in progress.</em></h1><p>Early ideas, paper notes, and reflections on research.</p><div class="journal-topics"><span>Ideas</span><span>Paper notes</span><span>Reflections</span></div><div class="journal-mark" aria-hidden="true"><span>n</span><i>01 / ∞</i></div></section><section class="writing-section" aria-labelledby="writing-heading"><div class="writing-heading"><h2 id="writing-heading">Latest writing <span>{len(posts):02}</span></h2><label class="journal-search"><span class="sr-only">Search articles</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10" cy="10" r="6.5"/><path d="m15 15 5 5"/></svg><input id="post-search" type="search" placeholder="Find an idea or note…" autocomplete="off"></label></div><div class="post-list">{''.join(cards)}</div><p class="empty-search" id="post-empty" hidden>No matching notes. Try another keyword.</p><p class="sr-only" id="post-status" role="status" aria-live="polite"></p></section><section class="journal-signoff"><p>Good ideas tend to start<br>as a note to yourself.</p><a href="/blog/feed.xml">Follow the notebook <span>↗</span></a></section></main>'''
    (BLOG/'index.html').write_text(shell('Blog','Research notes and experiments by Zimo Wen.','/blog/',body,cover=posts[0].get('cover','/assets/avatar.png') if posts else '/assets/avatar.png'))
    updated=posts[0]['date']+'T00:00:00Z' if posts else datetime.now().strftime('%Y-%m-%dT00:00:00Z')
    entries=''.join(f'<entry><title>{esc(p["title"])}</title><id>{ORIGIN}{p["url"]}</id><link href="{ORIGIN}{p["url"]}"/><updated>{p["date"]}T00:00:00Z</updated><summary>{esc(p["description"])}</summary></entry>' for p in posts)
    (BLOG/'feed.xml').write_text(f'<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>Zimo Wen — Blog</title><id>{ORIGIN}/blog/</id><link href="{ORIGIN}/blog/feed.xml" rel="self"/><link href="{ORIGIN}/blog/"/><updated>{updated}</updated><author><name>Zimo Wen</name></author>{entries}</feed>')
    print(f'Built blog index, {len(posts)} articles, and Atom feed.')

if __name__=='__main__':build()
