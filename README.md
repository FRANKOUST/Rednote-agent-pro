# Xiaohongshu Content Workbench

一个围绕 **小红书内容采集 → 分析 → 选题 → 起稿 → 配图 → 审核 → 发布预览 → 同步** 的统一内容助手工作台。

它不是单纯的爬虫 demo，也不是只会生成文案的玩具项目，而是一个保留工程骨架的产品化内容流水线：

- **统一业务层**：REST / MCP / Web 共用同一套服务
- **8 阶段流水线**：`crawl -> analyze -> topic -> draft -> image -> review -> publish -> sync`
- **provider registry**：collector / model / image / publish / sync 全部可替换
- **安全默认值**：默认人工审核、默认 dry-run、默认保留 publish safety gate
- **可复盘**：run、stage diagnostics、audit、publish、sync 全量留痕

---

## 1. 现在这个项目能做什么

### 内容流水线能力

一次完整 run 会按以下顺序推进：

1. **crawl**：抓取候选内容并入库为 `SourcePost`
2. **analyze**：输出运营视角分析报告
3. **topic**：从分析结果生成选题池
4. **draft**：生成可审核草稿
5. **image**：生成图片规划 / 图片资产
6. **review**：进入人工审核位
7. **publish**：准备发布、预览发布、发送发布
8. **sync**：同步采集侧和生成侧结果

### 当前入口

- **Web Console**：最适合日常操作和演示
- **REST API**：最适合集成和自动化
- **MCP tools**：最适合 Agent / Assistant 调用

---

## 2. 快速开始

### 2.1 安装依赖

```bash
pip install -e .[dev]
```

### 2.2 运行测试

```bash
pytest -q
```

### 2.3 启动服务

```bash
uvicorn app.main:app --reload
```

默认启动后可访问：

- Web 工作台：`http://127.0.0.1:8000/`
- REST API：`http://127.0.0.1:8000/api/...`
- MCP Endpoint：`http://127.0.0.1:8000/mcp`

---

## 3. 最推荐的使用方式：先从 Web 工作台开始

打开 `/` 后，你会看到“**内容助手工作台**”。

首页重点区域：

- **一键跑完整链路**：直接创建 full run
- **逐步执行**：先建一个 staged run，再一阶段一阶段推进
- **最近 Runs**：查看最近 run 状态
- **8 阶段状态卡片**：看 crawl / analyze / topic / draft / image / review / publish / sync 当前到了哪一步
- **Draft Queue**：审核草稿、做发布预览、执行 dry-run 发布
- **Sync Actions**：同步 crawled/generated 数据
- **Provider Health / Login Checks**：检查 collector/publisher 是否具备登录态和健康状态

### 一个最简单的演示流程

1. 打开 `/`
2. 输入关键词，比如：`咖啡,护肤`
3. 点击 **Run full pipeline**
4. 打开最新 run
5. 查看 stage diagnostics
6. 对 draft 执行 approve
7. 执行 publish preview
8. 执行 publish send（默认 dry-run）
9. 执行 sync_crawled / sync_generated

---

## 4. 怎么抓取小红书页面

这部分是最重要的使用说明。

### 4.1 当前仓库默认怎么抓

默认是 **安全演示模式**：

- 以 fixture / safe fallback 为主
- 可以完整演示“两阶段采集”的业务语义
- 不要求你立刻提供真实小红书登录态
- 非常适合本地开发、UI 验收、流程联调

也就是说：

- **你现在就可以跑通“抓取 → 分析 → 选题 → 草稿 → 发布预览 → 同步”全链路**
- 但默认抓取结果来自 fixture / safe provider，而不是你自己的真实小红书账号会话

### 4.2 项目里的抓取语义是什么

当前 collector provider 已经采用了“小红书内容采集常见的产品化结构”：

#### 阶段 1：候选收集

先从搜索页收集候选项：

- 关键词
- 候选 URL
- 作者
- 发布时间
- 内容类型

#### 阶段 2：详情补全

再对候选 URL 做详情补全，提取更可信字段：

- 标题
- 正文
- 标签
- 发布时间
- 点赞 / 评论 / 收藏
- URL

#### 最后过滤

只保留符合条件的图文内容：

- 正文不能为空
- 跳过广告词
- 跳过非图文 / 视频内容
- 近一年过滤
- 点赞 / 收藏 / 评论阈值过滤
- `topic_words` 相关性过滤

### 4.3 如果你只想本地演示抓取

直接使用默认设置即可。

示例：

```bash
uvicorn app.main:app --reload
```

然后在 Web 首页输入关键词执行 run，或者走 REST：

```bash
curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["咖啡"],
    "topic_words": ["咖啡", "手冲"],
    "run_mode": "full",
    "dry_run": true
  }'
```

### 4.4 如果你想准备“真实小红书页面抓取”

当前仓库已经预留了**登录态复用**相关配置，重点是：

- **优先 storage_state**
- **cookies 作为备用**

相关配置：

- `XHS_SCRAPLING_STORAGE_STATE_PATH`
- `XHS_SCRAPLING_COOKIES_PATH`
- `XHS_PLAYWRIGHT_STORAGE_STATE_PATH`

典型思路：

1. 先在本地浏览器里完成一次真实登录
2. 把登录态保存为 `storage_state.json`
3. 放到项目可访问路径
4. 再切换到对应 collector 配置做验证

示例环境变量：

```bash
set XHS_ENABLE_REAL_COLLECTOR=true
set XHS_SCRAPLING_MODE=live
set XHS_SCRAPLING_STORAGE_STATE_PATH=./data/scrapling/storage_state.json
set XHS_SCRAPLING_COOKIES_PATH=./data/scrapling/cookies.json
```

或：

```bash
set XHS_ENABLE_REAL_COLLECTOR=true
set XHS_DEFAULT_COLLECTOR_PROVIDER=playwright
set XHS_PLAYWRIGHT_STORAGE_STATE_PATH=./data/playwright/state.json
```

### 4.5 这里要明确说明一个现实情况

**当前仓库已经把“真实抓取所需的产品语义、登录态复用入口、过滤逻辑、诊断能力”都接好了，但真正的 live 小红书抓取仍然需要你自己的真实环境来完成最终验证。**

也就是说，仓库现在处于：

- **代码、接口、测试、工作台：已就绪**
- **真实抓取成功与否：取决于你的 storage state / cookies / 本地环境 / 目标页面变化**

所以正确使用姿势是：

1. 先用默认 fixture 模式把流程跑通
2. 再提供真实登录态做 live 验证
3. 如果 live 页面结构有变化，再按 diagnostics 微调 provider

---

## 5. REST API 怎么用

### 5.1 创建完整 run

```bash
curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["护肤"],
    "topic_words": ["护肤", "敏感肌"],
    "min_likes": 100,
    "min_favorites": 20,
    "min_comments": 5,
    "run_mode": "full",
    "dry_run": true
  }'
```

### 5.2 创建 staged run

```bash
curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["家装"],
    "topic_words": ["家装"],
    "run_mode": "step",
    "dry_run": true
  }'
```

### 5.3 运行某个 stage

```bash
curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs/<run_id>/stages/crawl
curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs/<run_id>/stages/analyze
curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs/<run_id>/stages/topic
curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs/<run_id>/stages/draft
curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs/<run_id>/stages/image
curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs/<run_id>/stages/review
```

### 5.4 查看 run 与 diagnostics

```bash
curl http://127.0.0.1:8000/api/content-pipeline/runs/<run_id>
curl http://127.0.0.1:8000/api/content-pipeline/runs/<run_id>/diagnostics
```

### 5.5 审核与发布

```bash
curl -X POST http://127.0.0.1:8000/api/content-drafts/<draft_id>/review/approve \
  -H "Content-Type: application/json" \
  -d '{"review_notes":"可以进入发布准备"}'

curl -X POST http://127.0.0.1:8000/api/content-drafts/<draft_id>/publish/prepare
curl -X POST http://127.0.0.1:8000/api/content-drafts/<draft_id>/publish/preview

curl -X POST http://127.0.0.1:8000/api/content-drafts/<draft_id>/publish/send \
  -H "Content-Type: application/json" \
  -d '{"dry_run":true}'
```

### 5.6 同步

```bash
curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs/<run_id>/sync/crawled \
  -H "Content-Type: application/json" \
  -d '{"dry_run":true}'

curl -X POST http://127.0.0.1:8000/api/content-pipeline/runs/<run_id>/sync/generated \
  -H "Content-Type: application/json" \
  -d '{"dry_run":true}'
```

---

## 6. MCP 怎么用

MCP endpoint：

- `POST /mcp`

当前高阶工具包括：

- `run_content_pipeline`
- `run_pipeline_stage`
- `crawl_and_analyze`
- `generate_topics_from_run`
- `generate_draft_from_topic`
- `prepare_publish`
- `preview_publish`
- `send_publish`
- `sync_crawled_data`
- `sync_generated_data`
- `check_collector_login`
- `check_publish_login`
- `check_provider_health`

最常用的是：

- 先 `tools/list`
- 再 `tools/call`

例如让 Agent 直接跑内容流水线：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "run_content_pipeline",
    "arguments": {
      "keywords": ["咖啡"],
      "topic_words": ["咖啡", "手冲"],
      "run_mode": "full",
      "dry_run": true
    }
  }
}
```

---

## 7. 配置项重点看哪些

最常用环境变量：

### Collector

- `XHS_DEFAULT_COLLECTOR_PROVIDER`
- `XHS_ENABLE_REAL_COLLECTOR`
- `XHS_SCRAPLING_MODE`
- `XHS_SCRAPLING_STORAGE_STATE_PATH`
- `XHS_SCRAPLING_COOKIES_PATH`
- `XHS_PLAYWRIGHT_STORAGE_STATE_PATH`

### Model

- `XHS_DEFAULT_MODEL_PROVIDER`
- `XHS_ENABLE_REAL_MODEL_PROVIDER`
- `XHS_MODEL_API_KEY`
- `XHS_MODEL_BASE_URL`
- `XHS_MODEL_NAME`

### Publish

- `XHS_DEFAULT_PUBLISH_PROVIDER`
- `XHS_ENABLE_REAL_PUBLISH_PROVIDER`
- `XHS_ALLOW_LIVE_PUBLISH`
- `XHS_XHS_PUBLISH_API_BASE`
- `XHS_XHS_PUBLISH_API_TOKEN`

### Sync

- `XHS_DEFAULT_SYNC_PROVIDER`
- `XHS_FEISHU_CLI_DRY_RUN`
- `XHS_FEISHU_SYNC_MODE`
- `XHS_FEISHU_BASE_TOKEN`
- `XHS_FEISHU_TABLE_ID`

---

## 8. 发布与同步是怎么设计的

### 发布

项目不会默认直接“真实自动发帖”。

而是拆成三步：

1. `prepare`
2. `preview`
3. `send`

这样做的好处：

- Web / REST / MCP 都能先看预览
- 审核位更清晰
- 默认不会绕过 safety gate

### 同步

同步也不是一个模糊动作，而是两种业务语义：

- `sync_crawled`：同步采集内容、分析摘要、候选源数据
- `sync_generated`：同步选题、草稿、审核结果、发布结果

---

## 9. 如何排查问题

优先看这几个入口：

- `/console/providers`
- `/console/runs/<run_id>/diagnostics`
- `/api/providers/status`
- `/api/audit-logs`
- `/api/sync-records`

如果你在做真实抓取验证，先检查：

1. storage_state / cookies 是否存在
2. provider health 是否 ready / degraded
3. collector login check 是否通过
4. run diagnostics 在 crawl 阶段报的具体错误是什么

---

## 10. 当前真实 blocker

仓库已经完成到“只差真实外部验证”的状态。

仍需你提供：

- 真实 XHS 登录态（storage state / cookies）
- 至少一个真实 OpenAI-compatible 模型端点
- 真实发布权限（browser state 或 API token）
- 真实 Feishu `lark-cli` 登录态和目标权限

没有这些输入时：

- **开发、演示、验收、前台操作、接口联调都可以继续做**
- **但真实对外平台联调不能宣称已完成**

---

## 11. 当前验证状态

```bash
pytest -q
```

当前仓库测试结果：

- `56 passed`

---

## 12. 相关文档

- `DEMO.md`
- `SHOWCASE.md`
- `REAL_OPS_READINESS.md`
- `OPERATOR_RUNBOOK.md`
- `PROVIDER_INTEGRATION_MATRIX.md`
- `ACCEPTANCE_CHECKLIST.md`
- `CONTENT_PIPELINE_DESIGN.md`
- `PROMPT_TEMPLATE_STRATEGY.md`
- `PRODUCT_WORKBENCH_GUIDE.md`
