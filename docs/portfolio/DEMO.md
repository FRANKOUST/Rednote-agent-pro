# Demo Script

## Goal

在 5 分钟内演示平台的完整主链路和工程设计质量。

## Script

1. 打开首页，介绍这是单团队内部使用的内容平台
2. 输入 `咖啡,护肤` 并启动 pipeline
3. 展示生成出的 drafts
4. 审核通过其中一个 draft
5. 触发 publish
6. 打开 `/api/publish-jobs` 展示发布记录
7. 打开 `/api/audit-logs` 展示审计记录
8. 打开 `/mcp` 的 `tools/list` / `tools/call` 示例，说明 AI agent 也可以走同一业务层
9. 展示 OpenSpec change 目录和设计文档，说明该项目具备规范化演进能力

## Talking Points

- 这个项目不是单一脚本，而是平台雏形
- 当前主链路已经能在 mock 模式下完整跑通
- 所有外部能力都已经 provider 化
- 下一步只需要替换 provider，而不是推翻业务层
