# 论文目录维护

## 数据与生成

- `publications.json` 是五种语言论文页共享的数据源；网站本身不需要构建。
- 修改数据后，在仓库根目录运行 `python3 scripts/build_publications.py`，然后运行 `python3 scripts/check_publications.py`。
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

- 优先保留原网站已有论文图；新增图来自公开可获取的 PDF Figure 1。
- 每张新增配图在 JSON 中记录来源 PDF、页码、裁切坐标和图注。
- `images/papers/` 为新提取的配图；`images/Publication/` 保留已有论文图片。
- 没有可靠原图的条目使用纯文字排版，不使用生成图或无关封面。
- 缩略图和标题使用同一个出版社/数字图书馆链接；DOI 链接由 DOI 系统跳转到出版页面。预印本链接到 arXiv 等文献库。
- PDF 全文仅临时用于提图；本次未将新下载全文上传到仓库。

## 核验范围

已检查数据去重、五语言记录一致性、全部本地图片和 PDF 路径、搜索/筛选、BibTeX 弹窗、标题与配图链接一致性。出版社可能限制机器人访问或要求订阅；不以网络状态码作为撤下已核实论文的依据。

## 作者加粗

生成脚本读取英文成员页 `members/index.html` 的姓名和校友页 `alumni/index.html` 的全部名单，在五种语言论文页中加粗匹配作者。匹配忽略大小写、空格、连字符和括号昵称，保留论文原始姓名拼写与顺序，不进行模糊匹配。更新成员或校友名单后，重新运行 `python3 scripts/build_publications.py` 即可同步。

## 研究方向分类

`research-topics.json` 定义项目页六个方向及五种语言名称；每篇论文的 `topics` 字段保存可编辑的分类 ID。同一论文可有多个方向，项目卡片数量因此不能相加作为论文总数。

分类依据论文标题、研究用途及可用摘要作编辑归类，不代表原出版物声明的分类。可访问性涵盖无障碍输入、老年用户、受限场景与晕动症等使用障碍；眼动方向同时涵盖眼动交互与基于眼动数据的研究；Web 3D 仅纳入有明确在线三维场景依据的条目。不明确属于六个方向的历史记录仍保留在全部论文中。

分类链接采用 `publications/index.html?topic=eye-tracking`，可叠加 `year`、`type`、`q` 参数；刷新、前进后退与语言切换会保持筛选条件。生成脚本同时更新五种语言的项目卡片、论文数量和分类选项。

## 定期维护

月度来源检查、自动翻译、失败处理和部署联动见 [AUTOMATION.md](AUTOMATION.md)。日语入口为 `ja/publications/index.html`。
