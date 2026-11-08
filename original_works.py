"""Continuous, verbatim reading editions of the three original works."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,quote
import json,re,html
ROOT=Path(__file__).resolve().parent
WORKS=json.loads((ROOT/'originals/works.json').read_text())
WORK_PATHS=['works/'+w['slug']+'/' for w in WORKS]
ORIGINAL='https://prostostone.github.io/Monophenomenalism/'
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
def plain(s):
 p=Text();p.feed(s);return ' '.join(' '.join(p.parts).split())
def fragment(name):
 s=(ROOT/'originals'/name).read_text()
 a=re.search(r'<article[^>]*>(.*?)</article>',s,re.S)
 if a:return a[1].strip()
 b=re.search(r'<body[^>]*>(.*?)</body>',s,re.S)[1]
 return re.split(r'<(?:div|nav) class="pagination"',b[b.index('<h1'):])[0].strip()
def complete(w,lang):
 pieces=[];toc=[];expected=[]
 for n in (1,2,3):
  filename=w['stem']+('_en' if lang=='en' else '')+f'-{n}.html'
  f=fragment(filename);expected.append(plain(f))
  # Keep all original words, but leave the page-level H1 to the reader header.
  f=re.sub(r'<(/?)h1\b',r'<\1h2',f)
  f=re.sub(r'\bid=([\"\'])(.*?)\1',lambda m:'id="p'+str(n)+'-'+m[2]+'"',f)
  def link(m):
   value=html.unescape(m[2])
   target='#p'+str(n)+'-'+value[1:] if value.startswith('#') else urljoin(ORIGINAL+filename,value)
   return 'href="'+html.escape(target,quote=True)+'"'
  f=re.sub(r'href=([\"\'])(.*?)\1',link,f)
  def heading(m):
   level,attrs,label=m.groups();found=re.search(r'\bid="([^"]+)"',attrs)
   ident=found[1] if found else f'work-heading-{len(toc)+1}'
   if not found:attrs+=' id="'+ident+'"'
   toc.append((ident,plain(label),level))
   return '<h'+level+attrs+'>'+label+'</h'+level+'>'
  f=re.sub(r'<h([2-4])([^>]*)>(.*?)</h\1>',heading,f,flags=re.S)
  pieces.append(f)
 body='\n'.join(pieces)
 assert plain(body)==' '.join(expected),('Original text changed',w['slug'],lang)
 return body,toc

def publish_works(g,lang):
 tr,E,url,href,local,write,layout,card=[g[k] for k in ('tr','E','url','href','local','write','layout','card')]
 author=tr(lang,'Роман Дудников','Roman Dudnikov');cards=[]
 for i,w in enumerate(WORKS):
  body,toc=complete(w,lang);path=WORK_PATHS[i];title=w['title'][lang];desc=w['desc'][lang]
  minutes=max(1,round(len(plain(body).split())/180));txt='text/work-'+w['slug']+'.txt'
  original=ORIGINAL+w['stem']+('_en' if lang=='en' else '')+'-1.html'
  original_pdf=ORIGINAL+quote(w['pdf'][lang])
  pdf=g['BASE']+g['pdf_path'](lang,'work-'+w['slug'])
  g['create_pdf'](g['OUT'],lang,'work-'+w['slug'],title,desc,body,url(lang,path),author)
  a={'title':title,'description':desc,'url':url(lang,path),'lang':lang,'kind':tr(lang,'Основная работа','Original work'),'minutes':minutes,'pdf_url':pdf}
  cards.append(card(a,i+1))
  content=f'''<div class="article-top"><a class="back" href="{href(lang,'works/')}">← {tr(lang,'Основные работы','Original works')}</a><p class="eyebrow">{tr(lang,'ПОЛНЫЙ ТЕКСТ','COMPLETE TEXT')} · {minutes} {tr(lang,'МИН ЧТЕНИЯ','MIN READ')}</p><h1>{E(title)}</h1><p class="deck">{E(desc)}</p><div class="meta"><span>{author}</span><a href="{url(lang,txt)}">TXT ↓</a>{g["download_button"](lang,pdf)}</div></div>{g['reading_toolbar'](lang)}<div class="article-grid original-work"><aside><nav aria-label="{tr(lang,'Содержание работы','Contents')}"><span class="eyebrow">{tr(lang,'СОДЕРЖАНИЕ','CONTENTS')}</span>{''.join(f'<a href="#{ident}">{E(label)}</a>' for ident,label,level in toc if level!='4')}</nav></aside><article><div class="prose">{body}</div><div class="article-download">{g["download_button"](lang,pdf)}</div><section class="source-note"><h2>{tr(lang,'Первоисточник','Original publication')}</h2><p>{tr(lang,'Текст Романа Дудникова перенесён дословно.','Roman Dudnikov’s text is reproduced verbatim.')} <a href="{original}">{tr(lang,'Открыть первоисточник','View original publication')} ↗</a> · <a href="{original_pdf}">{tr(lang,'Исходный PDF','Original PDF')} ↗</a></p><p><a href="{href(lang,'works/')}">← {tr(lang,'Все основные работы','All original works')}</a></p></section></article></div>'''
  schema={'@context':'https://schema.org','@type':'ScholarlyArticle','headline':title,'author':{'@type':'Person','name':author},'inLanguage':lang,'url':url(lang,path),'isBasedOn':original,'workTranslation':{'@type':'ScholarlyArticle','url':url('en' if lang=='ru' else 'ru',path)}}
  schema['encoding']={'@type':'MediaObject','encodingFormat':'application/pdf','contentUrl':pdf,'inLanguage':lang}
  write(local(lang,path+'index.html'),layout(lang,title,desc,path,content,schema,url(lang,txt),pdf_url=pdf))
  write(local(lang,txt),plain(body)+'\n')
 title=tr(lang,'Основные работы','Original works')
 desc=tr(lang,'Три работы Романа Дудникова. Полные тексты для последовательного чтения.','Three works by Roman Dudnikov. Complete texts for uninterrupted reading.')
 secondary='https://model-of-the-phenomenon.starryadage.chatgpt.site/'+('ru/' if lang=='ru' else '')
 listing=f'''<section class="article-top"><p class="eyebrow">{tr(lang,'РОМАН ДУДНИКОВ','ROMAN DUDNIKOV')}</p><h1>{title}</h1><p class="deck">{desc}</p></section><section class="listing works-list"><div class="section-head"><h2>{tr(lang,'Тексты для чтения','Read and explore')}</h2><span>03 {tr(lang,'работы','works')}</span></div>{''.join(cards)}</section><section class="catalog"><div class="source-note"><h2>{tr(lang,'Другие версии для чтения','Other reading editions')}</h2><p><a href="{g['SOURCE']}">{tr(lang,'Официальный сайт основных работ','Original website of the works')} ↗</a> · <a href="{original_pdf}">{tr(lang,'Исходный PDF','Original PDF')} ↗</a></p><p><a href="{secondary}">Model of the Phenomenon ↗</a> — {tr(lang,'дополнительный сайт с основными работами.','an additional website for the original works.')}</p></div></section>'''
 write(local(lang,'works/index.html'),layout(lang,title,desc,'works/',listing,{'@context':'https://schema.org','@type':'CollectionPage','name':title,'url':url(lang,'works/'),'inLanguage':lang}))
