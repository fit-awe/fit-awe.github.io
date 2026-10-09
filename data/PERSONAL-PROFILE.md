# Hai-Ning Liang 个人主页

英文地址：`https://fit-awe.github.io/members/haining-liang/`。
中文地址：`https://fit-awe.github.io/zh/members/haining-liang/`。

页面仅包含简介、精选论文、学术服务、教学、联系。按站点维护者要求，不设 Research 或 Awards 栏目；研究方向和获奖信息继续在实验室网站呈现。

## 维护

- 个人信息与论文选辑：`data/personal-profile.json`。
- 论文标题、作者、年份、图片、PDF、DOI 与 BibTeX：复用 `data/publications.json` 和 `scripts/publication_common.py`。
- 服务与教学：复用 `data/academic-profile.json`。只列 HKUST(GZ) 课程，学期采用对应官方课程表记录。
- 版式与文案：`templates/personal-profile.html`、`scripts/build_personal_profile.py`。
- 样式与交互：`css/personal-profile.css`、`js/personal-profile.js`，与实验室页面的样式隔离。
- 全站生成：`PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_site.py`。单独生成个人主页可运行 `scripts/build_personal_profile.py`。
- 中英文 Members 姓名链接分别进入对应语言个人主页；其他语言的 Members 链接进入英文个人主页。

页面在 JavaScript 禁用时仍显示全部选辑、个人资料与链接。启用 JavaScript 后增加论文搜索、年份筛选、原生 BibTeX 对话框和手机折叠菜单。引用从共享论文数据生成，标题与作者保留原文。

## 内容依据（2026-10-09 核对）

- [CMA 官方简介](https://cma.hkust-gz.edu.cn/faculty-regular/hai-ning-liang/)：副教授身份、2024 年入职、Western University 博士学位、此前在 XJTLU 任职。
- [原个人 / 实验室网站](https://hai-ning-liang.github.io/)：2019–2023 年系主任任期、办公室与邮件地址。
- 学域副主任：沿用已发布的 Members 职务与 `data/academic-profile.json` 中站点维护者于 2026-10-07 确认的任职记录。CMA 官方简介当前未单列该职务。
- [IEEE ISMAR 2026](https://www.ieeeismar.net/2026/committee/organizing/)、[IEEE ICDM 2025](https://www3.cs.stonybrook.edu/~icdm2025/organizingcommittee.html)、[Graphics Interface 2025](https://conferences.graphicsinterface.org/2025/committee/)：会议服务。
- 其他服务记录保留共享档案的来源链接，不新增任职断言；[The Visual Computer 编委页](https://link.springer.com/journal/371/editorial-board)仍列本人，机构文字尚未更新。
- [2026–27 秋季课程表](https://w5.hkust-gz.edu.cn/wcq/cgi-bin/2610/instructor/LIANG%2C%20Haining)、[2025–26 春季课程表](https://w5.hkust-gz.edu.cn/wcq/cgi-bin/2530/instructor/LIANG%2C%20Haining)：课程与共同授课记录。

视觉参考：[Mingming Fan](https://www.mingmingfan.com/)、[Zeng Wei](https://zeng-wei.com/)。采用照片、简短学术简介、清晰导航与图文论文列表；未复制参考网站代码或个人资料。
