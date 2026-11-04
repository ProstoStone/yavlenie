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
import hashlib
# Editorial regression guard; does not depend on Git checkout depth.
PRESERVED_RUSSIAN = {'freedom': 'e20c0110e070cefdfc6aad07ce69b9a4ddc0a8bf9fdb85223dcc6de93bac27bb', 'fear': '6f61a451e44f7ad08b6eb27cd5865f6c0cd062a942afcef072ab837219efbcc8', 'mistakes': '35355e9d7cfa5f8a602d86300f4902780c05e2f2bf3fae596165b89e77d79ada', 'start': '222649ed75142eef993804f7337ace862ed7ad2aa192e0d668ae72dbf1068e31', 'glossary': '2fc304b513f3561066c341e8411aff9513048479485864ac2425f61d4a1e04ba'}
for slug,digest in PRESERVED_RUSSIAN.items():
 assert hashlib.sha256((ROOT/"content"/(slug+".md")).read_bytes()).hexdigest()==digest,slug
expected=['Everything is one phenomenon.','The phenomenon is sensory experiencing.','A distinction within sensory experiencing is a concept.','Concepts structure the phenomenon into experience.','Experience is the phenomenon structured through concepts.']
s=(ROOT/'content/en/start.md').read_text()
assert all(f'{i}. {t}' in s for i,t in enumerate(expected,1))
# A bilingual glossary must preserve the exact five foundational theses and matching sections.
ru_glossary=(ROOT/'content/glossary.md').read_text()
en_glossary=(ROOT/'content/en/glossary.md').read_text()
ru_theses=['Всё есть одно явление.','Явление есть чувственное переживание.','Различение в чувственном переживании есть концепция.','Концепции структурируют явление в опыт.','Опыт есть явление, структурированное через концепции.']
assert all(f'{i}. {t}' in ru_glossary for i,t in enumerate(ru_theses,1))
assert all(f'{i}. {t}' in en_glossary for i,t in enumerate(expected,1))
ru_count=len(re.findall(r'^## ',ru_glossary,re.M))
en_count=len(re.findall(r'^## ',en_glossary,re.M))
assert ru_count==en_count and ru_count>=20,(ru_count,en_count)
# Third essay in the sequence: exact thesis wording and matching bilingual structure.
ru_weight=(ROOT/'content/weightlessness.md').read_text()
en_weight=(ROOT/'content/en/weightlessness.md').read_text()
assert all(f'{i}. {t}' in ru_weight for i,t in enumerate(ru_theses,1))
assert all(f'{i}. {t}' in en_weight for i,t in enumerate(expected,1))
assert len(re.findall(r'^## ',ru_weight,re.M))==len(re.findall(r'^## ',en_weight,re.M))>=12
assert 'Множество вещей. Множество различий.<br>Одно явление.' in (ROOT/'build.py').read_text()
assert 'Many things. Many distinctions.<br>One phenomenon.' in (ROOT/'build.py').read_text()
assert len(ET.parse(OUT/'sitemap.xml').getroot())==2*(len(ORDER)+2)
print('OK: bilingual pairing, language metadata, sitemap URLs, four figures per language, original Russian texts and five English theses preserved')
