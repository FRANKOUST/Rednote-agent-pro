# DEMO

## 演示目标

展示这个仓库已经从“工程骨架”升级为“可展示、可操作、可验收”的内容助手工作台。

## 推荐演示路径

1. 打开 `/`，展示“内容助手工作台”首页
2. 运行一次 `full` pipeline
3. 进入 run 详情，展示 8 个阶段与 diagnostics
4. 打开 Source Posts / Analysis / Topics / Drafts / Images
5. 对草稿执行 approve
6. 执行 publish preview，再执行 publish send（dry-run）
7. 执行 `sync_crawled` 与 `sync_generated`
8. 打开 `/console/providers` 展示 provider health 与 login checks
9. 调用 `/mcp` 的 `tools/list` 与 `run_content_pipeline`

## 预期观感

- 前台像“内容助手操作台”而不是原始工具集合
- run 有阶段状态、摘要、产物、错误、provider
- 发布与同步使用运营动作语义
- 即便没有真实外部权限，也可以完整演示 dry-run 产品链路
