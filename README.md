# FIT-AWE Lab website

香港科技大学（广州）FIT-AWE 实验室官网。默认入口为英文首页，用户可从语言菜单切换中文、法文、阿拉伯文或日文。纯静态 HTML / CSS / JavaScript，可直接部署仓库根目录。

## 预览

```sh
python3 -m http.server 8000
```

打开 `http://localhost:8000`；中文首页为 `http://localhost:8000/zh/`。

## 部署

- 类型：静态网站，无需安装依赖、构建或环境变量。
- 发布目录：仓库根目录 `.`。
- 首页：`index.html`；中文、法文、阿拉伯文、日文在 `zh/`、`fr/`、`ar/`、`ja/`。
- 保留目录结构、文件名大小写和含空格的文件名。
- 按真实路径提供 HTML、图片、字体和 PDF；支持目录的 `index.html`。
- 不要把所有请求重写到首页：这是多页面网站。
- `404.html` 可作为静态 404 页面。
- 已删除原模板的 Allan Lab 域名配置。新域名按实际部署平台配置。
- `.nojekyll` 用于支持直接托管已有静态文件。

给 Kimi 的部署说明见 [KIMI_DEPLOY.md](KIMI_DEPLOY.md)。私有仓库需要授权访问，也可以下载仓库 ZIP 交给 Kimi。

## 内容维护

| 内容 | 路径 |
| --- | --- |
| 英文首页 | `index.html` |
| 中文首页 | `zh/index.html` |
| 团队 / 成员 / 校友 | `teams/` / `members/` / `alumni/` |
| 项目 / 论文 | `projects/` / `publications/` |
| 共享论文数据 / 维护说明 | `data/publications.json` / `data/PUBLICATIONS.md` |
| 动态 / 招募 / 合作 | `allnews.html` / `vacancies/` / `entrepreneurship/` |
| 共享基础样式 / 调整样式 | `css/main.css` / `css/refinements.css` |
| 图片 / 论文 PDF | `images/` / `downloads/publication/` |

英文页面是正文来源；其他语言由 `scripts/build_locales.py` 和 `data/locales/` 的翻译字典生成。论文由共享 JSON 生成。修改英文后运行翻译、生成与检查脚本，不能只改译文 HTML。部署仍可直接使用仓库里的静态 HTML。

## 本次精简

- 四种语言首页正文减少约 83–84%，保留简介、入口、两条动态、联系方式和招募入口。
- 精简研究团队、项目与合作页面，完整成员、校友、论文和新闻仍可访问。
- 移除原模板物理实验室照片、仪器与相册内容、过时附件和隐藏页脚；旧仪器与相册地址转到研究项目页。
- 修正本地论文 PDF 路径、成员页脚本路径和旧团队页语言链接。
- 导航适配手机和平板；卡片使用可键盘访问的链接；移除外部字体请求。
- 修复论文页响应式断点；合并重复的 BibTeX 弹窗，支持按 Escape 关闭。

论文目录已按 DBLP、OpenAlex 和 Crossref 元数据重新核对，默认列出全部论文，支持搜索、年份与类型筛选。论文图片和标题链接到出版页面。数据覆盖范围、Google Scholar 访问限制及未确认条目见 [论文维护说明](data/PUBLICATIONS.md)。新闻仍保留原有内容。

## 模板来源

网站沿用 Allan Lab 学术网站模板及 Bootstrap / Bootswatch 样式。原模板页面标注代码采用 MIT License；第三方库头部保留其原有版权和许可声明。论文、照片和机构标识不因代码模板许可而重新授权。

## 月度自动更新

每月 1 日北京时间 09:17，GitHub Actions 检查 DBLP / Google Scholar、同步五种语言并核验成员与校友作者加粗。Kimi 部署需连接 main 的持续部署或平台部署钩子。API 密钥、运行步骤和限制见 [自动更新交接说明](data/AUTOMATION.md)。
