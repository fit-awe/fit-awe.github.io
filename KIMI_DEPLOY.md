# 给 Kimi 的部署与更新说明

## 可直接交给 Kimi 的说明

> 请部署 FIT-AWE 实验室官网，源仓库是 https://github.com/fit-awe/fit-awe.github.io ，使用 main。现有网站已经是可运行的纯静态多页面网站，英文入口为根目录 index.html。请直接部署，不要重新生成设计或按浏览器语言自动跳转。发布目录为仓库根目录，无需 npm install。保留 /zh/、/fr/、/ar/、/ja/、各语言的 awards/publications/members 等子页面、图片、字体、JavaScript 和 downloads/publication 下的 PDF。按实际路径提供文件，不要将所有路径回退到首页。请检查手机导航、语言切换、论文按钮组合筛选及 BibTeX。部署完成后返回访问地址。

| 参数 | 值 |
| --- | --- |
| 项目类型 | Static / Other |
| 分支 / 根目录 | `main` / `.` |
| 安装命令 / 构建命令 | 留空 |
| 发布目录 | `.` |
| 网页运行环境变量 / 数据库 | 无 |

## 保持定期更新

官网仓库包含 `.github/workflows/monthly-site-update.yml`，每月 1 日北京时间 09:17 检查论文来源，并从共享数据重新生成首页最新论文、新闻摘要、奖项和五种语言页面。说明见 `data/AUTOMATION.md`。

1. 绑定 GitHub `main` 的更新以重新部署，或配置托管平台实际提供的 `KIMI_DEPLOY_HOOK_URL`。一次性 ZIP 上传需要后续手动重新部署，不能自动获得新论文。
2. 新英文简介、新闻或其他文案的自动翻译与校对使用仓库 Secret `MOONSHOT_API_KEY`；不要将密钥放进网页或源码。只更新论文题目、作者、刊名时保留原文，无需翻译 API。
3. 内容修改请遵循 `README.md` 的来源表：首页和招募改模板；新闻、奖项和论文改共享 JSON；成员及校友在英文 Members 页面维护。译文和首页摘要由生成脚本同步。
4. 如需重新生成，安装 `scripts/requirements.txt`，运行 `python3 scripts/translate_locales.py`、`python3 scripts/build_site.py` 和三个 `check_*.py` 内容检查。部署现有静态文件不需要 Python。
5. 将一个新提交部署后，核对实际线上内容与该提交一致，再确认持续部署已生效。

现有 GitHub Pages 网站由官方仓库 `main` 发布。工作流自动提交后会显式请求 Pages 构建，以适配自动提交不会再次触发普通 push 工作流的情况；Kimi 平台仍需自己的 GitHub 联动或部署钩子。
