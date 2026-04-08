# PROMPT_TEMPLATE_STRATEGY

## 设计原则

- schema-first
- provider-agnostic
- 集中管理
- 可版本化
- 可被测试直接验证

## 当前模板

| Stage | template_id | version | Output Schema |
|---|---|---:|---|
| analyze | `analyze` | `v2.0` | `AnalysisResultSchema` |
| topic | `topic` | `v2.0` | `TopicSuggestionListSchema` |
| draft | `draft` | `v2.0` | `DraftResultSchema` |
| image | `image` | `v2.0` | `ImagePlanSchema` |

## 每个模板都包含

- `template_id`
- `version`
- `stage`
- `input_fields`
- `output_schema`
- `purpose`
- `system_prompt`
- `user_instruction`

## 运行时约束

- provider 先取模板，再构造请求
- live provider 输出必须经 Pydantic 校验
- 校验失败立即 fallback 到 safe provider
