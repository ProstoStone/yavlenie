from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from xml.etree import ElementTree as ET
import json
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
