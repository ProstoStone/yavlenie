"""Build downloadable reading editions from the same HTML as the website."""
from html import escape
from pathlib import Path
from weasyprint import HTML, CSS

ROOT = Path(__file__).resolve().parent
CSS_TEXT = '''
@page {
 size: A4; margin: 22mm 23mm 23mm;
 @bottom-left { content: "prostostone.github.io/yavlenie"; font: 8pt "DejaVu Sans"; color: #777; }
 @bottom-right { content: counter(page); font: 9pt "DejaVu Sans"; color: #777; }
}
body { font: 11.5pt/1.65 "DejaVu Serif", serif; color: #242424; }
h1 { font-size: 25pt; line-height: 1.2; margin: 0 0 6mm; }
h2 { font-size: 17pt; line-height: 1.3; margin: 9mm 0 4mm; }
h3 { font-size: 13pt; line-height: 1.4; margin: 6mm 0 3mm; }
h4 { font-size: 11.5pt; }
h1,h2,h3,h4 { break-after: avoid; }
p,li { orphans: 3; widows: 3; }
p { margin: 0 0 4mm; }
a { color: #795c41; text-decoration: underline; overflow-wrap: anywhere; }
.edition { font: 9pt "DejaVu Sans"; color: #795c41; margin-bottom: 6mm; }
.description { color: #555; font-size: 12pt; }
.origin { font: 8.5pt/1.5 "DejaVu Sans"; margin-bottom: 10mm; }
blockquote { border-left: 2pt solid #b9a38c; margin: 5mm 0; padding-left: 5mm; }
li { margin-bottom: 2mm; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; }
td,th { padding: 2mm; border: .5pt solid #ccc; overflow-wrap: normal; min-width: 15mm; }
tr { break-inside: avoid; }
td:last-child,th:last-child { min-width: 25mm; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; }
.figure { break-inside: avoid; margin: 6mm 0; padding: 3mm; border: .5pt solid #ddd; }
.figure figcaption { font: 9pt/1.5 "DejaVu Sans"; color: #555; }
.field { height: 65mm; }
.cut-source,.cut-arrangement { height: 45mm; }
.context { min-height: 40mm; }
.picture-palette,.landscape { height: 40mm; }
.source-note { border-top: .5pt solid #ccc; margin-top: 10mm; padding-top: 4mm; font-size: 9pt; }
'''

def pdf_path(lang, slug):
    return ('en/' if lang == 'en' else '') + 'pdf/' + slug + '.pdf'

def create_pdf(out, lang, slug, title, description, body, page_url, author=None):
    target = out / pdf_path(lang, slug)
    target.parent.mkdir(parents=True, exist_ok=True)
    label = 'Явление · Версия для чтения' if lang == 'ru' else 'Phenomenon · Reading edition'
    byline = '<p>' + escape(author) + '</p>' if author else ''
    source = f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}">
{f'<meta name="author" content="{escape(author, quote=True)}">' if author else ''}
</head><body><header><p class="edition">{label}</p><h1>{escape(title)}</h1>
<p class="description">{escape(description)}</p>{byline}
<p class="origin"><a href="{page_url}">{page_url}</a></p></header>
<main>{body}</main></body></html>'''
    HTML(string=source, base_url=page_url).write_pdf(
        target, stylesheets=[CSS(filename=str(ROOT / 'assets/illustrations.css')), CSS(string=CSS_TEXT)])
    return target
