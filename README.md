# Явление

Тематический сайт о монофеноменализме и Модели явления. Материалы без персональной авторской подписи; популярные интерпретации отделены от исходных работ.

Сайт: https://prostostone.github.io/yavlenie/

Первоисточники: https://prostostone.github.io/Monophenomenalism/index.html

## Добавить статью

Создайте `content/unique-slug.md` (латинские буквы, цифры и дефисы). Первые четыре строки: заголовок, краткое описание, тип материала, дата ISO YYYY-MM-DD. Затем пустая строка и текст. Поддерживаются абзацы, заголовки `##`, выделение `**жирным**` и нумерованный список. Произвольный HTML экранируется. Это ограниченный формат, не полный Markdown.

Пример:

```text
Название статьи
Краткое самостоятельное описание содержания.
Эссе
2026-11-03

Первый абзац.

## Вопрос

Объяснение и конкретный пример.
```

Коммит в main запускает сборку и публикацию через GitHub Actions. Не переименовывайте опубликованные slug без перенаправлений. Не публикуйте пустые будущие страницы.

## Локальная проверка

Python 3.10+; внешних зависимостей нет.

```sh
python3 build.py
python3 check.py
```

Результат — `dist/`. Постоянный адрес задан BASE и PREFIX в build.py; меняйте их вместе при переносе.

## Редакционный план

Следующие отдельные темы: ответственность без окончательного владельца; боль и сообщение о боли; почему концепция не значит выдумка; смысл без обязательного предназначения; научная проверка внутри опыта; чем самоприменимость отличается от доказательства. Это план, не опубликованные материалы.

К каждому тексту: отдельный вопрос, конкретный пример, границы вывода, ссылки на первоисточники. Не выдавать интерпретации за цитаты. Не создавать повторяющиеся страницы ради числа URL. Не приписывать автору исходных работ тексты сайта.

## Индексация и машинное чтение

Полный HTML не требует JavaScript. Есть canonical, description, Open Graph, JSON-LD, sitemap.xml, RSS, catalog.json, llms.txt и текстовые версии. llms.txt — вспомогательный указатель, а не гарантия использования ИИ. Видимый и текстовый контент совпадают по смыслу; скрытого рекламного текста нет.

GitHub Pages project site расположен в подкаталоге: robots.txt применяется только в корне домена https://prostostone.github.io/robots.txt. Этот проект не меняет его и не выдаёт файл внутри подкаталога за действующий robots.txt. Для включения в поиск после публикации можно отправить URL sitemap.xml в Google Search Console и Яндекс Вебмастер при наличии подтверждённого доступа к сайту. Индексация и цитирование не гарантированы.

Статьи публикуются с помощью автоматической сборки; личные данные, токены и вложенные исходные DOCX в репозиторий не включаются.

## Bilingual edition

Russian URLs remain unchanged. English pages are under `/en/`. Each source in
`content/<slug>.md` must have a complete counterpart in `content/en/<slug>.md`.
The filename is the language-independent article ID: the same slug pairs translations.
The first four lines remain title, description, category, and ISO publication date.
The body supports paragraphs, `##` headings, emphasis, numbered lists, Markdown links,
and blockquotes. The illustration article uses `{{figure:1}}` through `{{figure:4}}`;
reviewed accessible HTML lives in `templates/`, with `.en.html` translations.
Do not include arbitrary scripts or raw HTML in content Markdown.

Add new slugs to `ORDER` and choose genuinely relevant articles in `RELATED` in
`build.py`. Add both languages in one commit. The build verifies matching language
sets; `check.py` checks reciprocal alternates, canonical URLs, links, metadata,
feeds, figures, and preservation of the original five theses.

Both languages have their own home, glossary, About, catalogue, RSS, JSON catalogue,
plain-text articles and llms.txt. The root sitemap lists both languages and their
hreflang counterparts. There are no automatic language redirects or required scripts.
The About pages hold the editorial and AI provenance explanation. Article source
footers link directly to all three original works in the current language; the
original author is never entered as the author of derivative articles in JSON-LD.

The original philosophical repository and PDFs are not modified or mirrored.
English terminology follows the supplied translations: experiencing (переживание),
experience (опыт), sensory experiencing (чувственное переживание), distinction
(различение), concept (концепция). The source texts, not these popular explanations,
remain the authority for quotations.
