# 月度论文与多语言更新

工作流：`.github/workflows/monthly-site-update.yml`。每月 1 日北京时间 09:17 由 GitHub Actions 执行，也可在 Actions 页面点击 Run workflow 手动执行。GitHub 定时任务可能排队延迟，不是精确计时服务。

## 执行顺序

1. 从 DBLP 官方 SPARQL 查询用户指定的 `55/1198` 作者记录，按作者署名序号恢复完整顺序。
2. 分页检查指定 Google Scholar 资料页。遇到 HTTP 429、验证码或页面结构变化时记录访问失败，不绕过验证，不删除已有论文。作者或出版链接不完整的新增记录留在运行报告中等待核对。Scholar 独有条目还必须匹配 Crossref 的学术论文记录和完整作者信息，才会自动入库；专利、数据集和无可靠匹配的记录不会自动混入论文目录。
3. 按 DBLP 记录地址、DOI、规范化标题去重。仅增补，或将已知预印本提升为正式出版版本；保留现有配图、PDF 和人工分类。新增论文仅根据明确的标题关键词分类，没有依据的留在全部论文中。
4. 以英文页面为内容来源，检查中文、法文、阿拉伯文和日文翻译字典。新增正文调用 Kimi API 翻译，再用独立请求校对。无新增文案时不调用 API。作者姓名、公司名称、论文标题、期刊名和 BibTeX 保留原文，便于学术检索。
5. 生成五种语言，读取英文 Members 和 Alumni 名单并加粗匹配作者。检查每页语言、漏译、语言菜单目的页、导航、页内锚点、图片/PDF 路径、论文重复和作者顺序。
6. 所有检查通过才提交并推送 main。失败的生成结果留在临时运行环境，不会发布。两处文献来源都失败时停止，不推送；单处失败时在运行摘要中明确提示。
7. 有新提交且配置了部署钩子时发起 HTTPS POST；否则依赖托管平台的 GitHub 连续部署。每次运行的来源状态、新增论文和待核对记录保存在 `monthly-update-report` artifact 中，保留 90 天。

## 交给 Kimi 配置的内容

GitHub → 仓库 Settings → Secrets and variables → Actions：

| 设置 | 类型 | 用途 |
| --- | --- | --- |
| `MOONSHOT_API_KEY` | Secret | 新增英文正文的自动翻译及校对；不要写入源码或聊天记录 |
| `TRANSLATION_MODEL` | Variable，可选 | 默认 `kimi-k2.5`，按账号可用模型调整 |
| `TRANSLATION_BASE_URL` | Variable，可选 | 默认 `https://api.moonshot.cn/v1`；使用其他兼容账号区域时调整 |
| `KIMI_DEPLOY_HOOK_URL` | Secret，可选 | 托管平台提供的、支持无正文 HTTPS POST 的部署钩子；只有平台实际提供时才填写 |

仓库的 Actions 需启用，并允许工作流读写仓库内容。如果 main 有保护规则，需为此工作流配置允许的提交方式；不要在任务中强行绕过保护。

**线上自动更新还需要部署联动。** 静态网页本身不能定时执行 Python。Kimi 需要将部署绑定到 GitHub main 的提交更新，或配置平台提供的部署钩子。如果 Kimi 使用一次性 ZIP 部署且没有持续部署/定时运行能力，工作流只会更新 GitHub，线上网站不会自动更新；此时应改用支持 GitHub 连续部署的托管方式。

网站当前可直接部署，不需要 API 密钥。密钥仅供维护任务在出现新正文时使用；缺少密钥时，任务会停止而不是发布未翻译内容。翻译 API 的调用按账号计费。

## 本地维护与验证

```sh
python3 -m pip install -r scripts/requirements.txt
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/update_publications.py --dry-run
python3 scripts/translate_locales.py
python3 scripts/build_locales.py
python3 scripts/build_publications.py
python3 scripts/check_publications.py
python3 scripts/check_locales.py
```

确认新论文后执行不带 `--dry-run` 的更新，再生成与检查。英文页面是正文来源；翻译词条在 `data/locales/{zh,fr,ar,ja}.json`。不要只编辑已生成的译文 HTML，否则下次生成会被覆盖。保留人名的拉丁字母拼写，校友名单中的 now、summer、Remote co-supervision 等身份附注会本地化。

新增页面时同步 `scripts/build_locales.py` 的页面目录；新增语言时同步语言目录、论文界面词条和研究方向名称。漏译检查不会静默回退到英文。

参考：[DBLP 官方查询服务](https://sparql.dblp.org/)、[Kimi API 快速开始](https://platform.kimi.com/docs/api/quickstart)、[GitHub 工作流语法](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)、[GitHub Secrets](https://docs.github.com/en/actions/reference/security/secrets)。
