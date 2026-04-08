# PRODUCT_WORKBENCH_GUIDE

## 工作台定位

它不是底层 provider demo，而是一个可操作的“内容助手前台”。

## 首页应该看到什么

- 一键跑完整链路
- staged run 创建入口
- 最近 runs
- 8 阶段状态卡片
- Draft queue
- publish preview / send
- sync_crawled / sync_generated
- provider health + login checks

## 适合验收的操作路径

1. 创建 full run
2. 查看 run 详情和阶段 diagnostics
3. 审核草稿
4. 发布预览 / dry-run send
5. 触发 crawled/generated 同步
6. 查看 audit / publish job / sync record

## 为什么适合作品集展示

- 功能链路完整
- 界面可讲故事
- 工程结构没有塌成 demo
- 有治理（schema、diagnostics、safety gate、provider registry）
