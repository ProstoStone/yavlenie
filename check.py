from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from xml.etree import ElementTree as ET
import json,re
from build import OUT,BASE,PREFIX
class Page(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set();self.h1=0;self.canon=[];self.json=False;self.scripts=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  if t=='h1':self.h1+=1
  if t=='link' and a.get('rel')=='canonical':self.canon.append(a['href'])
  for k in ('href','src'):
   if k in a:self.links.append(a[k])
  if t=='script':assert a.get('type')=='application/ld+json';self.json=True
 def handle_endtag(self,t):
  if t=='script':self.json=False
 def handle_data(self,s):
  if self.json:json.loads(s)
pages={}
for p in OUT.rglob('*.html'):
 q=Page();q.feed(p.read_text());assert q.h1==1,(p,q.h1);assert len(q.canon)==1;p.resolve();pages[p.resolve()]=q
for p,q in pages.items():
 for href in q.links:
  u=urlsplit(href)
  if u.netloc and not href.startswith(BASE):continue
  path=u.path
  if path.startswith(PREFIX):target=OUT/unquote(path[len(PREFIX):])
  elif path.startswith('/'):raise AssertionError(('wrong base',href))
  else:target=p.parent/path if path else p
  if target.is_dir():target=target/'index.html'
  assert target.exists(),(p,href,target)
  if u.fragment and target.suffix=='.html':assert u.fragment in pages[target.resolve()].ids,(p,href)
for f in ('sitemap.xml','feed.xml'):ET.parse(OUT/f)
catalog=json.loads((OUT/'catalog.json').read_text());assert len(catalog['items'])>=6
print(f'OK: {len(pages)} pages, local links, anchors, JSON-LD, sitemap, RSS, catalog')
# Every translated page must identify itself and its matching counterpart.
from build import items,ORDER,url,ROOT
for lang in ('ru','en'):
 for path in ['', 'catalog/']+[s+'/' for s in ORDER]:
  rel=('en/' if lang=='en' else '')+path+'index.html'
  s=(OUT/rel).read_text()
  assert f'<html lang="{lang}">' in s
  assert f'rel="canonical" href="{url(lang,path)}"' in s
  for other in ('ru','en'):
   assert f'hreflang="{other}" href="{url(other,path)}"' in s
  assert 'noindex' not in s
  assert '{{figure:' not in s
 for f in ('feed.xml','catalog.json','llms.txt'):
  assert (OUT/('en' if lang=='en' else '')/f).exists()
 for slug in ORDER:
  p=OUT/('en' if lang=='en' else '')/slug/'index.html'
  s=p.read_text()
  assert '"inLanguage": "'+lang+'"' in s
  assert '"author"' not in s
  assert 'model'+('_en' if lang=='en' else '')+'-1.html' in s
  assert len(re.findall('<figure',s))==(4 if slug=='gradient' else 0)
import subprocess
for slug in ['freedom','fear','mistakes','start','glossary']:
 original=subprocess.check_output(['git','show','27d1b1c:content/'+slug+'.md'],cwd=ROOT).decode()
 assert (ROOT/'content'/f'{slug}.md').read_text()==original,slug
expected=['Everything is one phenomenon.','The phenomenon is sensory experiencing.','A distinction within sensory experiencing is a concept.','Concepts structure the phenomenon into experience.','Experience is the phenomenon structured through concepts.']
s=(ROOT/'content/en/start.md').read_text()
assert all(f'{i}. {t}' in s for i,t in enumerate(expected,1))
assert len(ET.parse(OUT/'sitemap.xml').getroot())==22
print('OK: bilingual pairing, language metadata, 22 indexed URLs, four figures per language, original Russian texts and five English theses preserved')
