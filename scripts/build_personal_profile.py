#!/usr/bin/env python3
"""Build Liang's bilingual profile from the existing shared academic records."""
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

from publication_common import author_key, bibtex, esc

ROOT = Path(__file__).resolve().parents[1]
ROUTE = 'members/haining-liang/index.html'
LABELS = {
    'en': {
        'page_title': 'Hai-Ning Liang | HKUST(GZ)',
        'description': 'Hai-Ning Liang, Associate Professor and Deputy Thrust Head of Computational Media and Arts at HKUST(GZ). Biography, selected publications, academic service, teaching and contact.',
        'skip': 'Skip to content', 'menu': 'Toggle navigation', 'navigation': 'Main navigation',
        'about': 'About', 'publications': 'Publications', 'service': 'Service', 'teaching': 'Teaching', 'contact': 'Contact',
        'position': 'Associate Professor · Deputy Thrust Head', 'thrust': 'Computational Media and Arts Thrust',
        'university': 'The Hong Kong University of Science and Technology (Guangzhou)',
        'affiliation_short': 'Computational Media and Arts · HKUST(GZ)',
        'office': 'Room 507, Building E1, HKUST(GZ)', 'city': 'Guangzhou, China',
        'portrait_alt': 'Portrait of Hai-Ning Liang', 'profile_links': 'Academic profiles and contact',
        'email_label': 'Email', 'faculty_label': 'Faculty profile',
        'opportunity_text': 'Interested in joining our group?', 'openings_label': 'See opportunities at FIT-AWE',
        'selected_work': 'Selected work', 'all_publications': 'Full publication list',
        'filter_year': 'Filter selected publications by year', 'all_years': 'All years',
        'search_label': 'Search selected publications', 'search_placeholder': 'Search selected papers…',
        'count_template': '{shown} of {total} selected publications',
        'empty': 'No matching papers. Try another keyword or year.', 'clear': 'Clear filters',
        'catalog_note': 'A selection of recent publications.', 'browse_catalog': 'Browse the complete catalog',
        'community': 'Academic community', 'conference_service': 'Conference organization', 'editorial_service': 'Editorial roles',
        'schedule': 'Course schedule', 'get_in_touch': 'Get in touch',
        'lab_description': 'For our research, group members and opportunities, visit the FIT-AWE Lab.',
        'visit_lab': 'Visit FIT-AWE Lab', 'back_to_top': 'Back to top',
        'copy': 'Copy BibTeX', 'copied': 'Copied', 'copy_failed': 'Select the citation and copy it manually.',
        'close': 'Close citation', 'citation_label': 'BibTeX citation', 'paper': 'Paper',
        'pdf_label': 'Read PDF', 'cite': 'Cite', 'co_taught': 'Co-taught',
    },
    'zh': {
        'page_title': '梁海宁 Hai-Ning Liang | 香港科技大学（广州）',
        'description': '梁海宁，香港科技大学（广州）计算媒体与艺术学域副教授、学域副主任。个人简介、精选论文、学术服务、教学与联系方式。',
        'skip': '跳至正文', 'menu': '展开或收起导航', 'navigation': '主导航',
        'about': '简介', 'publications': '论文', 'service': '学术服务', 'teaching': '教学', 'contact': '联系',
        'position': '副教授 · 学域副主任', 'thrust': '计算媒体与艺术学域',
        'university': '香港科技大学（广州）', 'affiliation_short': '计算媒体与艺术 · 香港科技大学（广州）',
        'office': '香港科技大学（广州）E1 楼 507 室', 'city': '中国 · 广州',
        'portrait_alt': '梁海宁个人照片', 'profile_links': '学术资料与联系方式',
        'email_label': '邮件', 'faculty_label': '学校个人资料',
        'opportunity_text': '有兴趣加入我们的团队？', 'openings_label': '查看 FIT-AWE 招募信息',
        'selected_work': '精选成果', 'all_publications': '完整论文列表',
        'filter_year': '按年份筛选精选论文', 'all_years': '全部年份',
        'search_label': '搜索精选论文', 'search_placeholder': '搜索精选论文…',
        'count_template': '显示 {shown} / {total} 篇精选论文',
        'empty': '没有找到匹配的论文，请更换关键词或年份。', 'clear': '清除筛选',
        'catalog_note': '近期论文选辑。', 'browse_catalog': '浏览完整论文目录',
        'community': '学术共同体', 'conference_service': '会议组织', 'editorial_service': '期刊任职',
        'schedule': '课程安排', 'get_in_touch': '欢迎联系',
        'lab_description': '研究方向、团队成员及招募信息，请访问 FIT-AWE 实验室网站。',
        'visit_lab': '访问 FIT-AWE 实验室', 'back_to_top': '返回顶部',
        'copy': '复制 BibTeX', 'copied': '已复制', 'copy_failed': '请选中引用内容并手动复制。',
        'close': '关闭引用', 'citation_label': 'BibTeX 引用', 'paper': '论文',
        'pdf_label': '阅读 PDF', 'cite': '引用', 'co_taught': '共同授课',
    },
}
ROLE_ZH = {
    'Associate Paper Chair': '论文副主席', 'Program Co-chair': '程序委员会联合主席',
    'Paper Awards Committee Chair': '论文奖委员会主席', 'Courses and Workshops Co-chair': '课程与工作坊联合主席',
    'Doctoral Consortium Co-chair': '博士生论坛联合主席', 'Editorial Board Member': '编委',
    'Associate Editor · Technologies for VR': '副编辑 · 虚拟现实技术', 'Section Editor': '栏目编辑',
}
COURSE_ZH = {
    'Introduction to Game Development': '游戏开发导论', 'Advanced Game Development': '高级游戏开发',
    'Independent Study': '独立研究', 'Career Development for Information Hub Students': '信息枢纽学生职业发展',
}


def build():
    profile = json.loads((ROOT / 'data/personal-profile.json').read_text())
    academic = json.loads((ROOT / 'data/academic-profile.json').read_text())
    papers = {p['id']: p for p in json.loads((ROOT / 'data/publications.json').read_text())['publications']}
    selected = [papers[key] for key in profile['selected_publication_ids']]
    assert len({p['id'] for p in selected}) == len(selected), 'Duplicate selected publication'
    assert all(any(author_key(a) == author_key(profile['name']) for a in p['authors']) for p in selected), 'Wrong author'
    template = (ROOT / 'templates/personal-profile.html').read_text()
    for lang, labels in LABELS.items():
        dest = ROOT / ('' if lang == 'en' else lang) / ROUTE

        def asset(path):
            return quote(os.path.relpath(ROOT / path, dest.parent), safe='/')

        def lab_page(path):
            return asset(('' if lang == 'en' else lang + '/') + path)

        values = {k: esc(v) for k, v in labels.items()}
        other = 'zh' if lang == 'en' else 'en'
        values.update({k: esc(profile[k]) for k in ['email', 'scholar', 'dblp', 'faculty_profile']})
        values.update(
            lang=lang, other_lang=other, language_label='中文' if lang == 'en' else 'English',
            language_url=asset(('zh/' if other == 'zh' else '') + ROUTE),
            canonical='https://fit-awe.github.io/' + ('zh/' if lang == 'zh' else '') + 'members/haining-liang/',
            portrait=asset(profile['portrait']), favicon=asset('images/brand/fit-awe-icon.svg'),
            lab_mark=asset('images/brand/fit-awe-icon.svg'), stylesheet=asset('css/personal-profile.css') + '?v=20261009',
            script=asset('js/personal-profile.js') + '?v=20261009',
            lab_url=lab_page('index.html'), openings_url=lab_page('vacancies/index.html'),
            all_publications_url=lab_page('publications/index.html'),
            course_schedule=esc(academic['teaching'][0]['terms'][0]['source']),
            biography=''.join('<p>' + esc(p) + '</p>' for p in profile['biography'][lang]),
            navigation_links=''.join(f'<a href="#{section}"' + (' aria-current="location"' if section == 'about' else '') + f'>{labels[section]}</a>' for section in ['about', 'publications', 'service', 'teaching', 'contact']),
        )
        years = sorted({p['year'] for p in selected}, reverse=True)
        values['year_filters'] = ''.join(f'<button type="button" data-year="{year}" aria-pressed="{str(not year).lower()}">{label}</button>' for year, label in [('', labels['all_years'])] + [(str(y), str(y)) for y in years])
        cards = []
        venues = {'IEEE Trans. Vis. Comput. Graph.': 'IEEE TVCG', 'CHI': 'ACM CHI', 'VR': 'IEEE VR'}
        for p in selected:
            authors = ', '.join(f'<strong>{esc(a)}</strong>' if author_key(a) == author_key(profile['name']) else esc(a) for a in p['authors'])
            figure = ''
            if p.get('image'):
                figure = f'<a class="paper-figure" href="{esc(p["url"])}" target="_blank" rel="noopener noreferrer" tabindex="-1" aria-hidden="true"><img src="{asset(p["image"]["path"])}" alt="" loading="lazy" decoding="async" width="320" height="200"></a>'
            pdf = ''
            if p.get('pdf_url'):
                pdf = f'<a href="{esc(p["pdf_url"])}" target="_blank" rel="noopener noreferrer" aria-label="{labels["pdf_label"]}: {esc(p["title"])}">PDF <span aria-hidden="true">↗</span></a>'
            elif p.get('pdf'):
                pdf = f'<a href="{asset(p["pdf"])}" download aria-label="{labels["pdf_label"]}: {esc(p["title"])}">PDF <span aria-hidden="true">↓</span></a>'
            search = esc(' '.join([p['title'], ' '.join(p['authors']), p['venue'], str(p['year'])]).casefold())
            cards.append(f'''<article class="publication-card" data-paper-id="{p['id']}" data-year="{p['year']}" data-search="{search}">
{figure}<div class="paper-content"><p class="paper-meta"><span class="venue">{esc(venues.get(p['venue'], p['venue']))}</span><span>{p['year']}</span></p>
<h3><a href="{esc(p['url'])}" target="_blank" rel="noopener noreferrer">{esc(p['title'])}</a></h3><p class="paper-authors">{authors}</p>
<div class="paper-links"><a href="{esc(p['url'])}" target="_blank" rel="noopener noreferrer">{labels['paper']} <span aria-hidden="true">↗</span></a>{pdf}<button type="button" data-citation-button aria-label="{labels['cite']}: {esc(p['title'])}" hidden>BibTeX</button></div>
<template class="citation-source">{esc(bibtex(p))}</template></div></article>''')
        values['publication_cards'] = '\n'.join(cards)

        def service_rows(group):
            rows = []
            for record in academic['service']:
                if record['group'] != group:
                    continue
                role = ROLE_ZH.get(record['role'], record['role']) if lang == 'zh' else record['role']
                rows.append(f'<li><a href="{esc(record["source"])}" target="_blank" rel="noopener noreferrer">{esc(record["name"])} <span aria-hidden="true">↗</span></a><span>{esc(role)}</span></li>')
            return '\n'.join(rows)

        values['conference_rows'] = service_rows('conference')
        values['editorial_rows'] = service_rows('editorial')
        teaching = []
        for record in academic['teaching']:
            if record['institution'] != 'hkust-gz':
                continue
            course = COURSE_ZH.get(record['name'], record['name']) if lang == 'zh' else record['name']
            term = record['terms'][0]
            term_label = term['label']
            if lang == 'zh':
                term_label = term_label.replace('Fall', '秋季').replace('Spring', '春季')
            note = '<span class="course-note">' + labels['co_taught'] + '</span>' if record.get('note') == 'Co-taught.' else ''
            teaching.append(f'<li><span class="course-code">{esc(record["code"])}</span><span class="course-name">{esc(course)}{note}</span><a class="course-term" href="{esc(term["source"])}" target="_blank" rel="noopener noreferrer">{esc(term_label)} <span aria-hidden="true">↗</span></a></li>')
        values['teaching_rows'] = '\n'.join(teaching)
        values['person_schema'] = json.dumps({
            '@context': 'https://schema.org', '@type': 'Person', 'name': profile['name'],
            'alternateName': [profile['chinese_name'], 'Haining Liang'], 'url': values['canonical'],
            'image': 'https://fit-awe.github.io/' + profile['portrait'], 'email': profile['email'],
            'jobTitle': labels['position'], 'worksFor': {'@type': 'CollegeOrUniversity', 'name': labels['university']},
            'sameAs': [profile['faculty_profile'], profile['scholar'], profile['dblp']],
        }, ensure_ascii=False).replace('<', '\\u003c')
        rendered = re.sub(r'\{\{([a-z_]+)\}\}', lambda m: values[m[1]], template)
        assert '{{' not in rendered, 'Unresolved template placeholder'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rendered, encoding='utf-8')
    print('Rendered personal profile in English and Chinese, with 6 selected publications.')


if __name__ == '__main__':
    build()
