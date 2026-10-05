# FIT-AWE Lab website

香港科技大学（广州）FIT-AWE 实验室官网：[fit-awe.github.io](https://fit-awe.github.io/)。官方仓库为 [fit-awe/fit-awe.github.io](https://github.com/fit-awe/fit-awe.github.io)，GitHub Pages 从 `main` 根目录发布。纯静态 HTML / CSS / JavaScript，默认英文，保留中文、法文、阿拉伯文和日文。

**FIT = Future Interaction Technology**

**AWE = Autonomy + Well-being + Entertainment**

## 预览与部署

```sh
python3 -m http.server 8000
```

打开 `http://localhost:8000/`。其他语言入口为 `/zh/`、`/fr/`、`/ar/`、`/ja/`。

部署现成页面无需安装或构建，发布目录为仓库根目录 `.`。保留目录结构、文件名大小写、图片、字体与 PDF。按真实路径提供各页面，不将所有请求回退到首页。`.nojekyll` 支持直接托管静态文件。Kimi 交接见 [KIMI_DEPLOY.md](KIMI_DEPLOY.md)。

## 修改内容

| 内容 | 编辑来源 |
| --- | --- |
| 首页简介、照片与区块 | `templates/home.html` |
| 新闻与首页最新 3 条动态 | `data/news.json`，保留日期的原始精度 |
| 奖项与首页最新 3 项 | `data/awards.json`，关联论文 ID 并提供来源；核查记录见 `data/AWARDS.md` |
| 全部论文与首页最新 6 篇 | `data/publications.json` |
| 成员、头像、身份与校友 | 英文 `members/index.html` |
| 招募介绍与申请材料 | `templates/join.html` |
| 产学研合作记录 | `scripts/build_content.py` 的 `industry_cards()` |
| 页头、页脚与导航 | `scripts/site_shell.py` |
| 四种译文 | `data/locales/{zh,fr,ar,ja}.json` |
| 全站样式 / 论文样式 | `css/refinements.css` / `css/publications.css` |
| 照片、论文配图 / PDF | `images/` / `downloads/publication/` |

`index.html`、`allnews.html`、`awards/`、`vacancies/`、`entrepreneurship/` 与各语言页面为生成结果；直接修改这些页面会在下次生成时被覆盖。新正文先增加翻译词条，再生成所有页面。月度流程可调用 Kimi API 翻译并独立校对新文案；论文题目、作者与刊名保持原文。

```sh
python3 -m pip install -r scripts/requirements.txt
python3 scripts/translate_locales.py
python3 scripts/build_site.py
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/check_publications.py
python3 scripts/check_locales.py
python3 scripts/check_content.py
```

`build_site.py` 会从共享记录生成首页与完整页面，并重算最新 6 篇论文。原 `build_publications.py` 入口也执行同一整站生成流程。

媒体报道和演讲使用简短新闻摘要展示。`data/news.json` 中的 `source` 会显示为相关链接，`source_label` 可指定“阅读报道”或“观看视频”等文字；省略时显示“相关链接”。链接文字通过 `data/locales/*.json` 同步翻译；外部来源在新标签页打开。活动日期与来源发布日期分别记录；TEDx 记录使用视频发布日期。

## 页面与交互

- About：负责人照片与联系信息、两张合影轮播及其下方最新动态、简短介绍；随后依次展示独立的论文奖项与最新论文区块、产学研合作及招募。照片自动切换，悬停或键盘聚焦时暂停，也可聚焦后使用方向键切换；不显示箭头和页码。首页不展示 Members 区块或独立导师侧栏。
- About 的 Service 与 Teaching：在最新论文之后展示会议任职、期刊编辑工作、校内职务，以及按学校分组的课程；首屏提供直达链接。共享记录及核验范围见 `data/academic-profile.json` 和 `data/ABOUT.md`。
- Members：Faculty、PhD、MPhil、Alumni；占位头像使用姓名首字母。所有现有名单与个人信息保留。
- Publications：按年份及已知发表日期倒序排列，桌面每行依次展示会议／期刊与年份、配图、标题及作者；缺图时文字扩展，手机纵向显示。顶部直接点击研究方向，并可搜索；年份与类型按钮位于“更多筛选”。`q`、`year`、`type`、`topic` 分享参数兼容刷新、浏览器历史和语言切换；支持 BibTeX 和 PDF 下载。补充材料单独标注，部分出版版链接到原站 PDF。
- Paper Awards：紧凑的两列列表，左侧会议／期刊及年份，右侧奖项或提名与论文标题。奖项名称链接到核实来源，论文标题链接到出版页面；提名与学生游戏竞赛决赛入围明确标注，包含成员早期成果。
- News、Industry–Academia Collaboration、Join Us：与首页、页头和页脚使用共享入口。
- Teams、Projects 已退出导航；旧链接跳转至 Members 或 Publications。校友旧入口转到 Members 的 Alumni 分区。

## 论文与定期维护

论文数据、配图、日期精度与作者加粗见 [data/PUBLICATIONS.md](data/PUBLICATIONS.md)。月度工作流为 `.github/workflows/monthly-site-update.yml`，每月 1 日北京时间 09:17 检查 DBLP / Google Scholar、生成并核验五种语言与共享摘要，通过后提交并请求 GitHub Pages 发布。新英文文案的 API 翻译设置和 Kimi 部署联动见 [data/AUTOMATION.md](data/AUTOMATION.md)。

## 许可

旧网站基于 Allan Lab 学术网站模板，原模板采用 MIT License；保留第三方库原有声明。新版页面采用自托管 Source Sans 3 字体，字体许可在 `fonts/OFL.txt`。论文、照片和机构标识不因代码或字体许可而重新授权。
