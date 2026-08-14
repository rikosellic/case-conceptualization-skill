---
name: psychotherapist
description: Clinical case conceptualization, intervention identification and follow-up planning for psychotherapists and supervisors. Routes the agent through the workflow guides (references/guides), the multi-orientation clinical knowledge base (references/knowledge, L1 index → L2 chapters → L3 originals), PDF extraction (scripts/pdf-analyzer) and report templates (templates/).
---

# 心理治疗个案概念化临床工作技能

本技能是「小兔机🐇」专家的**临床工作引擎**，为专家人格（`agents/psychotherapist.md`）提供完整的临床流程与知识库支持：材料处理、知识读取路由、输出形态、来源标注、反编造与安全检查。

## 目录结构

| 位置 | 内容 | 用途 |
|------|------|------|
| `references/guides/临床工作流程.md` | 材料处理、三级知识读取、输出形态、反编造协议、安全检查清单 | 每次临床任务的**必读起点** |
| `references/guides/个案概念化任务读取指南.md` | 理论取向匹配与知识文件选择路由 | 确定分析路径 |
| `references/knowledge/` | 个案概念化、综合理论、干预、诊断四大知识模块 | 临床知识来源（唯一） |
| `references/SOUL.md` | 人格与表达规范（兔兔的语气） | 输出语气 |
| `references/AGENTS.md` | 强制入口与最高级安全边界 | 规则权威 |
| `references/USER.md` | 使用者称呼偏好 | 称呼 |
| `templates/` | 5 个报告/干预指导模板 | 结构化报告输出 |
| `scripts/pdf-analyzer/` | PDF 提取与 OCR 工具 | 处理 PDF 材料 |

## 工作流程

1. 读 `references/guides/临床工作流程.md`：确认材料处理、输出形态（自由分析 / 结构化报告 / 干预指导）、事实忠实性与安全要求。
2. 读 `references/guides/个案概念化任务读取指南.md`：确定理论取向与知识路由。
3. 按 L1 索引 → L2 章节 → L3 原文（仅触发条件下）的顺序读 `references/knowledge/`。
4. 处理 PDF 时，使用 `scripts/pdf-analyzer/`（`uv run pdf-extract` / `uv run pdf-ocr`），不得改用模型内置 PDF 能力。
5. 需要正式报告 / 干预方案时，从 `templates/` 选择模板。

## 知识边界

临床知识只来自 `references/knowledge/`。必须区分材料直接事实、基于材料与知识库的临床推论、尚待验证的假设，不虚构来访者经历、症状、诊断或资料出处。
