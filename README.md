# FIT-AWE Lab website

香港科技大学（广州）FIT-AWE 实验室官网：[fit-awe.github.io](https://fit-awe.github.io/)。官方仓库为 [fit-awe/fit-awe.github.io](https://github.com/fit-awe/fit-awe.github.io)，GitHub Pages 从 `main` 根目录发布。纯静态 HTML / CSS / JavaScript，默认英文，保留中文、法文、阿拉伯文和日文。

**FIT = Future Interaction Technology**

**AWE = Arts, Work, Entertainment**

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
| 国际合作教师、当前任职、头像来源与优先展示 | `data/international-collaborators.json`；核实记录见 [COLLABORATORS.md](data/COLLABORATORS.md) |
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
python3 scripts/check_images.py
```

`build_site.py` 是整站构建入口，会从共享记录生成首页与完整页面、重算最新 6 篇论文，并生成响应式图片。单独运行 `build_publications.py` 后也应执行整站构建，以更新个人页和压缩图片。

构建还会自动压缩页面使用的照片、论文图和头像，生成 `images/optimized/` 下的 WebP 版本及 `data/image-variants.json`。原图保留，浏览器通过 `srcset` 按屏幕宽度和像素密度选择图片；正文以下图片延迟加载。替换图片时更新原始来源路径；成员页已有图片可通过 `data-image-source` 指向原图，避免重新压缩已生成的缩略图。压缩结果按内容缓存，月度更新会自动生成并验证新增图片的网页版本。

媒体报道和演讲使用简短新闻摘要展示。`data/news.json` 中的 `source` 会显示为相关链接，`source_label` 可指定“阅读报道”或“观看视频”等文字；省略时显示“相关链接”。链接文字通过 `data/locales/*.json` 同步翻译；外部来源在新标签页打开。活动日期与来源发布日期分别记录；TEDx 记录使用视频发布日期。

## 页面与交互

- 字体：正文约 18px，辅助信息约 15–16px，论文作者约 16–17px；字号使用 `rem`，跟随浏览器默认字号，按钮点击区域至少 44px。

- About：实验室简介、标题旁的 FIT/AWE 释义，以及两张合影轮播；桌面文字与照片框上下对齐，照片居中裁切，手机保留照片原比例。Lab updates 位于桌面右上方并随滚动固定，窄屏显示在 About 下方。随后依次展示论文奖项、最新论文、合作及招募，学校与 CMA Logo 位于首页底部。照片自动切换，悬停或键盘聚焦时暂停，也可聚焦后使用方向键切换；不显示箭头和页码。
- Members：Faculty、PhD、MPhil、International Collaborators、Alumni；缺少真实头像时使用姓名首字母。国际合作教师按共同论文与经核实的领域资历优先展示，合作论文数量与作者筛选在构建时自动更新。
- Publications：按年份及已知发表日期倒序排列，桌面每行依次展示会议／期刊与年份、配图、标题及作者；缺图时文字扩展，手机纵向显示。顶部直接点击研究方向，并可搜索；年份与类型按钮位于“更多筛选”。`q`、`year`、`type`、`topic` 分享参数兼容刷新、浏览器历史和语言切换；支持 BibTeX 和 PDF 下载。补充材料单独标注，部分出版版链接到原站 PDF。
- Paper Awards：紧凑的两列列表，左侧会议／期刊及年份，右侧奖项或提名与论文标题。奖项名称链接到核实来源，论文标题链接到出版页面；提名与学生游戏竞赛决赛入围明确标注，包含成员早期成果。
- 页头导航：About、Members、Awards、Publications、Collaboration、Join Us，以及语言切换。News 通过首页 Lab updates 的“查看更多”入口访问。
- Teams、Projects 已退出导航；旧链接跳转至 Members 或 Publications。校友旧入口转到 Members 的 Alumni 分区。

## 论文与定期维护

论文数据、配图、日期精度与作者加粗见 [data/PUBLICATIONS.md](data/PUBLICATIONS.md)。月度工作流为 `.github/workflows/monthly-site-update.yml`，每月 1 日北京时间 09:17 检查 DBLP / Google Scholar、生成并核验五种语言与共享摘要，通过后提交并请求 GitHub Pages 发布。新英文文案的 API 翻译设置和 Kimi 部署联动见 [data/AUTOMATION.md](data/AUTOMATION.md)。

## 许可

旧网站基于 Allan Lab 学术网站模板，原模板采用 MIT License；保留第三方库原有声明。新版页面采用自托管 Source Sans 3 字体，字体许可在 `fonts/OFL.txt`。论文、照片和机构标识不因代码或字体许可而重新授权。
