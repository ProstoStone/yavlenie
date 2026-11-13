from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from xml.etree import ElementTree as ET
import json,re
from build import OUT,BASE,PREFIX
from pdf_export import pdf_path
class Page(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set();self.h1=0;self.canon=[];self.json=False;self.scripts=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  if t=='h1':self.h1+=1
  if t=='link' and a.get('rel')=='canonical':self.canon.append(a['href'])
  for k in ('href','src'):
   if k in a:self.links.append(a[k])
  if t=='script':
   self.json=a.get('type')=='application/ld+json'
   assert self.json or (a.get('id')=='reading-theme' and 'src' not in a) or (
    a.get('src')==PREFIX+'assets/reader-audio.js?v=audio-reader-20261112' and 'defer' in a
   )
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
  if u.scheme not in ('','http','https'):continue
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
from build import items,ORDER,url,ROOT,WORK_PATHS
ALL_SLUGS=[a["slug"] for a in items if a["lang"]=="ru"]
for lang in ('ru','en'):
 for path in ['', 'catalog/', 'works/']+[s+'/' for s in ALL_SLUGS]+WORK_PATHS:
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
  if slug=='ya-mir-drugie':
   assert '"author":' in s and '"copyrightHolder":' in s
   assert ('Роман Дудников' if lang=='ru' else 'Roman Dudnikov') in s
  else:assert '"author"' not in s
  assert 'model'+('_en' if lang=='en' else '')+'-1.html' in s
  assert len(re.findall('<figure',s))==(4 if slug=='gradient' else 0)
import hashlib
# Editorial regression guard; does not depend on Git checkout depth.
PRESERVED_RUSSIAN = {'freedom': '6f7a983800d47b555ffc77ab6161cf73071504e616af3ad35b9b908fd7c67745', 'fear': '884e890d5fb196fe54ced141af4b1c2493d4c259dff92593d7c87ea464bf2ed2', 'mistakes': '8e42590b43a3b3eaebacec66a0690c3120f78df46d65d40ca8496c18608a1ab8', 'start': '1b09bdc971e7e0779e5fdc03ac8cb011a42ee5dfeea9c6fd69f44b0d983cfe14', 'glossary': '039ad6e20dc53ebf02da6912d0d2dc1aad59c943ca041d01e83eacf2c34773ac'}
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
# Editorial consistency: corresponding Russian and English articles retain their structure.
EDITORIAL_SLUGS=('freedom','fear','mistakes','nihilism-without-verdict','weightlessness','after-ubermensch','start','glossary','bol-ne-vydumka','daoism-monophenomenalism','monophenomenalism-boundaries')
for slug in EDITORIAL_SLUGS:
 ru=(ROOT/'content'/(slug+'.md')).read_text()
 en=(ROOT/'content/en'/(slug+'.md')).read_text()
 assert len(re.findall(r'^## ',ru,re.M))==len(re.findall(r'^## ',en,re.M)),slug
 assert len(ru)>3000 and len(en)>3000,slug
# Full Russian and English Daoism research must remain structurally paired.
for lang,theses in (('ru',ru_theses),('en',expected)):
 dao=(ROOT/'content'/('en' if lang=='en' else '')/'daoism-monophenomenalism.md').read_text()
 assert len(dao)>60000,(lang,'Daoism study unexpectedly truncated')
 assert len(re.findall(r'^### \d+\. ',dao,re.M))==38,(lang,'Daoism study must retain 21+17 numbered sections')
 assert all(f'{i}. {t}' in dao for i,t in enumerate(theses,1)),(lang,'Daoism model theses altered')
 # Every source heading must be rendered as an HTML heading, not literal Markdown.
 page_html=(OUT/('en/' if lang=='en' else '')/'daoism-monophenomenalism'/'index.html').read_text()
 expected_headings=len(re.findall(r'^#{2,3} ',dao,re.M))
 rendered_headings=len(re.findall(r'<h[23] id="section-\d+">',page_html))
 assert expected_headings==rendered_headings,(lang,'Markdown headings leaked into article HTML',expected_headings,rendered_headings)
 assert not re.search(r'<p>\s*#{2,4}\s',page_html),(lang,'Raw Markdown heading in HTML')
# Philosophical boundaries article: complete paired editions, correct wording and no Markdown artifacts.
for lang,theses in (('ru',ru_theses),('en',expected)):
 article=(ROOT/'content'/('en' if lang=='en' else '')/'monophenomenalism-boundaries.md').read_text(encoding='utf-8')
 assert len(article)>30000,(lang,'boundaries article unexpectedly truncated')
 assert len(re.findall(r'^## \d{1,2}\. ',article,re.M))==16,(lang,'boundaries sections')
 assert all(f'{i}. {t}' in article for i,t in enumerate(theses,1)),(lang,'model theses altered')
 page=(OUT/('en/' if lang=='en' else '')/'monophenomenalism-boundaries'/'index.html').read_text()
 assert page.count('<h2 id=')==18,(lang,'boundaries headings missing')
 assert not re.search(r'<p>\s*#{2,4}\s',page),(lang,'raw Markdown headings in boundaries article')
 assert '<link rel="alternate" type="application/pdf" href="'+BASE+pdf_path(lang,'monophenomenalism-boundaries')+'">' in page
ru_boundaries=(ROOT/'content/monophenomenalism-boundaries.md').read_text()
assert 'После этого определения монофеноменализма' in ru_boundaries
assert 'Ни принадлежность к какой-либо конкретной недвойственной традиции' in ru_boundaries
assert 'такой цели не существует или её невозможно обоснованно установить' not in (ROOT/'content/nihilism-without-verdict.md').read_text()
assert 'no such purpose exists, or none can be adequately established' not in (ROOT/'content/en/nihilism-without-verdict.md').read_text()
assert 'Ни одно из этих действий не обязательно.' not in (ROOT/'content/fear.md').read_text()
assert 'None of these responses is required.' not in (ROOT/'content/en/fear.md').read_text()
assert len(ET.parse(OUT/'sitemap.xml').getroot())==2*(len(ALL_SLUGS)+3+len(WORK_PATHS))
print('OK: bilingual pairing, language metadata, sitemap URLs, four figures per language, original Russian texts and five English theses preserved')

# Explicitly attributed essay: bilingual section alignment and foundational theses.
for lang in ('ru','en'):
 p=ROOT/'content'/('en' if lang=='en' else '')/'ya-mir-drugie.md'
 t=p.read_text()
 assert len(re.findall(r'^## ',t,re.M))==14
 exact=ru_theses if lang=='ru' else expected
 assert all(f'{i}. {v}' in t for i,v in enumerate(exact,1))
 assert ('Роман Дудников' if lang=='ru' else 'Roman Dudnikov') in (OUT/('en/' if lang=='en' else '')/'ya-mir-drugie'/'index.html').read_text()
print('OK: authored bilingual essay and five theses verified')

# Every reading page has a real, readable PDF with all of its prose in order.
from pypdf import PdfReader
from original_works import WORKS, plain, Text
from pdf_export import pdf_path
def compact(value):
 return re.sub(r'\s+', '', value).replace('\u00ad', '')
editions=[(a['lang'],a['slug'],a['slug']+'/') for a in items]
editions += [(lang,'work-'+w['slug'],'works/'+w['slug']+'/') for lang in ('ru','en') for w in WORKS]
for lang,slug,page in editions:
 pdf=OUT/pdf_path(lang,slug)
 reader=PdfReader(pdf)
 assert len(reader.pages)>0 and pdf.stat().st_size>5000,pdf
 text='\n'.join(re.sub(r'prostostone\.github\.io/yavlenie\s*\d+', '', p.extract_text() or '') for p in reader.pages)
 assert '\ufffd' not in text,('Invalid character',pdf)
 if slug=='daoism-monophenomenalism':
  assert not re.search(r'(?m)^\s*#{2,4}\s',text),('Raw Markdown heading in PDF',lang)
 # Remove repeated running footers before comparing the full body, not just a sample.
 page_html=(OUT/('en/' if lang=='en' else '')/page/'index.html').read_text()
 prose=re.search(r'<div class="prose">(.*?)</div><section class="source-note">',page_html,re.S)[1]
 parser=Text();parser.feed(prose);remaining=compact(text)
 for chunk in parser.parts:
  needle=compact(chunk)
  if not needle:continue
  position=remaining.find(needle)
  if position<0:
   # PDF extraction may interleave list markers or neighbouring table cells.
   cursor=0
   for token in re.findall(r'\w+|[^\w\s]', chunk):
    token=compact(token)
    if not token:continue
    found=remaining.find(token,cursor)
    assert found>=0,('PDF text differs from HTML',pdf,token,needle[:90])
    cursor=found+len(token)
  # Table cells can be extracted in a different order across page breaks.
 pdf_url=BASE+pdf_path(lang,slug)
 assert page_html.count('class="pdf-download" href="'+pdf_url+'"')>=1,(page,lang)
 assert '<link rel="alternate" type="application/pdf" href="'+pdf_url+'">' in page_html
 assert any(p.get('/Annots') for p in reader.pages),('Missing PDF links',pdf)
# Both reading languages and original-work editions expose a static theme button
# immediately after their PDF download link; JavaScript binds it to the shared theme.
for lang in ('ru', 'en'):
 for page in ('start/', WORK_PATHS[0]):
  html_page=(OUT/('en/' if lang=='en' else '')/page/'index.html').read_text()
  assert re.search(r'class="reader-buttons".*?class="pdf-download"[^>]*>[^<]*</a><button type="button" id="reader-theme-toggle"',html_page,re.S),(lang,page,'reader theme control missing after PDF')
  assert "document.getElementById('reader-theme-toggle')" in html_page,(lang,page,'theme handler missing')
  assert re.search(r'id="reader-smaller".*?id="reader-font".*?id="reader-larger"',html_page,re.S),(lang,page,'font button must replace size reset between A− and A+')
  assert 'id="reader-reset"' not in html_page,(lang,page,'obsolete font-size reset button')
  assert "document.getElementById('reader-font')" in html_page,(lang,page,'font handler missing')
  assert 'root.dataset.readingFont' in html_page,(lang,page,'font state missing')
  assert "yavlenie-font" in html_page,(lang,page,'font choice persistence missing')
  # Compact visible labels must retain their position and accessible descriptions.
  button_row=re.search(r'<div class="reader-buttons">(.*?)</div><div class="reader-audio-panel"',html_page,re.S)
  assert button_row,(lang,page,'reader button group missing')
  button_html=button_row[1]
  assert re.search(r'id="reader-smaller"[^>]*>−</button>.*?id="reader-font"[^>]*>A</button>.*?id="reader-larger"[^>]*>\+</button>.*?id="reader-focus"[^>]*>.*?</button>.*?class="pdf-download"[^>]*>.*?</a><button[^>]*id="reader-theme-toggle"[^>]*>◐</button>',button_html,re.S),(lang,page,'compact reader control labels/order')
  assert 'aria-label="' in button_html,(lang,page,'reader controls lack accessible labels')
  assert re.search(r'class="pdf-download"[^>]*>PDF</a>',button_html),(lang,page,'compact PDF label missing')
  assert re.search(r'id="reader-theme-toggle"[^>]*>◐</button>.*?id="reader-listen-toggle"',button_html,re.S),(lang,page,'listen toggle must be beside theme')
  assert 'aria-expanded="false"' in button_html,(lang,page,'listen panel must start collapsed')
  assert 'id="reader-audio-play"' in html_page and 'id="reader-audio-pause"' in html_page and 'id="reader-audio-stop"' in html_page
  assert 'id="reader-audio-rate"' in html_page and 'id="reader-audio-voice"' in html_page and 'id="reader-audio-section"' in html_page
  assert 'reader-audio.js?v=audio-reader-20261112' in html_page
css=(ROOT/'assets/style.css').read_text()
# The current mobile design uses natural spacing and allows wrapping, without stretching.
mobile_css=css[css.index('/* Compact mobile reading controls:'):]
mobile_row=re.search(r'\.reader-toolbar \.reader-buttons\s*\{([^}]+)\}',mobile_css)[1]
assert all(rule in mobile_row for rule in ('flex-wrap:wrap','justify-content:flex-start','width:auto','gap:8px'))
assert 'flex:0 0 auto' in mobile_css
assert '#reader-listen-toggle' in mobile_css
assert 'reader-audio-panel' in css and 'reader-audio-settings' in css
assert (ROOT/'assets/reader-audio.js').exists()
print('OK: bilingual article and original-work theme and font controls available')

assert len(list(OUT.rglob('*.pdf')))==len(editions)
print(f'OK: {len(editions)} PDFs, full text preserved, bilingual download links and PDF metadata')

# Sentence-case safeguard for authored English titles and section headings.
# Keep proper nouns in their usual case; reject accidental pervasive Title Case.
for article in (ROOT/'content/en').glob('*.md'):
 lines=article.read_text(encoding='utf-8').splitlines()
 headings=[lines[0]]+[line[3:] for line in lines if line.startswith('## ')]
 for heading in headings:
  # Preserve the deliberately published title of the preceding comparative study.
  if article.stem=='buddhism-monophenomenalism' and heading=='Buddhism and Monophenomenalism: A Comparative Study':continue
  words=[w for w in re.findall(r"[^\W\d_]+(?:[’'-][^\W\d_]+)*",heading,re.UNICODE) if len(w)>1]
  capitals=sum(word[0].isupper() for word in words)
  assert not (len(words)>=4 and capitals>=4 and capitals/len(words)>=0.7),('English heading uses Title Case',article,heading)
  assert not (2<=len(words)<=3 and capitals==len(words)),('Short English heading uses Title Case',article,heading)
print('OK: English article headings use sentence case')

# Comparative study: full parallel structure and verbatim foundational theses.
buddhist_ru=(ROOT/'content/buddhism-monophenomenalism.md').read_text()
buddhist_en=(ROOT/'content/en/buddhism-monophenomenalism.md').read_text()
assert all(f'{i}. {t}' in buddhist_ru for i,t in enumerate(ru_theses,1))
assert all(f'{i}. {t}' in buddhist_en for i,t in enumerate(expected,1))
for level,count in ((2,2),(3,35),(4,17)):
 pattern=r'^'+'#'*level+' '
 assert len(re.findall(pattern,buddhist_ru,re.M))==len(re.findall(pattern,buddhist_en,re.M))==count
for lang in ('ru','en'):
 page=(OUT/('en' if lang=='en' else '')/'buddhism-monophenomenalism/index.html').read_text()
 assert page.count('<h3 id=')==35 and page.count('<h4 id=')==17
 assert not re.search(r'<p>#{2,4} ',page)
print('OK: complete bilingual Buddhist study, nested headings, and unchanged five theses')

# Article 16: parallel complete editions, source anchors, and unchanged theses.
assert ORDER.index('zen-monophenomenalism')==15
zen_ru=(ROOT/'content/zen-monophenomenalism.md').read_text()
zen_en=(ROOT/'content/en/zen-monophenomenalism.md').read_text()
assert all(f'{i}. {t}' in zen_ru for i,t in enumerate(ru_theses,1))
assert all(f'{i}. {t}' in zen_en for i,t in enumerate(expected,1))
assert len(zen_ru.split('\n\n'))==len(zen_en.split('\n\n'))
for level,count in ((2,3),(3,41)):
 assert len(re.findall(r'^'+'#'*level+' ',zen_ru,re.M))==len(re.findall(r'^'+'#'*level+' ',zen_en,re.M))==count
for lang in ('ru','en'):
 directory=OUT/('en' if lang=='en' else '')
 page=(directory/'zen-monophenomenalism/index.html').read_text()
 assert page.count('<h3 id=')==41
 assert '<p>##' not in page and '<p>---' not in page
 assert all(f'id="ref-{ref}"' in page for ref in ['A','B','C']+[str(i) for i in range(1,22)])
 home=(directory/'index.html').read_text()
 assert re.search(r'<a class="entry" href="[^"]*/zen-monophenomenalism/"><span class="num">16</span>',home)
print('OK: Zen study is article 16 in both languages; complete text, theses, and sources verified')

# Article 17: complete matching Russian and English editions.
new_slug='ya-ne-nuzhno-ustranyat'
assert ORDER.index(new_slug)==16
for lang in ('ru','en'):
 content_path=ROOT/'content'/('en' if lang=='en' else '')/(new_slug+'.md')
 source_text=content_path.read_text(encoding='utf-8')
 assert len(re.findall(r'^## ',source_text,re.M))==5,(lang,'article 17 headings')
 assert '2026-11-12' in source_text.splitlines()[3],(lang,'article 17 date')
 html_page=(OUT/('en/' if lang=='en' else '')/new_slug/'index.html').read_text()
 assert html_page.count('<h2 id=')==5,(lang,'article 17 sections')
 home_page=(OUT/('en/' if lang=='en' else '')/'index.html').read_text()
 assert re.search(r'<a class="entry" href="[^"]*/ya-ne-nuzhno-ustranyat/"><span class="num">17</span>',home_page),(lang,'article 17 index position')
 assert 'id="reader-theme-toggle"' in html_page and 'id="reader-font"' in html_page
 assert '<link rel="alternate" type="application/pdf" href="'+BASE+pdf_path(lang,new_slug)+'">' in html_page
print('OK: article 17 is bilingual, complete and published with PDF editions')

# The terminology article precedes the essay on unity in both languages.
assert ORDER.index("yavlenie-chto-znachit-eto-slovo")==7
assert ORDER[8]=="odno-ne-znachit-odinakovo"
for lang in ("ru","en"):
 page=(OUT/("en" if lang=="en" else "")/"yavlenie-chto-znachit-eto-slovo/index.html").read_text()
 assert page.count("<h2 id=")==6
 assert "<p>---</p>" not in page
 assert (OUT/pdf_path(lang,"yavlenie-chto-znachit-eto-slovo")).exists()
