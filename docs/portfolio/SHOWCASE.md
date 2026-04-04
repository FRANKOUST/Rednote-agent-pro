# Portfolio Showcase

## Project

Xiaohongshu Content Platform

## Positioning

一个适合放入作品集的“AI 内容生产平台”项目，展示了如何把内容采集、分析、生成、审核、发布、同步整合为统一的可扩展系统，而不是停留在单点脚本或 demo API。

## What This Demonstrates

- 平台化架构能力
- 领域建模和状态机设计能力
- Provider 抽象与替换能力
- 人工审核与自动化发布并存的工作流设计
- REST / MCP / Web 三种入口复用同一业务层
- 从 inline 调度到 external worker adapter 的可演进后台任务设计
- 文档驱动与规范驱动开发能力
- 从需求拆解到可运行交付的闭环能力

## Demo Narrative

1. 用户输入关键词
2. 系统执行采集阶段并产出 source posts
3. 系统分析爆款模式并生成选题
4. 系统生成 drafts 与配图
5. 操作员在 Web Console 批准内容
6. 系统执行 publish 并写入 publish job
7. 系统创建 sync record 与审计日志

## Portfolio Angles

- `Architecture`: 模块化单体 + provider 插件层 + 异步任务编排
- `Product thinking`: 默认人工审核，自动发布可配置开关
- `Operational safety`: 发布记录、同步记录、审计记录齐全
- `Extensibility`: mock provider 和真实 provider 的替换边界清晰

## Current Limitations

- 实际小红书抓取仍为 mock provider
- 实际 OpenAI/Feishu/发布通道仍未接通
- MCP 为 phase-one 的轻量 JSON-RPC tool surface，而非完整生产级兼容实现

## Why It Is Still Valuable

这个版本已经体现了完整系统设计与工程落地能力，且具备明确的真实集成扩展路径，非常适合作为“平台型 AI 工程项目”的展示样本。
