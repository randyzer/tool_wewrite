# WeWrite

公众号内容全流程 AI Skill —— 从热点抓取到草稿箱推送，一句话搞定；每个环节也能单独调用。

安装后对你的 Agent 说「写一篇公众号文章」跑完整管道，或者只要哪步用哪步：
`/wewrite-topic` 出选题、`/wewrite-visual` 配封面、`/wewrite-review` 查 AI 味、
`/wewrite-rewrite` 一稿改写成小红书/抖音版。兼容 Claude Code、OpenClaw、Codex，
以及任何支持 Agent Skills 规范的宿主。

## 它能做什么

```
"写一篇公众号文章"
  → 抓热点 → 选题评分 → 框架选择 → 素材采集 → 内容增强
  → 写作（真实信息锚定 + 风格注入 + 编辑锚点）
  → SEO优化 → AI配图 → 微信排版 → 推送草稿箱
```

首次使用时会引导你设置公众号风格，之后每次只需一句话。生成的文章带有 2-3 个编辑锚点——花 3-5 分钟加入你自己的话，文章就会从"AI 初稿"变成"你的作品"。

管道的每一段都是独立 skill，one step at a time：

| 你说 | 激活 | 产出 |
|------|------|------|
| 今天写什么 / 找几个选题 | `wewrite-topic` | 10 个评分排序的选题 |
| 就这个选题写一篇 | `wewrite-write` | 反 AI 初稿 + 编辑锚点 |
| 检查一下 / 有没有 AI 味 | `wewrite-review` | 生成档案 + 逐句改进建议 |
| 给这篇配个封面 | `wewrite-visual` | 封面 + 内文配图 .png |
| 推到草稿箱 / 换个主题 | `wewrite-publish` | 微信草稿 / 本地 HTML |
| 改写成小红书 / 抖音版 | `wewrite-rewrite` | 过原创度+反AI双门的平台版本 |
| 学习我的修改 / 导入范文 | `wewrite-learn` | playbook 规则 / 风格库 |
| 看看文章数据 | `wewrite-stats` | 阅读数据回填 + 选题建议 |
| 重新设置风格 | `wewrite-style` | style.yaml |

模块单独激活时缺什么前置会自己补（或向你要），状态经 `~/.wewrite/output/_state.yaml` 在模块间传递——上午选完题，下午在新会话里说"就写这个"也能接上。

## 架构：三层解耦

设计原则一句话：**prompt 负责判断，Python 负责确定性**。

| 层 | 位置 | 内容 |
|----|------|------|
| Prompt | `skills/`（10 个自包含 skill） | 选题好不好、像不像人写的、哪里要改——方法论与判断，每个 skill 自带 references/ |
| Runtime | `wewrite` CLI（pip 包） | 打分、转 HTML、调微信 API、生图、成本路由——确定性操作 |
| State | `~/.wewrite/`（`WEWRITE_HOME` 可覆盖） | 凭证、风格、历史、学习产物、输出文件——全部在仓库外 |

skill 目录复制到哪都能用；CLI 与 skill 独立安装升级；换机器只需带走 `~/.wewrite/`。

## 安装

**Claude Code / Agent-Skills 宿主**（推荐，一条命令装全套）：

```bash
git clone --depth 1 https://github.com/oaker-io/wewrite.git ~/wewrite
cd ~/wewrite && bash install.sh
```

`install.sh` 做三件事：装 `wewrite` CLI（uv/pipx，无则回退 venv）、把 10 个 skill 符号链接到 `~/.claude/skills/` 与 `~/.agents/skills/`、把旧版留在仓库里的用户状态迁到 `~/.wewrite/`。仓库可以克隆到任意位置。

**skills.sh**（按需挑模块）：

```bash
npx skills add oaker-io/wewrite
```

skill 目录自包含、复制即用；`wewrite` CLI 需另装一条：`uv tool install git+https://github.com/oaker-io/wewrite.git`。

**OpenClaw**（单 SKILL.md 形态，用构建好的 `dist/openclaw/`）：

```bash
git clone --depth 1 https://github.com/oaker-io/wewrite.git ~/wewrite
ln -sfn ~/wewrite/dist/openclaw ~/.openclaw/skills/wewrite
bash ~/.openclaw/skills/wewrite/install.sh
```

**Codex**（OpenAI Codex CLI，经自定义 prompt 承载）：

```bash
git clone --depth 1 https://github.com/oaker-io/wewrite.git ~/wewrite
cd ~/wewrite && bash install.sh
python3 scripts/build_codex.py --install   # 装 /wewrite prompt 到 ~/.codex/prompts/
```

之后在 Codex 里 `/wewrite 写一篇关于 X 的文章`。源 `skills/` 更新后重跑 `build_codex.py --install` 同步。详见 [`dist/codex/README.md`](dist/codex/README.md)。

> OpenClaw / Codex 均为单文件形态：构建脚本把 `skills/` 下的模块按管道顺序合并回一份单体 SKILL.md / prompt，使用体验与模块化版一致。

### 配置（可选）

```bash
cp config.example.yaml ~/.wewrite/config.yaml
```

填入微信公众号 `appid`/`secret`（推送需要）和图片 API key（生图需要）。不配也能用——自动降级为本地 HTML + 输出图片提示词。配了 `WEWRITE_WRITER_API_KEY` 则正文写作路由给便宜的写作模型（DeepSeek，约 $0.04/篇）。

## 快速开始

```
你：写一篇公众号文章                → 全流程（默认全自动）
你：写一篇关于 AI Agent 的公众号文章
你：交互模式，写一篇关于效率工具的推文  → 在选题/框架/配图处暂停确认
你：今天写什么                      → 只要选题（wewrite-topic）
你：检查一下                        → 生成档案 + 质量自检（wewrite-review）
你：改写成小红书                    → 多平台改写（wewrite-rewrite）
你：学习我的修改                    → 飞轮学习（wewrite-learn）
你：导入范文 / 查看范文库           → 风格库（wewrite-learn）
你：看看有什么主题 / 换成 sspai 主题 → 主题画廊 / 重排版（wewrite-publish）
你：做一个小绿书                    → 图片帖（wewrite-publish）
你：看看文章数据怎么样              → 效果复盘（wewrite-stats）
你：学习排版 + 文章链接             → 提取排版主题（wewrite-learn）
你：更新                            → 升级到最新版
```

## 核心能力

| 能力 | 说明 | 所在 |
|------|------|------|
| 热点抓取 | 微博 + 头条 + 百度实时热搜 | `wewrite hotspots` |
| SEO 评分 | 百度 + 360 搜索量化评分 | `wewrite seo` |
| 选题生成 | 10 选题 × 3 维度评分 + 历史去重 | wewrite-topic |
| 素材采集 | WebSearch 真实数据/引述/案例，禁止编造 | wewrite-write |
| 框架生成 | 7 套写作骨架（痛点/故事/清单/对比/热点解读/纯观点/复盘） | wewrite-write |
| 内容增强 | 按框架类型自动匹配：角度发现/密度强化/细节锚定/真实体感 | wewrite-write |
| 反 AI 写作 | 写作契约（句长交替/情绪起伏/口语修正）+ 维度随机化 + 分段实时自检 | wewrite-write |
| 反 AI 评分 | 11 项统计检测，0-1 连续分 | `wewrite score` |
| SEO 优化 | 标题策略 / 摘要 / 关键词 / 标签 | wewrite-review |
| 视觉 AI | 封面 3 创意 + 内文 3-6 配图，风格锚定全文一致 | `wewrite image-gen` |
| 排版发布 | 16+ 主题 + 微信兼容修复 + 暗黑模式 | `wewrite preview/publish` |
| 多平台改写 | 一稿 → 小红书/抖音，内容级真改 + 原创度门 | wewrite-rewrite |
| 效果复盘 | 微信数据分析 API 回填阅读数据，反哺选题 | `wewrite stats` |
| 范文风格库 | SICO 式 few-shot：从你的文章提取风格指纹，写作时注入 | `wewrite exemplar` |
| 风格飞轮 | 学习你的修改，越用越像你 | `wewrite learn-edits` |
| 排版学习 | 从任意公众号文章 URL 提取排版主题 | `wewrite learn-theme` |
| 文章采集 | 从公众号 URL 提取正文为 Markdown，可导入范文库 | `wewrite fetch-article` |

## 写作人格

像选排版主题一样选写作风格。在 `~/.wewrite/style.yaml` 里一行配置：

```yaml
writing_persona: "midnight-friend"
```

| 人格 | 适合 | 风格特点 |
|------|------|---------|
| `midnight-friend` | 个人号/自媒体 | 极度口语化、高自我怀疑、每段第一人称 |
| `warm-editor` | 生活/文化/情感 | 温暖叙事、故事嵌套数据、柔和情绪弧 |
| `industry-observer` | 行业媒体/分析 | 中性分析、数据先行、稳中带刺 |
| `sharp-journalist` | 新闻/评论 | 犀利简洁、数据驱动、强观点 |
| `cold-analyst` | 财经/投研 | 冷静克制、逻辑链条、风险意识强 |
| `humor-storyteller` | 泛科技娱乐/热点辣评 | 包袱密集、荒诞解构、笑完有余味 |
| `tech-coder` | 技术教程/开发者社区 | 代码先行、注释式行文、版本敏感 |

每个人格定义了语气浓度、数据呈现方式、情绪弧线、不确定性表达模板等参数。详见 `skills/wewrite-write/personas/`；自定义人格放 `~/.wewrite/personas/`。

## 内容质量

WeWrite 的目标不是"骗过 AI 检测"，而是**写出值得读的文章**。核心机制：

1. **内容增强**：根据框架类型自动执行不同策略——热点文找反直觉角度、干货文强化信息密度、故事文锚定真实细节、对比文注入真实用户体感
2. **素材采集**：自动 WebSearch 真实数据/引述/案例，锚定在文章中（不编造）
3. **范文风格库**：导入你已发布的文章，写作时自动注入你的风格指纹（句长节奏、情绪表达、转折方式）
4. **编辑锚点**：在 2-3 个关键位置标记"在这里加一句你自己的话"
5. **学习飞轮**：每次你编辑后说"学习我的修改"，下次初稿更接近你的风格
6. **文章自检**：说"检查一下"，查看生成档案（用了什么框架/人格/策略）+ 质量检查（具体到哪句话该怎么改）

## 排版引擎

### 16 个主题

```bash
wewrite gallery    # 浏览器内预览所有主题（并排对比 + 一键复制）
wewrite themes     # 列出主题名称
```

| 类别 | 主题 |
|------|------|
| 通用 | `professional-clean`（默认）、`minimal`、`newspaper` |
| 科技 | `tech-modern`、`bytedance`、`github` |
| 文艺 | `warm-editorial`、`sspai`、`ink`、`elegant-rose` |
| 商务 | `bold-navy`、`minimal-gold`、`bold-green` |
| 风格 | `bauhaus`、`focus-red`、`midnight` |

所有主题均支持微信暗黑模式。`wewrite learn-theme <url>` 学到的新主题存在 `~/.wewrite/themes/`，加载时优先于内置主题。

### 微信兼容性自动修复

| 问题 | 自动修复 |
|------|---------|
| 外链被屏蔽 | 转为上标编号脚注 + 文末参考链接 |
| 中英混排无间距 | CJK-Latin 自动加空格 |
| 加粗标点渲染异常 | 标点移到 `</strong>` 外 |
| 原生列表不稳定 | `<ul>/<ol>` 转样式化 `<section>` |
| 暗黑模式颜色反转 | 注入 `data-darkmode-*` 属性 |
| `<style>` 被剥离 | 所有 CSS 内联注入 |

### 容器语法

````markdown
:::dialogue
你好，请问这个功能怎么用？
> 很简单，直接在 Markdown 里写就行。
:::

:::timeline
**2024 Q1** 立项启动
**2024 Q3** MVP 上线
:::

:::callout tip
提示框，支持 tip / warning / info / danger。
:::

:::quote
好的排版不是让读者注意到设计，而是让读者忘记设计。
:::
````

## CLI 独立使用

`wewrite` CLI 不依赖任何 Agent，可以单独当排版/发布/评分工具用：

```bash
wewrite preview article.md --theme sspai            # Markdown → 微信 HTML 预览
wewrite publish article.md --cover cover.png --title "标题"   # 推送草稿箱
wewrite image-post p1.jpg p2.jpg -t "周末探店"       # 小绿书/图片帖（横滑轮播）
wewrite score article.md --verbose                  # 反 AI 评分（11 项检测）
wewrite hotspots --limit 20                         # 抓热点
wewrite seo --json "AI大模型" "科技股"               # SEO 分析
wewrite exemplar article.md / --list                # 范文风格库
wewrite fetch-article <url> -o out.md               # 公众号文章 → Markdown
wewrite learn-theme <url> --name my-style           # 学排版主题
wewrite diagnose                                    # 环境 + 配置自检
wewrite home                                        # 查看状态目录
wewrite migrate --from <旧仓库路径>                  # 从 v2.1 及更早版本迁移状态
```

## 目录结构

```
wewrite/
├── skills/                   # Prompt 层：10 个自包含 skill（复制即用）
│   ├── wewrite/                # 主入口：路由 + 全流程编排（Step 1/8 内联，Step 2-7 调模块）
│   ├── wewrite-style/          # 风格设置 / Onboard（onboard.md、style-template.md、style.example.yaml）
│   ├── wewrite-topic/          # 选题（topic-selection.md）
│   ├── wewrite-write/          # 框架 + 素材 + 反 AI 写作（writing-guide、frameworks、personas/ 7 人格…）
│   ├── wewrite-review/         # SEO + 编辑自评 + 反 AI 评分 + 自检报告（seo-rules.md）
│   ├── wewrite-visual/         # 封面 + 内文配图（visual-prompts.md、cover-prompts.md）
│   ├── wewrite-publish/        # 排版 + 发布 + 主题画廊 + 小绿书（wechat-constraints.md）
│   ├── wewrite-learn/          # 学习修改 / 导入范文 / 学排版（learn-edits.md）
│   ├── wewrite-stats/          # 文章数据复盘（effect-review.md）
│   └── wewrite-rewrite/        # 一源多平台改写（multiplatform-rewrite.md + platforms/ 平台定义）
│
├── src/wewrite/              # Runtime 层：`wewrite` CLI（pip 包）
│   ├── cli.py                  # 子命令调度器
│   ├── paths.py                # 状态目录解析（$WEWRITE_HOME → ~/.wewrite）
│   ├── migrate.py              # 旧状态一次性迁移
│   ├── commands/               # diagnose / score / hotspots / seo / stats / learn-* / exemplar / fetch-article / llm-write / similarity / build-playbook
│   └── toolkit/                # converter / theme / publisher / wechat_api / image_gen + 16 个内置主题
│
├── dist/openclaw/            # OpenClaw 兼容版（CI 自动构建，模块合并回单体 SKILL.md）
├── dist/codex/               # Codex 自定义 prompt（同源合并）
│
├── pyproject.toml            # CLI 打包定义
├── config.example.yaml       # API 配置模板
├── writing-config.example.yaml # 写作参数模板
├── scripts/                  # 仅开发构建工具（build_openclaw / build_codex / context_budget）
└── tests/                    # converter + context_budget 测试
```

State 层（全部在 `~/.wewrite/`，不在仓库）：`config.yaml`、`style.yaml`、`history.yaml`、`playbook.md`、`writing-config.yaml`、`exemplars/`、`corpus/`、`lessons/`、`output/`、`themes/`。

## 工作流程

```
Step 1  环境检查 + 加载风格（不存在则 Onboard）        ← 主入口 wewrite
  ↓
Step 2  热点抓取 → 历史去重 + SEO → 选题              ← wewrite-topic
  ↓
Step 3  框架选择 → 素材采集（WebSearch 真实数据）      ┐
  ↓                                                    ├ wewrite-write
Step 4  维度随机化 → 范文注入 → 写作 → 快速自检        ┘
  ↓
Step 5  SEO 优化 → 质量验证                            ← wewrite-review
  ↓
Step 6  视觉 AI（封面 + 内文配图）                     ← wewrite-visual
  ↓
Step 7  预检 + 排版 + 发布（16 主题 + 微信兼容修复）   ← wewrite-publish
  ↓
Step 8  写入历史 → 回复用户（含编辑建议 + 飞轮提示）   ← 主入口 wewrite
```

默认全自动，主入口按序编排各模块，状态经 `~/.wewrite/output/_state.yaml` 传递（契约见 `skills/wewrite/references/pipeline-state.md`）。说"交互模式"可在选题/框架/配图处暂停确认。

## 升级

对 Agent 说「更新」，或手动：

```bash
cd <仓库路径> && git pull && bash install.sh
```

skill 每次运行会自动比对版本并提示。从 v2.1 及更早版本升级时，install.sh 会自动把仓库里的旧用户状态迁到 `~/.wewrite/`。

## License

MIT
