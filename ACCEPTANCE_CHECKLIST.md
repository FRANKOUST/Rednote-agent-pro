# ACCEPTANCE_CHECKLIST

- [x] 已有统一内容流水线服务，显式支持 8 个阶段
- [x] 支持一键完整链路与逐步执行两种模式
- [x] crawl 已引入“两阶段采集 + 登录态复用 + 过滤”思路
- [x] SourcePost / run / audit / diagnostics / provider health 已接入
- [x] Analysis / Topic / Draft schema 已升级为运营视角
- [x] prompt 模板已版本化并带 schema 约束
- [x] publish 已拆为 prepare / preview / send
- [x] sync 已拆为 sync_crawled / sync_generated
- [x] MCP 已提供高阶运营动作工具
- [x] Web Console 已升级为内容助手工作台
- [x] 测试通过
- [x] README / DEMO / SHOWCASE / RUNBOOK / DESIGN / TEMPLATE / WORKBENCH 文档已更新
- [ ] 真实 XHS 登录态验证（外部 blocker）
- [ ] 真实 model provider 验证（外部 blocker）
- [ ] 真实 publish 权限验证（外部 blocker）
- [ ] 真实 Feishu sync 验证（外部 blocker）
