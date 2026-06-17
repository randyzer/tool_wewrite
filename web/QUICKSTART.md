# 本地运行 WeWrite Web

在你自己的机器上跑前后端。`localhost` 即本机，密钥留在本地，无需外发。

## 前置
- Python 3.11+
- Node 18+（建议 20/22）
- 一个 Anthropic API Key（真正生成文章需要；只看 UI 可不填）
- `claude` CLI 已安装并在 PATH 中 —— Claude Agent SDK 靠它驱动
  （安装：`npm i -g @anthropic-ai/claude-code`，或见官方文档）

## 拉代码
```bash
git fetch origin claude/skill-web-tool-l066oz
git checkout claude/skill-web-tool-l066oz
```

## 后端（终端 1）
```bash
cd web/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r ../../requirements.txt   # toolkit 依赖（agent 通过 Bash 调用）

cp .env.example .env
# 编辑 .env：
#   ANTHROPIC_API_KEY=sk-ant-...            （必填，才能生成）
#   APP_SECRET_KEY=<下面命令生成>           （加密微信/小红书凭证用）
#   WEWRITE_IMAGE_PROVIDER=doubao           （可选，要 AI 配图才填）
#   WEWRITE_IMAGE_API_KEY=...               （可选）
#   XHS_MCP_URL=http://localhost:18060/mcp  （可选，小红书真机发布才填）
#
# 生成 APP_SECRET_KEY：
#   .venv/bin/python -c "from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())"

.venv/bin/uvicorn app.main:app --reload --port 8000
# 验证： curl http://localhost:8000/api/health
```

> skill 的 `python3` 会优先用 `{repo}/.venv/bin/python3`（若存在）。最省事的做法是在**仓库根**建一个含 toolkit 依赖的 venv，或把根 `.venv` 软链到后端 venv：
> `ln -sfn "$PWD/web/backend/.venv" "$PWD/.venv"`（在仓库根执行）。
> 不做也行 —— 那样 agent 用系统 `python3`，需系统装好根 `requirements.txt`。

### 线上部署：LLM 走 relay（真 Claude）

本地开发把 `ANTHROPIC_*` 三项都留空即可，用本机登录的 `claude` 凭证。**线上服务器**没有登录态，改走 relay，在服务器 `.env` 填：

```bash
ANTHROPIC_BASE_URL=https://relay.upthos.com   # relay 根，CLI 自动补 /v1/messages
ANTHROPIC_AUTH_TOKEN=<有 Claude 权限的 relay key>   # 走 Authorization: Bearer
WEWRITE_MODEL=claude-sonnet-4-6                # 管道 100+ 轮，Sonnet 比 Opus 快近半
# ANTHROPIC_API_KEY 留空（与上面二选一，别同时设）
```

⚠️ relay 必须真正映射到 **Anthropic Claude**：用下面这条自检，响应 `model` 以 `claude` 开头才算通；若是 `gpt-*` 说明 relay 把 claude-* id 偷偷路由到了 GPT，SDK（Claude 专用）不可用。

```bash
curl -s https://relay.upthos.com/v1/messages \
  -H "Content-Type: application/json" -H "anthropic-version: 2023-06-01" \
  -H "Authorization: Bearer $ANTHROPIC_AUTH_TOKEN" \
  -d '{"model":"claude-sonnet-4-6","max_tokens":16,"messages":[{"role":"user","content":"ping"}]}' \
  | python3 -c "import sys,json;m=json.load(sys.stdin).get('model','');print('OK',m) if m.startswith('claude') else print('FAIL',m)"
```

## 前端（终端 2）
```bash
cd web/frontend
npm install
cp .env.example .env.local   # 默认 NEXT_PUBLIC_API_BASE=http://localhost:8000
npm run dev                  # http://localhost:3000
```

## 测试动线
1. 打开 http://localhost:3000
2. **设置页**：填公众号风格；如要推草稿箱，绑定微信 appid/secret（加密存储）
3. 首页输入「写一篇关于 X 的公众号文章」→ 开始生成 → 看实时进度 → 预览/Markdown/配图
4. 成稿卡片下「发布到平台」：微信走管道；小红书需先扫码登录（要先起 xiaohongshu-mcp）

## 小红书真机发布（可选）
另起 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)（Docker 一条命令），
把它的 MCP 端点填进后端 `.env` 的 `XHS_MCP_URL`，重启后端。发布面板里小红书即可扫码登录、发布。

## 常见问题
- **点生成报 error**：多半是 `ANTHROPIC_API_KEY` 没配，或 `claude` CLI 不在 PATH。看后端终端日志。
- **没有配图**：没配图片 provider → 管道走 `skip_image_gen` 降级（无图）；小红书因「至少 1 张图」会发布失败，属预期。
- **小红书显示「未配置」**：`XHS_MCP_URL` 没填或 xiaohongshu-mcp 没起。
- **CORS 报错**：确认后端 `.env` 的 `WEWRITE_CORS_ORIGINS` 含你的前端地址（默认含 `http://localhost:3000`）。
