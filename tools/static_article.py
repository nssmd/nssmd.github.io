"""Static public article; the full interactive copy is written separately for review."""
from pathlib import Path
from html import escape
from bs4 import BeautifulSoup
import json

def make_static(html,root):
    s=BeautifulSoup(html,'html.parser')
    for tag in list(s.find_all('script')):
        if tag.get('type')!='application/ld+json':tag.decompose()
    for node in list(s.select('button,input,dialog,.case-filters,.selection-review,.review-toast,.review-dock')):node.decompose()
    for video in list(s.find_all('video')):
        poster=video.get('poster');source=video.find('source');url=(source.get('src') or source.get('data-src')) if source else None
        if not poster:video.decompose();continue
        wrap=s.new_tag('div',attrs={'class':'static-video-cover'});a=s.new_tag('a',href=url or '#',target='_blank',rel='noopener');im=s.new_tag('img',src=poster,alt=video.get('aria-label','Recorded robot execution'),width='960',height='540');a.append(im);wrap.append(a)
        if url:label=s.new_tag('a',href=url,target='_blank',rel='noopener',attrs={'class':'static-watch'});label.string='Watch the recorded execution ↗';wrap.append(label)
        video.replace_with(wrap)
    for details in list(s.select('.case-plan')):
        camera=details.find('a');p=s.new_tag('p',attrs={'class':'static-case-link'})
        if camera:camera.attrs.pop('data-camera-title',None);p.append(camera.extract())
        details.replace_with(p)
    data=json.loads((root/'blog/assets/compass/scenecode-traces.json').read_text())
    for study in s.select('[data-sync-case]'):
        task=study['data-sync-case'];trace=data[task];updates=trace['updates'];indices=list(dict.fromkeys([0,len(updates)//2,len(updates)-1]));grid=study.select_one('.sync-grid');sequence=s.new_tag('div',attrs={'class':'static-sequence'})
        for i in indices:
            state=updates[i];row=s.new_tag('section',attrs={'class':'static-step'});fig=s.new_tag('figure');img=s.new_tag('img',src=f'/blog/assets/compass/{task}-step-{state["step"]}.webp',alt=f'Recorded execution at {state["time"]:.2f} seconds',width='640',height='360');fig.append(img);cap=s.new_tag('figcaption');cap.string=f'{state["time"]:.2f}s · recorded review';fig.append(cap);p=s.new_tag('p',attrs={'class':'static-progress'});p.string=state['progress'];fig.append(p);row.append(fig);copy=s.new_tag('div',attrs={'class':'static-step-copy'});p=s.new_tag('p',attrs={'class':'mini-label'});p.string='SCENECODE UPDATE';copy.append(p);pre=s.new_tag('pre');code=s.new_tag('code');code.string=json.dumps({'next_command':state['commands'][0] if state['commands'] else None,'expect':state['expect']},indent=2);pre.append(code);copy.append(pre);row.append(copy);sequence.append(row)
        p=s.new_tag('p',attrs={'class':'static-study-video'});a=s.new_tag('a',href=f'/blog/assets/compass/{task}-scenecode.mp4',target='_blank',rel='noopener');a.string='Watch the full execution with SceneCode alongside ↗';p.append(a);sequence.append(p);grid.replace_with(sequence);study.attrs.pop('data-sync-case',None)
    for p in s.select('.article-body>p'):
        text=p.get_text(' ',strip=True)
        if text.startswith('These case studies pair the robot'):
            p.clear();p.append('The following case studies show successive recorded reviews. Each keyframe is paired with the current SceneCode command and expected outcomes, so the progression can be read from top to bottom. Full synchronized recordings are linked below each case.')
        elif text.startswith('Each study also includes a'):
            p.clear();p.append('The linked recordings show the execution and changing SceneCode side by side.')
        elif 'Open a case to read its SceneCode plan' in text:
            p.clear();p.append('Ordering, memory, object selection, precision, and coordination put different demands on the robot. These recorded COMPASS executions show how the task requirements become concrete actions. Each example includes a link to its execution video.')
    for a in s.find_all('a'):
        if a.get_text(' ',strip=True)=='SceneCode in motion ↓':a.clear();a.append('Case studies ↓')
    heading=s.find(id='case-studies')
    if heading:heading.clear();heading.append('Case studies: SceneCode through execution')
    for c in s.select('.sync-options,.replay-timeline,.code-tabs,.scene-anchors'):c.decompose()
    return str(s)

def static_index(html):
    s=BeautifulSoup(html,'html.parser')
    for node in list(s.select('.journal-search,#post-empty,#post-status')):node.decompose()
    for tag in list(s.find_all('script')):
        if tag.get('type')!='application/ld+json':tag.decompose()
    return str(s)
