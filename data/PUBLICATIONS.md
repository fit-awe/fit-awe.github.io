# 论文目录维护

## PDF 下载统一标签

作者要求暂不开放全文时，设置 `full_text_access: withheld`，移除 `pdf`／`pdf_url` 及线上 PDF 文件，保留目录记录、下载标签与规范引用，页面显示“全文暂未开放”。私有原件和恢复信息存于部署目录之外；不能仅隐藏下载按钮。媒体导入会跳过此类记录，避免下次同步自动重新公开。恢复开放需依据用户新的明确指令。

所有提供 PDF 的条目使用 `第一作者姓氏-会刊简称YY-短标题`，例如 `Shi-ISS26-WindowPlacement.pdf` 与 `Long-VRST26-ScaleCueWIM.pdf`。标签显示在 PDF 操作下方，也可用于目录搜索；五种语言共用同一标签。补充材料以 `-Supplement` 结尾，不能当作全文。

`download_label` 是持久的人工可编辑字段，不包含扩展名。新增 PDF 时先运行 `python3 scripts/publication_labels.py --write`，检查作者姓氏、会刊简称及短标题，再构建。脚本保留已有标签，大小写不敏感去重；重名追加稳定的记录标识摘要。已知会议关联按核验结果设置，例如 PACM HCI 的这篇 ISS 2026 论文用 ISS；不能单凭期刊版式猜测会议。预印本使用 arXiv 等实际来源代码。

本地 PDF 的浏览器下载属性使用该标签加 `.pdf`。存储仍按原内容去重，原路径和文件字节不变，已分享的公众号、LinkedIn 和旧下载网址继续有效。外站 PDF 显示同一命名规范的参考标签，但保留原站链接；跨站下载文件名由原站与浏览器决定，不保证重命名。标题、作者顺序、DOI 和 BibTeX 不因标签而改写。

验收包括 `python3 -m unittest discover -s scripts -p 'test_publication_labels.py'`、全站构建及 `check_publications.py`，确认全部下载标签唯一、可搜索、可见且本地下载文件名一致。

## 数据与生成

- `publications.json` 是五种语言论文页共享的数据源；网站本身不需要构建。
- 修改数据后，在仓库根目录运行 `python3 scripts/build_site.py`，然后运行 `python3 scripts/check_publications.py`。
- 维护脚本需要 Python 和 `beautifulsoup4`；部署已生成的网站不需要这些依赖。
- `publication-review.json` 保留原网站中非论文、标题/DOI 不匹配或无法核验的记录，方便日后人工补充；这些记录没有被静默丢弃。

## 2026-09-15 数据来源

1. DBLP：`https://dblp.org/pid/55/1198.html`，通过官方 `https://sparql.dblp.org/sparql` 接口取得全部 321 条署名记录，包含预印本和更正记录。
2. OpenAlex：`https://openalex.org/A5031886887`，分页读取全部 415 条索引记录，用于补充 DBLP 未覆盖的论文、全文位置与作者信息。
3. 原网站 341 条记录：按标题与 DOI 对照；不直接信任原始 BibTeX，因为部分 DOI 指向无关论文。
4. Crossref：通过 DOI 元数据核对未匹配记录的正式标题和作者。
5. Google Scholar：用户提供的 `https://scholar.google.com/citations?user=UJPH5ioAAAAJ` 返回 HTTP 429，无法完整读取；页面保留原资料页入口，未声称逐条核验 Scholar 的全部记录。

同标题的预印本与正式发表版本合并，优先链接正式出版记录；同 DOI 不重复显示。会议整本目录、数据集、专利、视频及无法确定的错误元数据不作为论文混入公开列表。全部 DBLP 来源记录都可以追溯到合并后的条目。

## 配图

- 优先保留原网站已有论文图；新增图从对应 PDF 提取，优先头图或 Figure 1，也使用能更好介绍本研究的系统图、界面图和实验图片。
- 每张新增配图在 JSON 中记录来源 PDF、页码、裁切坐标和图注。
- `images/papers/` 为新提取的配图；`images/Publication/` 保留已有论文图片。
- 没有可靠原图的条目使用纯文字排版，不使用生成图或无关封面。
- 缩略图和标题使用同一个出版社/数字图书馆链接；DOI 链接由 DOI 系统跳转到出版页面。预印本链接到 arXiv 等文献库。

## PDF 与 2026-10-05 配图补充

本次将本地已保存的 220 条 DBLP PDF 记录匹配到 178 个目录条目，合并正式发表与预印本记录的重复版本。新增 82 张经逐张视觉检查的研究图片，配图总计 198 条；本次涉及的缺图条目中，三篇没有研究图的短篇/社论保留文字展示。

论文目录现在有 180 个 PDF 入口，其中 169 个使用官网本地文件并提供直接下载，11 个出版版使用已经核实可访问的原站 PDF 链接。两份补充材料使用“补充材料 PDF”标识，不能当作论文正文；配图可来自这些与论文对应的研究界面补充材料。

- `pdf` 保存本地文件路径，`pdf_url` 保存原站 PDF 链接；保留出版社/文献库入口。
- `pdf_metadata` 保存来源、版本、页数、原文件及托管文件 SHA-256、文件大小。`document_kind: supplement` 标识补充材料；未知版本仍保留为 `unknown`。
- 新文件按内容校验值去重，放在 `downloads/publication/papers/`，不为每种语言重复保存。无损压缩仅优化 PDF 对象和编码，并核对所有页面文字与页数，不降低图片分辨率。
- `publication-pdf-review.json` 记录补充材料和需要链接原站的出版版本；`publication-figure-review.json` 保留已检查图片的页码、裁切坐标、图注及来源校验值。
- `publication-media-import.json` 记录本次导入的目录 ID、文件及校验值。论文和图片的原有声明不因网站代码许可而重新授权。

后续可用同一全文库导入新增材料；图片先检查并在图审记录中标记 `approved`。导入依赖只在整理材料时需要，网站部署和普通构建不需要安装。

```sh
python3 -m pip install -r scripts/requirements-media.txt
python3 scripts/import_publication_media.py --library /path/to/paper-library --figures data/publication-figure-review.json --apply
python3 scripts/build_site.py
python3 scripts/check_publications.py
```

## 核验范围

已检查数据去重、五语言记录一致性、全部本地图片和 PDF 路径、搜索/筛选、BibTeX 弹窗、标题与配图链接一致性。出版社可能限制机器人访问或要求订阅；不以网络状态码作为撤下已核实论文的依据。

## 作者加粗

生成脚本读取英文成员页 `members/index.html` 的成员卡片和 Alumni 分区中的全部名单，在五种语言论文页中加粗匹配作者。匹配忽略大小写、空格、连字符和括号昵称，保留论文原始姓名拼写与顺序，不进行模糊匹配。更新成员或校友名单后，重新运行 `python3 scripts/build_site.py` 即可同步。旧 `alumni/index.html` 仅跳转至 Members 的 Alumni 分区。

## 研究方向分类

`research-topics.json` 定义五个研究方向及五种语言名称，每篇论文的 `topics` 字段保存可编辑的分类 ID。同一论文可有多个方向，各方向数量不能相加作为论文总数。

| 方向 | 分类 ID | 归类范围 |
| --- | --- | --- |
| Gaming | `gaming` | 游戏、体感游戏、严肃游戏、游戏化及玩家体验 |
| Interaction Tech | `interaction-tech` | 交互方法、设备、界面、输入反馈、XR、眼动交互、具身交互与交互可视化 |
| Text Entry | `text-entry` | 文字／字符输入、键盘、打字、文字选择、编辑与纠错；不把一般阅读、字幕或写作教学算作输入技术 |
| AI | `ai` | 机器学习、计算机视觉、神经网络、智能体、语言模型及有明确 AI 方法或主题的研究；一般教育“学习”、统计分析、传统优化或个性化不自动等于 AI |
| Accessibility | `accessibility` | 老年与残障用户、康复、无障碍设计及明确降低使用障碍的方法；免手持输入须结合实际研究动机，普通健康应用不自动归入 |

2026-10-16 重新检查 393 条目录记录的题名与主题，结合可用全文和出版方／作者摘要补充人工分类，不代表已逐篇核验全部全文。人工结果直接保存在 `publications.json`；`update_publications.py` 的 `topic_tags()` 仅为新增记录提供初步分类，合并时保留已有人工分类。没有明确对应方向的历史论文继续出现在 All，避免把材料、网络或教学记录强行塞入交互或 AI 类别。

边界核对示例：[AdaptiveVoice 的作者摘要](https://rochester-bear-lab.github.io/publications/2024-adaptivevoice.html)描述组合优化的自适应语音界面，归 Interaction Tech；[3D-PV 的出版方摘要](https://www.sciencedirect.com/science/article/pii/S0957417425024868)描述 3DGS 与语义融合预测方法，归 AI。本地 `Duo Streamers`、`CountingFruit`、`CD-UDepth` 与晕动症预测论文的正文用于核对标题未显式写出 AI 的方法；`Hands-free multi-type character text entry` 与 `Exploration of Hands-free Text Entry Techniques` 的引言明确讨论手／臂功能受限用户，交叉归入 Text Entry、Interaction Tech 与 Accessibility。

分类链接采用 `publications/index.html?topic=text-entry`，可叠加 `year`、`type`、`q` 参数；刷新、前进后退与语言切换会保持筛选条件。旧 `games` 链接转为 `gaming`，旧 `experience`、`eye-tracking`、`web3d` 链接转为 `interaction-tech`；已取消的宽泛 `applications` 链接回到 All，保留其他条件。页面只显示新五类，不再显示 Web 3D。年份和类型按钮位于“更多筛选”；带有年份或类型参数的链接会自动展开。每组单选，各组组合，保留搜索、数量和清除功能。

论文列表按目录年份倒序，同一年内按已知首次在线发表日期从新到旧排序，同时间记录保持原目录顺序，只有年份的记录排在该年已知日期之后。会议或期刊与目录年份合并显示在左侧，不单列年份标题；日期完整值仍保留在数据及屏幕阅读器可读的时间标签中。常见刊名缩写仅用于显示，完整名称和原始数据保留。

## 定期维护

月度来源检查、自动翻译、失败处理和部署联动见 [AUTOMATION.md](AUTOMATION.md)。日语入口为 `ja/publications/index.html`。

## 2026-10-22 作者提供的两篇已录用论文

新增 ScaleCue-WIM（ACM VRST 2026）与 Hand-based Window Placement（ACM ISS 2026 / PACM HCI），均依据作者提供的完整具名 PDF 及录用确认整理，保留原作者顺序。目录显示“已录用”，未将预计的 2026 年 11 月出版月份当作已发生的在线发表日期。目录由 393 条增至 395 条，两篇均归 Interaction Tech。

两份 PDF 首页均声明 CC BY 4.0，按原始字节保存于 `downloads/publication/papers/2026-scalecue-wim.pdf` 和 `2026-window-placement.pdf`；校验值、页数及原始声明记录于各条 `pdf_metadata`。图 1 直接来自对应 PDF，未使用概念封面代替研究图片。

每条记录提供可下载的本地全文，标题、图片和“查看论文”也指向该全文。DOI 字段按稿件保留；本轮 DOI 注册查询尚未返回元数据，不将其作为唯一全文入口。两篇的规范 BibTeX 保存在记录和对应 `.bib` 文件中，引用按钮优先使用该规范文本。可通过 `publications/?q=ScaleCue-WIM` 和 `publications/?q=window+placement` 分享单篇筛选结果，直接访问 PDF 下载按钮。

## 2026-10-04 日期与首页同步

本次为 334 条记录补充带来源的发表日期元数据，59 条无法获取的记录保留原年份。`published_date` 保存 `YYYY`、`YYYY-MM` 或 `YYYY-MM-DD` 原始精度，`published_date_source` 指向 Crossref 官方 DOI 记录或 arXiv 原始页面，`published_date_basis` 记录元数据字段或首次提交。Crossref 优先使用 `published-online`，没有该字段时才使用其公开出版日期；索引、上传与更新日期不当作发表日期。

首页从目录重算最新 6 篇期刊论文、会议论文和明确标记的预印本，不按是否有配图挑选。按可核实的发表日期降序，只有年份的条目排在该年已知月份/日期之后，相同日期保持目录顺序。可核实的未来发表日期会等到该日期所在期间再进入首页，完整目录保留记录。

已有论文日期补充可运行 `python3 scripts/enrich_publication_dates.py`；来源访问失败不会删除记录。月度脚本为新增和近年的未补充记录查询日期；正式版本替代预印本时，使用正式版本的日期，保留论文 ID、配图和人工分类。所有记录的日期在五种语言中按相同精度显示。

首页、完整论文和 Awards 共用成员及校友作者匹配规则。Awards 只保存关联 ID、奖项类型、年份和来源，完整标题、作者、图片和出版链接复用论文目录。成员早期成果亦纳入 Awards 展示。
