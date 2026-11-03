#!/usr/bin/env python3
"""Dependency-free static publisher. Content format documented in README.md."""
from pathlib import Path
import json, re, html, shutil
from datetime import date
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist'
BASE='https://prostostone.github.io/yavlenie-ryadom/'
PREFIX='/yavlenie-ryadom/'
SOURCE='https://prostostone.github.io/Monophenomenalism/index.html'
NAME='Явление рядом'
E=html.escape
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT/'assets', OUT/'assets')

def write(path,text):
 p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def inline(s): return re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',E(s))
def render(body):
 result=[];toc=[];n=0
 for block in body.strip().split('\n\n'):
  if block.startswith('## '):
   n+=1;title=block[3:].strip();toc.append((f'section-{n}',title));result.append(f'<h2 id="section-{n}">{inline(title)}</h2>')
  elif re.match(r'^\d+\. ',block):
   result.append('<ol>'+''.join('<li>'+inline(re.sub(r'^\d+\. ','',x))+'</li>' for x in block.splitlines())+'</ol>')
  else: result.append('<p>'+inline(block.replace('\n',' '))+'</p>')
 return '\n'.join(result),toc
items=[]
for path in sorted((ROOT/'content').glob('*.md')):
 title,desc,kind,published,body=path.read_text().split('\n',4)
 date.fromisoformat(published)
 slug=path.stem
 assert re.fullmatch(r'[a-z0-9-]+',slug)
 items.append(dict(slug=slug,title=title,description=desc,kind=kind,date=published,body=body.strip(),url=BASE+slug+'/',minutes=max(1,round(len(body.split())/180))))
by={x['slug']:x for x in items}
order=['freedom','mistakes','fear','start','glossary','about']
items.sort(key=lambda x:order.index(x['slug']) if x['slug'] in order else len(order))

def layout(title,desc,path,content,schema,alternate=None,noindex=False):
 canonical=BASE+path
 return f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} — {NAME}</title><meta name="description" content="{E(desc,quote=True)}">
<meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-snippet:-1,max-image-preview:large'}"><link rel="canonical" href="{canonical}">
<link rel="icon" href="{PREFIX}assets/icon.svg" type="image/svg+xml"><link rel="stylesheet" href="{PREFIX}assets/style.css">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="{BASE}feed.xml">
{f'<link rel="alternate" type="text/plain" href="{BASE}text/{alternate}.txt" title="Текстовая версия">' if alternate else ''}
<meta property="og:type" content="{'article' if alternate else 'website'}"><meta property="og:title" content="{E(title,quote=True)}"><meta property="og:description" content="{E(desc,quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="{NAME}">
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<','&lt;')}</script>
</head><body><a class="skip" href="#main">К содержанию</a>
<header class="header"><a class="brand" href="{PREFIX}" aria-label="Явление рядом — главная"><span class="mark" aria-hidden="true">я.</span>{NAME}</a><nav aria-label="Основная навигация"><a href="{PREFIX}start/">С чего начать</a><a href="{PREFIX}#articles">Все тексты</a><a href="{PREFIX}about/">О проекте</a></nav></header>
<main id="main">{content}</main>
<footer><div><strong>{NAME}</strong><p>Монофеноменализм и Модель явления<br>в вопросах повседневной жизни.</p></div><nav aria-label="Ссылки внизу страницы"><a href="{SOURCE}">Исходные работы ↗</a><a href="{PREFIX}glossary/">Словарь</a><a href="{PREFIX}catalog/">Текстовый каталог</a><a href="{PREFIX}feed.xml">RSS</a><a href="{PREFIX}about/">О материалах</a></nav><p class="footnote">Популярные интерпретации и пояснения. Без персональной авторской подписи.</p></footer>
</body></html>'''

def card(a,i):
 return f'''<a class="entry" href="{PREFIX}{a['slug']}/"><span class="num">{i:02d}</span><div><div class="meta">{a['kind']} <span>·</span> {a['minutes']} мин чтения</div><h3>{E(a['title'])}<span aria-hidden="true">↗</span></h3><p>{E(a['description'])}</p></div></a>'''
entries=''.join(card(a,i+1) for i,a in enumerate(items) if a['slug']!='about')
home=f'''<section class="hero"><p class="eyebrow">ЗАМЕТКИ О ТОМ, ЧТО УЖЕ ЕСТЬ</p><h1>Жизнь ближе,<br>чем её <em>объяснения.</em></h1><div class="hero-bottom"><p>Свобода, страх, ошибки и привычное «я».<br>Монофеноменализм и Модель явления —<br>понятным языком, рядом с обычной жизнью.</p><a class="button" href="{PREFIX}start/">Начать знакомство <span aria-hidden="true">↗</span></a></div><div class="orbit" aria-hidden="true"><span></span><span></span><span></span></div></section>
<section class="intro"><span class="eyebrow">ОДНА ТОЧКА ВХОДА</span><p>Не обязательно сначала разобраться во всём,<br>чтобы заметить то, что происходит сейчас.</p><a href="{SOURCE}">Перейти к исходным работам ↗</a></section>
<section id="articles" class="listing"><div class="section-head"><h2>Тексты для чтения</h2><span>{len(items)-1:02d} материалов</span></div>{entries}</section>
<section class="closing"><span class="eyebrow">КОНТЕКСТ И ЗНАЧЕНИЯ</span><h2>Слова знакомые.<br>Смысл стоит уточнить.</h2><p>Что здесь называется явлением, концепцией и опытом? Короткий словарь помогает читать дальше без подмены значений.</p><a href="{PREFIX}glossary/">Открыть словарь →</a></section>'''
write('index.html',layout('Монофеноменализм в повседневной жизни','Статьи о свободе, страхе, ошибках и опыте. Монофеноменализм и Модель явления простыми словами, со ссылками на первоисточники.','',home,{'@context':'https://schema.org','@type':'CollectionPage','name':NAME,'url':BASE,'inLanguage':'ru','hasPart':[{'@type':'WebPage','url':a['url'],'name':a['title']} for a in items]}))
for a in items:
 body,toc=render(a['body']); slug=a['slug']
 related=[x for x in items if x['slug']!=slug and x['slug']!='about'][:3]
 toc_html=''.join(f'<a href="#{id}">{E(t)}</a>' for id,t in toc)
 note='Свободное философское прочтение. Не доказательство исходной позиции и не обещание определённого жизненного результата.' if a['kind']=='Эссе' else 'Пояснение для знакомства с темой. Точные формулировки и аргументы — в исходных работах.'
 content=f'''<div class="article-top"><a class="back" href="{PREFIX}#articles">← Все тексты</a><p class="eyebrow">{a['kind']} · {a['minutes']} МИН ЧТЕНИЯ</p><h1>{E(a['title'])}</h1><p class="deck">{E(a['description'])}</p><div class="meta"><time datetime="{a['date']}">{date.fromisoformat(a['date']).day} {['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'][date.fromisoformat(a['date']).month-1]} {date.fromisoformat(a['date']).year}</time><span>·</span><a href="{PREFIX}text/{slug}.txt">Текстовая версия</a></div></div>
<div class="article-grid"><aside><nav aria-label="Содержание статьи"><span class="eyebrow">В ЭТОМ ТЕКСТЕ</span>{toc_html}</nav></aside><article><div class="prose">{body}</div><section class="source-note"><h2>Связь с исходными работами</h2><p>{note}</p><a href="{SOURCE}">«Монофеноменализм» и «Модель явления» ↗</a><p><a href="{PREFIX}about/">О происхождении и статусе материалов</a></p></section></article></div>
<section class="related"><h2>Продолжить чтение</h2>{''.join(card(x,i+1) for i,x in enumerate(related))}</section>'''
 schema={'@context':'https://schema.org','@type':'Article','headline':a['title'],'description':a['description'],'datePublished':a['date'],'dateModified':a['date'],'inLanguage':'ru','mainEntityOfPage':a['url'],'url':a['url'],'isPartOf':{'@type':'WebSite','name':NAME,'url':BASE},'citation':SOURCE,'articleSection':a['kind']}
 write(slug+'/index.html',layout(a['title'],a['description'],slug+'/',content,schema,slug))
 text=f"{a['title']}\n{a['description']}\n\nТип: {a['kind']}\nДата: {a['date']}\nСтраница: {a['url']}\nСтатус: {note}\n\n{a['body']}\n\nИсходные работы: {SOURCE}\nО материалах: {BASE}about/\n"
 write('text/'+slug+'.txt',text)
 # Separate downloadable source; same text, no hidden additional claims.
 a['text_url']=BASE+'text/'+slug+'.txt'
write('catalog.json',json.dumps({'title':NAME,'url':BASE,'language':'ru','source':SOURCE,'status':'Популярные интерпретации и пояснения, не первоисточник','items':[{k:v for k,v in a.items() if k not in ['body']} for a in items]},ensure_ascii=False,indent=2))
cat='<section class="article-top"><p class="eyebrow">ОТКРЫТЫЙ КАТАЛОГ</p><h1>Все тексты.<br>Прямые ссылки.</h1><p class="deck">HTML для чтения, обычный текст для сохранения и JSON для программной обработки. Содержание одинаково доступно людям и программам.</p></section><section class="catalog"><p><a href="'+PREFIX+'catalog.json">Каталог JSON</a> · <a href="'+PREFIX+'llms.txt">Краткий указатель llms.txt</a> · <a href="'+PREFIX+'feed.xml">RSS</a></p>'
for a in items: cat+=f'<div class="catalog-row"><h2><a href="{a["url"]}">{E(a["title"])}</a></h2><p>{E(a["description"])}</p><a href="{a["text_url"]}">Обычный текст ↗</a></div>'
cat+='</section>'
write('catalog/index.html',layout('Каталог текстов','Все материалы сайта: HTML, текстовые версии, JSON и RSS.','catalog/',cat,{'@context':'https://schema.org','@type':'CollectionPage','name':'Каталог текстов','url':BASE+'catalog/'}))
write('llms.txt','# Явление рядом\n\n> Статьи и пояснения о монофеноменализме и Модели явления. Популярные интерпретации, не авторские первоисточники и не независимые доказательства.\n\nИсходные работы: '+SOURCE+'\n\n## Материалы\n'+''.join(f'- [{a["title"]}]({a["text_url"]}): {a["description"]}\n' for a in items)+'\nКаталог JSON: '+BASE+'catalog.json\n')
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9')
root=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
for url in [BASE,BASE+'catalog/']+[a['url'] for a in items]:
 el=ET.SubElement(root,'url');ET.SubElement(el,'loc').text=url
write('sitemap.xml',ET.tostring(root,encoding='unicode',xml_declaration=True))
rss=ET.Element('rss',version='2.0');channel=ET.SubElement(rss,'channel')
for k,v in [('title',NAME),('link',BASE),('description','Новые статьи о монофеноменализме и Модели явления'),('language','ru')]:ET.SubElement(channel,k).text=v
for a in items:
 if a['slug']=='about':continue
 el=ET.SubElement(channel,'item')
 for k,v in [('title',a['title']),('link',a['url']),('guid',a['url']),('description',a['description'])]:ET.SubElement(el,k).text=v
write('feed.xml',ET.tostring(rss,encoding='unicode',xml_declaration=True))
write('.nojekyll','')
write('404.html',layout('Страница не найдена','Такой страницы здесь нет.','404.html','<section class="article-top"><p class="eyebrow">404</p><h1>Здесь пока пусто.</h1><p class="deck">Возможно, адрес изменился.</p><a class="button" href="'+PREFIX+'">К текстам →</a></section>',{},noindex=True))
print(f'Built {len(items)} articles and {len(list(OUT.rglob("*.html")))} HTML pages')
