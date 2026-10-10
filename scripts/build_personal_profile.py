#!/usr/bin/env python3
"""Build Liang's bilingual profile from the existing shared academic records."""
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

from publication_common import esc

ROOT = Path(__file__).resolve().parents[1]
ROUTE = 'members/haining-liang/index.html'
LABELS = {
    'en': {
        'page_title': 'Hai-Ning Liang | HKUST(GZ)',
        'description': 'Hai-Ning Liang, Associate Professor and Deputy Thrust Head of Computational Media and Arts at HKUST(GZ). Biography, academic service, teaching and contact.',
        'skip': 'Skip to content', 'menu': 'Toggle navigation', 'navigation': 'Main navigation',
        'about': 'About', 'service': 'Service', 'teaching': 'Teaching', 'contact': 'Contact',
        'position': 'Associate Professor · Deputy Thrust Head', 'thrust': 'Computational Media and Arts Thrust',
        'university': 'The Hong Kong University of Science and Technology (Guangzhou)',
        'affiliation_short': 'Computational Media and Arts · HKUST(GZ)',
        'office': 'Room 602, Building E3, HKUST(GZ)', 'city': 'Guangzhou, China',
        'portrait_alt': 'Portrait of Hai-Ning Liang', 'profile_links': 'Academic profiles and contact',
        'email_label': 'Email', 'faculty_label': 'Faculty profile',
        'opportunity_text': 'Interested in joining our group?', 'openings_label': 'See opportunities at FIT-AWE',
        'community': 'Academic community', 'conference_service': 'Conference organization', 'editorial_service': 'Editorial roles',
        'schedule': 'Course schedule', 'get_in_touch': 'Get in touch',
        'lab_description': 'For our research, group members and opportunities, visit the FIT-AWE Lab.',
        'visit_lab': 'Visit FIT-AWE Lab', 'back_to_top': 'Back to top',
        'co_taught': 'Co-taught',
    },
    'zh': {
        'page_title': '梁海宁 Hai-Ning Liang | 香港科技大学（广州）',
        'description': '梁海宁，香港科技大学（广州）计算媒体与艺术学域副教授、学域副主任。个人简介、学术服务、教学与联系方式。',
        'skip': '跳至正文', 'menu': '展开或收起导航', 'navigation': '主导航',
        'about': '简介', 'service': '学术服务', 'teaching': '教学', 'contact': '联系',
        'position': '副教授 · 学域副主任', 'thrust': '计算媒体与艺术学域',
        'university': '香港科技大学（广州）', 'affiliation_short': '计算媒体与艺术 · 香港科技大学（广州）',
        'office': '香港科技大学（广州）E3 楼 602 室', 'city': '中国 · 广州',
        'portrait_alt': '梁海宁个人照片', 'profile_links': '学术资料与联系方式',
        'email_label': '邮件', 'faculty_label': '学校个人资料',
        'opportunity_text': '有兴趣加入我们的团队？', 'openings_label': '查看 FIT-AWE 招募信息',
        'community': '学术共同体', 'conference_service': '会议组织', 'editorial_service': '期刊任职',
        'schedule': '课程安排', 'get_in_touch': '欢迎联系',
        'lab_description': '研究方向、团队成员及招募信息，请访问 FIT-AWE 实验室网站。',
        'visit_lab': '访问 FIT-AWE 实验室', 'back_to_top': '返回顶部',
        'co_taught': '共同授课',
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
            lab_mark=asset('images/brand/fit-awe-icon.svg'), stylesheet=asset('css/personal-profile.css') + '?v=20261010-readable1',
            script=asset('js/personal-profile.js') + '?v=20261009-profile2',
            lab_url=lab_page('index.html'), openings_url=lab_page('vacancies/index.html'),
            course_schedule=esc(academic['teaching'][0]['terms'][0]['source']),
            biography=''.join('<p>' + esc(p) + '</p>' for p in profile['biography'][lang]),
            navigation_links=''.join(f'<a href="#{section}"' + (' aria-current="location"' if section == 'about' else '') + f'>{labels[section]}</a>' for section in ['about', 'service', 'teaching', 'contact']),
        )

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
    print('Rendered personal profile in English and Chinese: About, Service, Teaching and Contact.')


if __name__ == '__main__':
    build()
