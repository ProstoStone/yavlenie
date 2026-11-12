#!/usr/bin/env python3
"""Static bilingual publisher; optional reading theme; automatic bilingual PDF editions."""
from pathlib import Path
import json,re,html,shutil
from pdf_export import create_pdf, pdf_path
from datetime import date,datetime,timezone
from email.utils import format_datetime
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist'
BASE='https://prostostone.github.io/yavlenie/'
PREFIX='/yavlenie/'
SOURCE='https://prostostone.github.io/Monophenomenalism/index.html'
SOURCE_BASE=SOURCE.rsplit('/',1)[0]+'/'
E=html.escape
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir();shutil.copytree(ROOT/'assets',OUT/'assets')
def write(path,text):
 p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def local(lang,path=''):return ('en/' if lang=='en' else '')+path
def url(lang,path=''):return BASE+local(lang,path)
def href(lang,path=''):return PREFIX+local(lang,path)
def tr(lang,ru,en):return en if lang=='en' else ru
def name(lang):return tr(lang,'Явление','Phenomenon')
def inline(s):
 s=E(s)
 s=re.sub(r'\[([^\]]+)\]\((https://[^\s)]+|/[^\s)]+|#[^\s)]+)\)',r'<a href="\2">\1</a>',s)
 s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
 return re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<em>\1</em>',s)
def render(body,lang):
 result=[];toc=[]
 for block in body.strip().split('\n\n'):
  block=block.strip()
  if not block:continue
  if re.match(r'^#{2,4} ',block):
   marks,title=block.split(' ',1);level=len(marks);title=title.strip()
   ident=f'section-{len(toc)+1}' if level<=3 else f'subsection-{len(result)+1}'
   if level<=3:toc.append((ident,title))
   result.append(f'<h{level} id="{ident}">{inline(title)}</h{level}>')
  elif re.fullmatch(r'\{\{figure:[1-4]\}\}',block):
   n=block[9];result.append((ROOT/f'templates/gradient-{n}{".en" if lang=="en" else ""}.html').read_text())
  elif re.match(r'^\d+\. ',block):result.append('<ol>'+''.join('<li>'+inline(re.sub(r'^\d+\. ','',x))+'</li>' for x in block.splitlines())+'</ol>')
  elif re.match(r'^\[([A-C]|\d+)\] ',block):
   ref=re.match(r'^\[([A-C]|\d+)\] ',block)[1];result.append(f'<p id="ref-{ref}">'+inline(block)+'</p>')
  elif block.startswith('> '):result.append('<blockquote><p>'+inline(block[2:])+'</p></blockquote>')
  else:result.append('<p>'+inline(block.replace('\n',' '))+'</p>')
 return '\n'.join(result),toc
ORDER=['freedom','after-ubermensch','nihilism-without-verdict','weightlessness','mistakes','fear','bol-ne-vydumka','odno-ne-znachit-odinakovo','gradient','start','glossary','ya-mir-drugie','advaita-monophenomenalism','buddhism-monophenomenalism','zen-monophenomenalism','ya-ne-nuzhno-ustranyat','daoism-monophenomenalism','monophenomenalism-boundaries','about']
RELATED={'ya-mir-drugie':['advaita-monophenomenalism','start','glossary'],'freedom':['after-ubermensch','weightlessness','nihilism-without-verdict'],'after-ubermensch':['nihilism-without-verdict','weightlessness','freedom'],'nihilism-without-verdict':['weightlessness','after-ubermensch','freedom'],'weightlessness':['after-ubermensch','nihilism-without-verdict','freedom'],'mistakes':['bol-ne-vydumka','freedom','fear'],'fear':['freedom','bol-ne-vydumka','mistakes'],'bol-ne-vydumka':['odno-ne-znachit-odinakovo','gradient','glossary'],'odno-ne-znachit-odinakovo':['gradient','bol-ne-vydumka','start'],'gradient':['odno-ne-znachit-odinakovo','bol-ne-vydumka','glossary'],'start':['freedom','odno-ne-znachit-odinakovo','glossary'],'glossary':['gradient','bol-ne-vydumka','start'],'advaita-monophenomenalism':['buddhism-monophenomenalism','start','glossary'],'buddhism-monophenomenalism':['zen-monophenomenalism','advaita-monophenomenalism','glossary'],'zen-monophenomenalism':['daoism-monophenomenalism','buddhism-monophenomenalism','advaita-monophenomenalism'],'ya-ne-nuzhno-ustranyat':['freedom','ya-mir-drugie','start'],'daoism-monophenomenalism':['monophenomenalism-boundaries','zen-monophenomenalism','ya-ne-nuzhno-ustranyat'],'monophenomenalism-boundaries':['daoism-monophenomenalism','advaita-monophenomenalism','buddhism-monophenomenalism'],'about':['start','glossary','gradient']}
items=[]
for lang in ('ru','en'):
 for p in sorted((ROOT/'content'/('en' if lang=='en' else '')).glob('*.md')):
  title,desc,kind,published,body=p.read_text().split('\n',4);date.fromisoformat(published)
  slug=p.stem;assert re.fullmatch(r'[a-z0-9-]+',slug)
  items.append(dict(slug=slug,title=title,description=desc,kind=kind,date=published,body=body.strip(),lang=lang,url=url(lang,slug+'/'),text_url=url(lang,'text/'+slug+'.txt'),pdf_url=BASE+pdf_path(lang,slug),minutes=max(1,round(len(body.split())/180))))
  if slug=='ya-mir-drugie':items[-1]['author']=tr(lang,'Роман Дудников','Roman Dudnikov')
by={(a['lang'],a['slug']):a for a in items}
assert {a['slug'] for a in items if a['lang']=='ru'}=={a['slug'] for a in items if a['lang']=='en'}
def sources(lang):
 suffix='_en' if lang=='en' else ''
 return [(tr(lang,'Модель явления','Model of the Phenomenon'),SOURCE_BASE+f'model{suffix}-1.html'),(tr(lang,'Монофеноменализм','Monophenomenalism'),SOURCE_BASE+f'monophenomenalism{suffix}-1.html'),(tr(lang,'Рабочая карта','Working Map'),SOURCE_BASE+f'working_map{suffix}-1.html')]
def source_links(lang):return ' · '.join(f'<a href="{u}">{t}</a>' for t,u in sources(lang))
def layout(lang,title,desc,path,content,schema,text_path=None,noindex=False,pdf_url=None):
 theme_script=(ROOT/'assets/theme.js').read_text()
 n=name(lang);other='en' if lang=='ru' else 'ru';canonical=url(lang,path)
 alts='' if noindex else ''.join(f'<link rel="alternate" hreflang="{l}" href="{url(l,path)}">' for l in ('ru','en'))+f'<link rel="alternate" hreflang="x-default" href="{url("ru",path)}">'
 return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} — {n}</title><meta name="description" content="{E(desc,quote=True)}"><meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-snippet:-1,max-image-preview:large'}"><link rel="canonical" href="{canonical}">{alts}
<script id="reading-theme">{theme_script}</script>
<link rel="icon" type="image/svg+xml" sizes="any" href="{PREFIX}assets/favicon.svg?v=ya-logo-20261112">
<link rel="stylesheet" href="{PREFIX}assets/style.css?v=beige-progress-20261112"><link rel="stylesheet" href="{PREFIX}assets/illustrations.css">
<link rel="alternate" type="application/rss+xml" title="{n}" href="{url(lang,'feed.xml')}">
{f'<link rel="alternate" type="text/plain" href="{text_path}">' if text_path else ''}
{f'<link rel="alternate" type="application/pdf" href="{pdf_url}">' if pdf_url else ''}
<meta property="og:type" content="{'article' if text_path else 'website'}"><meta property="og:title" content="{E(title,quote=True)}"><meta property="og:description" content="{E(desc,quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:locale" content="{'en_US' if lang=='en' else 'ru_RU'}"><meta property="og:locale:alternate" content="{'ru_RU' if lang=='en' else 'en_US'}"><meta property="og:site_name" content="{n}">
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')}</script></head><body class="{'reading-page' if text_path else 'index-page'}">
<a class="skip" href="#main">{tr(lang,'К содержанию','Skip to content')}</a>
<header class="header"><a class="brand" href="{href(lang)}"><span class="mark" aria-hidden="true">я.</span>{n}</a><nav aria-label="{tr(lang,'Основная навигация','Main navigation')}"><a href="{href(lang,'start/')}">{tr(lang,'С чего начать','Start here')}</a><a href="{href(lang,'#articles')}">{tr(lang,'Все тексты','All articles')}</a><a href="{href(lang,'works/')}">{tr(lang,'Основные работы','Original works')}</a><a href="{href(lang,'about/')}">{tr(lang,'О проекте','About')}</a><span class="reading-controls"><a class="language" href="{url(other,path) if not noindex else url(other)}" lang="{other}" hreflang="{other}" aria-label="{tr(lang,'Read this page in English','Читать эту страницу по-русски')}">{tr(lang,'EN','RU')}</a><button id="theme-toggle" class="theme-toggle" type="button" aria-label="{tr(lang,'Тёмная тема','Dark theme')}" title="{tr(lang,'Тёмная тема','Dark theme')}" aria-pressed="false" hidden><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="#fff" stroke="currentColor" stroke-width="1.5"/><path d="M12 3a9 9 0 0 0 0 18Z" fill="#000"/></svg></button></span></nav></header>
<main id="main">{content}</main><footer><div><strong>{n}</strong><p>{tr(lang,'Монофеноменализм и Модель явления<br>в вопросах повседневной жизни.','Monophenomenalism and Model of the Phenomenon<br>through everyday questions.')}</p></div><nav aria-label="{tr(lang,'Ссылки внизу страницы','Footer links')}"><a href="{href(lang,'glossary/')}">{tr(lang,'Словарь','Glossary')}</a><a href="{href(lang,'catalog/')}">{tr(lang,'Текстовый каталог','Text catalogue')}</a><a href="{url(lang,'feed.xml')}">RSS</a><a href="{href(lang,'about/')}">{tr(lang,'О материалах','About the articles')}</a><a href="{SOURCE}">{tr(lang,'Монофеноменализм: первоисточники ↗','Monophenomenalism: original works ↗')}</a></nav></footer></body></html>'''
def download_button(lang,pdf,title=None):
 label=tr(lang,'Скачать','Download')
 aria=label+' PDF'+(': '+title if title else '')
 return f'<a class="pdf-download" href="{E(pdf,quote=True)}" download type="application/pdf" aria-label="{E(aria,quote=True)}">{label}</a>'
def card(a,i):
 return f'<div class="entry-wrap"><a class="entry" href="{a["url"]}"><span class="num">{i:02d}</span><div><div class="meta">{a["kind"]} · {a["minutes"]} {tr(a["lang"],"мин чтения","min read")}</div><h3>{E(a["title"])}</h3><p>{E(a["description"])}</p></div></a><div class="entry-actions">{download_button(a["lang"],a["pdf_url"],a["title"])}<a class="read-link" href="{a["url"]}" aria-label="{E(tr(a["lang"],"Читать: ","Read: ")+a["title"],quote=True)}">{tr(a["lang"],"Читать","Read")}</a></div></div>'
from original_works import publish_works, WORK_PATHS
def reading_toolbar(lang,pdf):
 return f'''<div class="reader-toolbar" role="region" aria-label="{tr(lang,'Настройки чтения','Reading settings')}"><span>{tr(lang,'Удобное чтение','Reading settings')}</span><div class="reader-buttons"><button type="button" id="reader-smaller" hidden aria-label="{tr(lang,'Уменьшить текст','Smaller text')}">−</button><button type="button" id="reader-font" hidden aria-pressed="false" aria-label="{tr(lang,'Переключить шрифт','Switch reading font')}" title="{tr(lang,'Переключить шрифт','Switch reading font')}">A</button><button type="button" id="reader-larger" hidden aria-label="{tr(lang,'Увеличить текст','Larger text')}">+</button><button type="button" id="reader-focus" hidden aria-pressed="false">{tr(lang,'Фокус','Focus')}</button>{download_button(lang,pdf)}<button type="button" id="reader-theme-toggle" aria-pressed="false" aria-label="{tr(lang,'Сменить тему','Switch theme')}" title="{tr(lang,'Сменить тему','Switch theme')}">◐</button></div></div><div class="reading-progress" aria-hidden="true" hidden><span></span></div>
'''
for lang in ('ru','en'):
 publish_works(globals(),lang)
 articles=sorted([a for a in items if a['lang']==lang],key=lambda a:ORDER.index(a['slug']) if a['slug'] in ORDER else len(ORDER))
 home=f'''<section class="hero"><p class="eyebrow">{tr(lang,'МОНОФЕНОМЕНАЛИЗМ И МОДЕЛЬ ЯВЛЕНИЯ','MONOPHENOMENALISM AND MODEL OF THE PHENOMENON')}</p><h1>{tr(lang,'Всё есть одно явление.<em>Различия не требуют второго мира.</em>','Everything is one phenomenon.<em>Differences don\'t require another world.</em>')}</h1><div class="hero-bottom"><p>{tr(lang,'Кто выбирает? Где возникает ошибка?<br>Что значит свобода, которую не нужно даже принимать?<br>Страх, ответственность, привычное «я» и повседневный опыт —<br>через монофеноменализм и «Модель явления».','Who makes a choice? What makes something a mistake?<br>What does it mean to be free without even having to accept freedom?<br>Fear, responsibility, the familiar “I,” and everyday experience —<br>explored through monophenomenalism and <em>Model of the Phenomenon</em>.')}</p><a class="button" href="{href(lang,'start/')}">{tr(lang,'Начать знакомство','Start exploring')} ↗</a></div><div class="orbit" aria-hidden="true"><span></span><span></span><span></span></div></section>
<section class="intro"><span class="eyebrow">{tr(lang,'ОДНА ТОЧКА ВХОДА','A PLACE TO BEGIN')}</span><p>{tr(lang,'Множество вещей. Множество различий.<br>Одно явление.',"Many things. Many distinctions.<br>One phenomenon.")}</p><a href="{SOURCE}">{tr(lang,'Перейти к исходным работам ↗','Explore the original works ↗')}</a></section>
<section id="articles" class="listing"><div class="section-head"><h2>{tr(lang,'Тексты для чтения','Read and explore')}</h2><span>{len(articles)-1:02d} {tr(lang,'материалов','texts')}</span></div>{''.join(card(a,i+1) for i,a in enumerate(articles) if a['slug']!='about')}</section>
<section class="closing"><span class="eyebrow">{tr(lang,'КОНТЕКСТ И ЗНАЧЕНИЯ','CONTEXT AND MEANING')}</span><h2>{tr(lang,'Слова знакомые.<br>Смысл стоит уточнить.','Familiar words.<br>Meanings worth exploring.')}</h2><p>{tr(lang,'Что здесь называется явлением, концепцией и опытом? Короткий словарь помогает читать дальше без подмены значений.','What do phenomenon, concept, and experience mean here? A short glossary helps you read on without losing the distinctions.')}</p><a href="{href(lang,'glossary/')}">{tr(lang,'Открыть словарь','Open the glossary')} →</a></section>'''
 write(local(lang,'index.html'),layout(lang,tr(lang,'Монофеноменализм в повседневной жизни','Monophenomenalism in everyday life'),tr(lang,'Статьи о свободе, страхе, ошибках и опыте. Монофеноменализм и Модель явления простыми словами.','Articles about freedom, fear, mistakes, and experience. Monophenomenalism and Model of the Phenomenon in plain language.'),'',home,{'@context':'https://schema.org','@type':'CollectionPage','name':name(lang),'url':url(lang),'inLanguage':lang,'hasPart':[{'@type':'WebPage','url':a['url'],'name':a['title']} for a in articles]}))
 for a in articles:
  slug=a['slug'];body,toc=render(a['body'],lang);related=[by[lang,s] for s in RELATED.get(slug,['start','glossary','freedom'])]
  byline=f'<span>·</span><span>{tr(lang,"Автор","Author")}: {E(a["author"])}</span>' if a.get('author') else ''
  content=f'''<div class="article-top"><a class="back" href="{href(lang,'#articles')}">← {tr(lang,'Все тексты','All articles')}</a><p class="eyebrow">{a['kind']} · {a['minutes']} {tr(lang,'МИН ЧТЕНИЯ','MIN READ')}</p><h1>{E(a['title'])}</h1><p class="deck">{E(a['description'])}</p><div class="meta"><time datetime="{a['date']}">{a['date']}</time><span>·</span><a href="{a['text_url']}">{tr(lang,'Текстовая версия','Plain text')}</a>{byline}</div></div>
{reading_toolbar(lang,a["pdf_url"])}
<div class="article-grid{' glossary-grid' if slug=='glossary' else ''}"><aside><nav aria-label="{tr(lang,'Содержание статьи','Contents')}"><span class="eyebrow">{tr(lang,'В ЭТОМ ТЕКСТЕ','IN THIS ARTICLE')}</span>{''.join(f'<a href="#{i}">{E(t)}</a>' for i,t in toc)}</nav></aside><article><div class="prose">{body}</div><section class="source-note"><h2>{tr(lang,'Исходные работы','Original works')}</h2><p>{source_links(lang)}</p></section></article></div><section class="related"><h2>{tr(lang,'Продолжить чтение','Keep reading')}</h2>{''.join(card(x,i+1) for i,x in enumerate(related))}</section>'''
  schema={'@context':'https://schema.org','@type':'Article','headline':a['title'],'description':a['description'],'datePublished':a['date'],'inLanguage':lang,'mainEntityOfPage':a['url'],'url':a['url'],'isPartOf':{'@type':'WebSite','name':name(lang),'url':url(lang)},'citation':[u for t,u in sources(lang)],'articleSection':a['kind'],'workTranslation':{'@type':'Article','url':url('en' if lang=='ru' else 'ru',slug+'/'),'inLanguage':'en' if lang=='ru' else 'ru'}}
  schema['encoding']={'@type':'MediaObject','encodingFormat':'application/pdf','contentUrl':a['pdf_url'],'inLanguage':lang}
  create_pdf(OUT,lang,slug,a['title'],a['description'],body+'<section class="source-note"><h2>'+tr(lang,'Исходные работы','Original works')+'</h2><p>'+source_links(lang)+'</p></section>',a['url'],a.get('author'))
  if a.get('author'):
   schema['author']={'@type':'Person','name':a['author'],'url':SOURCE}
   schema['copyrightHolder']={'@type':'Person','name':a['author'],'url':SOURCE}
  write(local(lang,slug+'/index.html'),layout(lang,a['title'],a['description'],slug+'/',content,schema,a['text_url'],pdf_url=a['pdf_url']))
  plain=a['body']
  for i in range(1,5):
   f=(ROOT/f'templates/gradient-{i}{".en" if lang=="en" else ""}.html').read_text();caption=re.search(r'<figcaption>(.*?)</figcaption>',f)[1]
   plain=plain.replace('{{figure:'+str(i)+'}}',tr(lang,'Иллюстрация','Illustration')+f' {i}: '+caption)
  write(local(lang,'text/'+slug+'.txt'),f'{a["title"]}\n{a["description"]}\n'+(f'{tr(lang,"Автор","Author")}: {a["author"]}\n' if a.get('author') else '')+f'\n{a["url"]}\n\n{plain}\n\n'+ '\n'.join(f'{t}: {u}' for t,u in sources(lang))+'\n'+url(lang,'about/')+'\n')
 cat=f'<section class="article-top"><p class="eyebrow">{tr(lang,"ОТКРЫТЫЙ КАТАЛОГ","OPEN CATALOGUE")}</p><h1>{tr(lang,"Все тексты.<br>Прямые ссылки.","Every text.<br>Direct links.")}</h1><p class="deck">{tr(lang,"HTML для чтения, PDF для скачивания, обычный текст для сохранения и JSON для программной обработки.","HTML for reading, PDF for download, plain text for saving, and JSON for programmatic access.")}</p></section><section class="catalog"><p><a href="{url(lang,"catalog.json")}">JSON</a> · <a href="{url(lang,"llms.txt")}">llms.txt</a> · <a href="{url(lang,"feed.xml")}">RSS</a></p>'
 for a in articles:cat+=f'<div class="catalog-row"><h2><a href="{a["url"]}">{E(a["title"])}</a></h2><p>{E(a["description"])}</p><a href="{a["text_url"]}">{tr(lang,"Обычный текст","Plain text")} ↗</a> {download_button(lang,a["pdf_url"],a["title"])}</div>'
 write(local(lang,'catalog/index.html'),layout(lang,tr(lang,'Каталог текстов','Text catalogue'),tr(lang,'Все материалы сайта: HTML, текстовые версии, JSON и RSS.','Every article: HTML, plain text, JSON, and RSS.'),'catalog/',cat+'</section>',{'@context':'https://schema.org','@type':'CollectionPage','name':name(lang),'url':url(lang,'catalog/'),'inLanguage':lang}))
 write(local(lang,'catalog.json'),json.dumps({'title':name(lang),'url':url(lang),'language':lang,'sources':sources(lang),'items':[{k:v for k,v in a.items() if k!='body'} for a in articles]},ensure_ascii=False,indent=2))
 write(local(lang,'llms.txt'),'# '+name(lang)+'\n\n'+tr(lang,'Авторские эссе и статьи, подготовленные при помощи ИИ; сведения о происхождении: ','Author essays and articles prepared with AI assistance; provenance: ')+url(lang,'about/')+'\n\n'+ '\n'.join(f'{t}: {u}' for t,u in sources(lang))+'\n\n'+''.join(f'- [{a["title"]}]({a["text_url"]}): {a["description"]}\n' for a in articles)+'\nJSON: '+url(lang,'catalog.json')+'\n'+url('en' if lang=='ru' else 'ru','llms.txt')+'\n')
 rss=ET.Element('rss',version='2.0');channel=ET.SubElement(rss,'channel')
 for k,v in [('title',name(lang)),('link',url(lang)),('description',tr(lang,'Новые статьи о монофеноменализме и Модели явления','Articles on monophenomenalism and Model of the Phenomenon')),('language',lang)]:ET.SubElement(channel,k).text=v
 for a in articles:
  if a['slug']=='about':continue
  el=ET.SubElement(channel,'item')
  for k,v in [('title',a['title']),('link',a['url']),('guid',a['url']),('description',a['description']),('pubDate',format_datetime(datetime.fromisoformat(a['date']).replace(tzinfo=timezone.utc)))]:ET.SubElement(el,k).text=v
 write(local(lang,'feed.xml'),ET.tostring(rss,encoding='unicode',xml_declaration=True))
 write(local(lang,'404.html'),layout(lang,tr(lang,'Страница не найдена','Page not found'),'404','404.html',f'<section class="article-top"><h1>{tr(lang,"Здесь пока пусто.","Nothing here yet.")}</h1><a href="{href(lang)}">{tr(lang,"К текстам","Back to reading")} →</a></section>',{},noindex=True))
ET.register_namespace('xhtml','http://www.w3.org/1999/xhtml')
sitemap=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
for path in ['', 'catalog/', 'works/']+[a['slug']+'/' for a in items if a['lang']=='ru']+WORK_PATHS:
 for lang in ('ru','en'):
  node=ET.SubElement(sitemap,'url');ET.SubElement(node,'loc').text=url(lang,path)
  for l in ('ru','en','x-default'):ET.SubElement(node,'{http://www.w3.org/1999/xhtml}link',rel='alternate',hreflang=l,href=url('ru' if l=='x-default' else l,path))
write('sitemap.xml',ET.tostring(sitemap,encoding='unicode',xml_declaration=True));write('.nojekyll','')
print(f'Built {len(items)} materials in two languages; {len(list(OUT.rglob("*.html")))} HTML pages')
