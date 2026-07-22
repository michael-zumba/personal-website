"""Extract structured content from HTML research reports into JSON for docx generation.

Author: Dr Yuqian Zhang
Date: 16 July 2026

Reads the report manifest (written by sync_reports.py) to discover which HTML files to process.
"""

import json
import os
import re
import sys
from bs4 import BeautifulSoup, NavigableString, Tag


def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('\u2014', ' -- ').replace('\u2013', ' - ')
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('&amp;', '&')
    return text


def extract_standard_report(soup):
    result = {'title': '', 'subtitle': '', 'author': '', 'date': '', 'abstract': '', 'sections': [], 'references': []}

    header = soup.find('header')
    if header:
        h1 = header.find('h1')
        if h1:
            result['title'] = clean_text(h1.get_text())
        subtitle_el = header.find(class_='subtitle')
        if subtitle_el:
            result['subtitle'] = clean_text(subtitle_el.get_text())
        meta_el = header.find(class_='meta')
        if meta_el:
            meta_text = clean_text(meta_el.get_text())
            parts = [p.strip() for p in meta_text.split('|')]
            if len(parts) >= 1:
                result['author'] = parts[0]
            if len(parts) >= 2:
                result['date'] = parts[1]

    exec_summary = soup.find('section', class_='exec-summary')
    if exec_summary:
        p_texts = [clean_text(p.get_text()) for p in exec_summary.find_all('p', recursive=True) if clean_text(p.get_text())]
        if p_texts:
            result['abstract'] = ' '.join(p_texts)

    container = soup.find('div', class_='container')
    if not container:
        container = soup.body or soup

    for child in container.find_all(recursive=False):
        if not isinstance(child, Tag):
            continue
        classes = child.get('class', [])

        if 'exec-summary' in classes or 'toc' in classes:
            continue

        if 'ref-section' in classes:
            refs = extract_standard_refs(child)
            if not refs:
                refs = extract_ref_list_items(child)
            result['references'].extend(refs)
            continue

        if child.name == 'section':
            process_section(child, result)

    if not result['title']:
        title_tag = soup.find('title')
        if title_tag:
            result['title'] = clean_text(title_tag.get_text())
    if not result['author']:
        for meta in soup.find_all('meta'):
            if meta.get('name', '').lower() == 'author':
                result['author'] = meta.get('content', '')
                break

    result['references'] = deduplicate_refs(result['references'])
    return result


def extract_nlp_report(soup):
    result = {'title': '', 'subtitle': '', 'author': '', 'date': '', 'abstract': '', 'sections': [], 'references': []}

    report_head = soup.find('header', class_='report-head')
    if report_head:
        h1 = report_head.find('h1')
        if h1:
            result['title'] = clean_text(h1.get_text())
        subtitle = report_head.find('p', class_='subtitle')
        if subtitle:
            result['subtitle'] = clean_text(subtitle.get_text())
        byline = report_head.find('p', class_='byline')
        if byline:
            spans = byline.find_all('span')
            parts = [clean_text(s.get_text()) for s in spans if clean_text(s.get_text()) and '|' not in clean_text(s.get_text())]
            if len(parts) >= 1:
                result['author'] = parts[0]
            if len(parts) >= 2:
                result['date'] = parts[1]

        abstract = report_head.find('div', class_='abstract')
        if abstract:
            p_texts = [clean_text(p.get_text()) for p in abstract.find_all('p') if clean_text(p.get_text())]
            if p_texts:
                result['abstract'] = ' '.join(p_texts)

    main = soup.find('main')
    if main:
        for child in main.find_all(recursive=False):
            if not isinstance(child, Tag):
                continue
            if child.name == 'section':
                process_nlp_section(child, result)

    refs_footer = soup.find('footer', class_='report-foot')
    if refs_footer:
        sources = refs_footer.find('div', class_='sources')
        if sources:
            ol = sources.find('ol')
            if ol:
                for li in ol.find_all('li', recursive=False):
                    txt = clean_text(li.get_text())
                    a = li.find('a')
                    url = a.get('href', '') if a else ''
                    if txt:
                        result['references'].append({'text': txt, 'url': url})

    result['references'] = deduplicate_refs(result['references'])
    return result


def process_section(section_el, result):
    h2 = section_el.find('h2')
    section_title = clean_text(h2.get_text()) if h2 else ''
    section_id = section_el.get('id', '')

    if section_id == 'references' or section_title.lower() == 'references':
        for ref_div in section_el.find_all('div', class_='ref-section'):
            result['references'].extend(extract_ref_list_items(ref_div))
        return

    content = extract_section_body(section_el)

    if section_title or content:
        result['sections'].append({'heading': section_title, 'level': 1, 'content': content})

    for h3 in section_el.find_all('h3'):
        sub = extract_h3_subsection(section_el, h3)
        if sub:
            result['sections'].append(sub)


def process_nlp_section(section_el, result):
    h2 = section_el.find('h2')
    heading = clean_text(h2.get_text()) if h2 else ''

    content = []
    for child in section_el.children:
        if not isinstance(child, Tag):
            continue
        if child.name in ('span',) and 'section-kicker' in (child.get('class', [])):
            continue
        if child.name == 'h2':
            continue
        content.extend(parse_inline_element(child))

    if heading or content:
        result['sections'].append({'heading': heading, 'level': 1, 'content': content})


def extract_section_body(element):
    content = []
    for child in element.children:
        if not isinstance(child, Tag):
            continue
        if child.name in ('h2', 'h3'):
            continue
        content.extend(parse_inline_element(child))
    return content


def extract_h3_subsection(parent, h3):
    heading = clean_text(h3.get_text())
    content = []
    for sibling in h3.find_next_siblings():
        if not isinstance(sibling, Tag):
            continue
        if sibling.name in ('h2', 'h3'):
            break
        content.extend(parse_inline_element(sibling))
    if not heading and not content:
        return None
    return {'heading': heading, 'level': 2, 'content': content}


def parse_inline_element(child):
    items = []
    classes = child.get('class', [])

    if child.name == 'p':
        txt = clean_text(child.get_text())
        if txt:
            items.append({'type': 'paragraph', 'text': txt})

    elif child.name in ('ul',) and 'key-findings' not in classes:
        li_items = [clean_text(li.get_text()) for li in child.find_all('li', recursive=False) if clean_text(li.get_text())]
        if li_items:
            items.append({'type': 'bullet_list', 'items': li_items})

    elif child.name == 'ol':
        li_items = [clean_text(li.get_text()) for li in child.find_all('li', recursive=False) if clean_text(li.get_text())]
        if li_items:
            items.append({'type': 'numbered_list', 'items': li_items})

    elif child.name in ('table',) or 'chart-container' in classes or 'table-wrap' in classes:
        tbl = child if child.name == 'table' else child.find('table')
        if tbl:
            td = extract_table_data(tbl)
            caption = ''
            h4 = child.find('h4')
            if h4:
                caption = clean_text(h4.get_text())
            cap_tag = child.find('caption')
            if cap_tag:
                caption = clean_text(cap_tag.get_text())
            note_el = child.find(class_='chart-note')
            note = clean_text(note_el.get_text()) if note_el else ''
            if td:
                items.append({'type': 'table', 'caption': caption, 'note': note, 'headers': td['headers'], 'rows': td['rows']})

    elif child.name == 'div' and 'callout' in classes:
        txt = clean_text(child.get_text())
        if txt:
            items.append({'type': 'callout', 'text': txt})

    elif child.name == 'div' and 'two-col' in classes:
        for sub_div in child.find_all(class_='chart-container'):
            tbl = sub_div.find('table')
            if tbl:
                td = extract_table_data(tbl)
                caption = clean_text(sub_div.find('h4').get_text()) if sub_div.find('h4') else ''
                if td:
                    items.append({'type': 'table', 'caption': caption, 'note': '', 'headers': td['headers'], 'rows': td['rows']})

    elif child.name == 'div' and 'metric-row' in classes:
        metrics = []
        for metric_el in child.find_all(class_='metric'):
            num = clean_text(metric_el.find(class_='metric-num').get_text()) if metric_el.find(class_='metric-num') else ''
            label = clean_text(metric_el.find(class_='metric-label').get_text()) if metric_el.find(class_='metric-label') else ''
            if num or label:
                metrics.append(f"{num} -- {label}")
        if metrics:
            items.append({'type': 'bullet_list', 'items': metrics})

    elif child.name == 'figure':
        caption_el = child.find('figcaption')
        if caption_el:
            txt = clean_text(caption_el.get_text())
            if txt:
                items.append({'type': 'paragraph', 'text': '[Figure] ' + txt})

    elif child.name in ('h3', 'h4'):
        items.append({'type': 'heading', 'level': 3 if child.name == 'h3' else 4, 'text': clean_text(child.get_text())})

    return items


def extract_table_data(tbl):
    headers, rows = [], []
    thead, tbody = tbl.find('thead'), tbl.find('tbody')
    if thead:
        headers = [clean_text(th.get_text()) for th in thead.find_all('th')]
    if tbody:
        for tr in tbody.find_all('tr'):
            row = [clean_text(td.get_text()) for td in tr.find_all('td')]
            if row:
                rows.append(row)
    if not headers and not rows:
        all_rows = tbl.find_all('tr')
        for tr in all_rows:
            row = [clean_text(c.get_text()) for c in tr.find_all(['td', 'th'])]
            if row:
                rows.append(row)
    return {'headers': headers, 'rows': rows}


def extract_standard_refs(ref_section):
    refs = []
    for item in ref_section.find_all(class_='ref-item'):
        txt = clean_text(item.get_text())
        a = item.find('a')
        link = a.get('href', '') if a else ''
        if txt:
            refs.append({'text': txt, 'url': link})
    return refs


def extract_ref_list_items(ref_div):
    refs = []
    for ol in ref_div.find_all('ol', class_='ref-list'):
        for li in ol.find_all('li', recursive=False):
            txt = clean_text(li.get_text())
            a = li.find('a')
            link = a.get('href', '') if a else ''
            if txt:
                refs.append({'text': txt, 'url': link})
    return refs


def deduplicate_refs(refs):
    seen, unique = set(), []
    for ref in refs:
        key = ref['text'][:100]
        if key not in seen:
            seen.add(key)
            unique.append(ref)
    return unique


def extract_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'noscript', 'svg', 'head']):
        tag.decompose()

    if soup.find('header', class_='report-head'):
        return extract_nlp_report(soup)
    return extract_standard_report(soup)


if __name__ == '__main__':
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    MANIFEST_PATH = os.path.join(SCRIPT_DIR, '.report_manifest.json')
    OUT_DIR = os.path.join(SCRIPT_DIR, 'extracted_json')

    if not os.path.exists(MANIFEST_PATH):
        print('ERROR: Manifest not found. Run sync_reports.py first.')
        sys.exit(1)

    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)

    os.makedirs(OUT_DIR, exist_ok=True)

    for entry in manifest:
        html_path = entry['html_path']
        slug = entry['slug']

        if not os.path.exists(html_path):
            print(f'SKIP: {html_path} (not found)')
            continue

        print(f'Extracting: {slug}')
        content = extract_html(html_path)

        out_path = os.path.join(OUT_DIR, f'{slug}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

        print(f'  Title: {content["title"][:80]}...')
        print(f'  Sections: {len(content["sections"])}  Refs: {len(content["references"])}')

    print('\nDone.')
