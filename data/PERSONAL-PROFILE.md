# Hai-Ning Liang 个人主页

英文地址：`https://fit-awe.github.io/members/haining-liang/`。
中文地址：`https://fit-awe.github.io/zh/members/haining-liang/`。

页面包含简介、学术服务、教学、联系。按站点维护者要求，不设 Research、Awards 或 Publications 栏目；研究方向、获奖信息和论文继续在实验室网站呈现。根据 2026-10-10 的补充要求，简介中简要说明全球前 2% 科学家入选记录和主要任职。

## 维护

- 个人信息：`data/personal-profile.json`。
- 服务与教学：复用 `data/academic-profile.json`。只列 HKUST(GZ) 课程，学期采用对应官方课程表记录。
- 版式与文案：`templates/personal-profile.html`、`scripts/build_personal_profile.py`。
- 样式与交互：`css/personal-profile.css`、`js/personal-profile.js`，与实验室页面的样式隔离。
- 全站生成：`PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_site.py`。单独生成个人主页可运行 `scripts/build_personal_profile.py`。
- 中英文 Members 姓名链接分别进入对应语言个人主页；其他语言的 Members 链接进入英文个人主页。

页面在 JavaScript 禁用时仍显示个人资料与链接。启用 JavaScript 后增加手机折叠菜单和当前栏目提示。

## 内容依据（2026-10-10 核对）

- [CMA 官方简介](https://cma.hkust-gz.edu.cn/faculty-regular/hai-ning-liang/)：副教授身份、2024 年入职、Western University 博士学位、此前在 XJTLU 任职，以及苏州市智能虚拟工程重点实验室和 XJTLU 虚拟工程中心副主任经历。
- [原个人 / 实验室网站](https://hai-ning-liang.github.io/)：2019–2023 年系主任任期与邮件地址。办公室根据站点维护者 2026-10-09 的指令更新为 E3 602。
- 学域副主任：沿用已发布的 Members 职务与 `data/academic-profile.json` 中站点维护者于 2026-10-07 确认的任职记录。CMA 官方简介当前未单列该职务。
- [IEEE ISMAR 2026](https://www.ieeeismar.net/2026/committee/organizing/)、[IEEE ICDM 2025](https://www3.cs.stonybrook.edu/~icdm2025/organizingcommittee.html)、[Graphics Interface 2025](https://conferences.graphicsinterface.org/2025/committee/)：会议服务。
- 简介中概述 [The Visual Computer 编委](https://link.springer.com/journal/371/editorial-board)、[Frontiers in Virtual Reality 副编辑](https://www.frontiersin.org/journals/virtual-reality/sections/technologies-for-vr/editors)，以及 IEEE ISMAR 2026、[VINCI 2025](https://vinci2025.games.cg.jku.at/committee/) 和 IEEE ICDM 2025 的主要会议任职。2026-10-10 核对期刊和会议官网；The Visual Computer 和 International Journal of Serious Games 仍列本人，机构文字尚未更新。
- 全球前 2% 科学家：[Stanford–Elsevier 2026 版原始数据库](https://elsevier.digitalcommonsdata.com/datasets/btchxktzyw/9)，2026-10-07 发布，年度影响力数据对应 2025 年引用。已下载并核对文件 SHA-256；`Table_1_Authors_singleyr_2025_pubs_since_1788_wopp_extracted_202608.xlsx` 的 `Data` 表第 139580 行为 `Liang, Hai Ning`，机构为香港科技大学（广州）。原始记录和文件哈希保存在 `data/personal-profile.json` 的 `recognition.source_record` 中。页面标明“2026 版年度影响力榜单”。
- [2026–27 秋季课程表](https://w5.hkust-gz.edu.cn/wcq/cgi-bin/2610/instructor/LIANG%2C%20Haining)、[2025–26 春季课程表](https://w5.hkust-gz.edu.cn/wcq/cgi-bin/2530/instructor/LIANG%2C%20Haining)：课程与共同授课记录。

视觉参考：[Mingming Fan](https://www.mingmingfan.com/)、[Zeng Wei](https://zeng-wei.com/)。采用照片、简短学术简介与清晰导航；未复制参考网站代码或个人资料。
