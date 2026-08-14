# 小兔机🐇 — WorkBuddy 心理治疗与个案概念化专家

面向心理咨询师、心理治疗师和督导工作的 WorkBuddy 专家（Agent 型）。它可根据初访记录、咨询记录、治疗逐字稿、督导材料或报告草稿，辅助生成中文个案概念化、识别既有干预、分析治疗难点并规划后续干预。

由原 OpenClaw Agent workspace（`psychotherapist/`）迁移而来，功能、语气与人格保持不变。

## 类型

`expertType: "agent"`（单专家，非专家团）

## 专家身份

- **名字**：小兔机🐇（自称兔兔）
- **职业**：心理治疗·个案概念化与督导辅助专家
- **头像**：`avatars/expert.png`（由原「小兔机头像.JPG」缩放至 512×512）

## 目录结构

```text
psychotherapist/
├── .codebuddy-plugin/
│   └── plugin.json          # 专家包清单（名称、展示信息、分类、标签等）
├── agents/
│   └── psychotherapist.md   # 专家定义：人格 + 能力 + 工作流程 + 输出规范 + 安全边界
├── skills/
│   └── psychotherapist/
│       ├── SKILL.md         # 临床工作技能入口
│       ├── references/      # 临床参考内容（原样保留）
│       │   ├── AGENTS.md    # 完整强制入口规则（原文）
│       │   ├── SOUL.md      # 完整人格与语气规范（原文）
│       │   ├── USER.md      # 使用者称呼偏好
│       │   ├── TOOLS.md     # PDF 工具说明
│       │   ├── IDENTITY.md  # 展示身份
│       │   ├── guides/      # 临床工作流程与知识读取指南
│       │   └── knowledge/   # 核心知识库：个案概念化/干预/诊断（149 个文件）
│       ├── scripts/
│       │   └── pdf-analyzer/ # PDF 提取与 OCR 工具（uv 环境）
│       └── templates/       # 5 个报告 / 干预指导模板（.md + .docx）
├── avatars/
│   └── expert.png           # 专家头像（512×512，≤500KB）
└── README.md
```

`references/guides/` 与 `references/knowledge/` 是原治疗师 Agent 的核心，内容未做改动；专家在运行时按 `references/guides/` 的 L1/L2/L3 纪律读取它们。

## 安装到 WorkBuddy

专家包必须放到 WorkBuddy 的专家目录才能被检测到：

```
C:\Users\<用户名>\.workbuddy\plugins\marketplaces\my-experts\plugins\
```

（若设置了 `WORKBUDDY_CONFIG_DIR` 环境变量，则为 `$WORKBUDDY_CONFIG_DIR\plugins\marketplaces\my-experts\plugins\`）

把整个 `psychotherapist-workbuddy` 文件夹复制（或重命名为 `psychotherapist`）到该目录下，然后在 WorkBuddy 中：

1. 左侧边栏进入「专家」→「我的专家」；
2. 若未自动出现，重启 WorkBuddy 或重新扫描专家；
3. 点击「召唤专家」开始使用。

也可以直接在 WorkBuddy 中通过「专家 → 我的专家 → 创建专家 / 从资料转化」完成，或使用内置的「专家包管理器」技能校验与注册本包。

## 使用方式

- `帮我看看这段咨询里可能发生了什么` → 自由分析（默认）
- `请整理成一份心理动力学个案报告，重点写治疗关系` → 结构化报告
- `请基于这份概念化给出完整的后续干预方案` → 干预指导

## 头像替换

如需更换头像，替换 `avatars/expert.png`：PNG/JPG，512×512，单张 ≤500KB，并保持 `plugin.json` 中 `avatar` 字段一致。

## 隐私与临床边界

- 不要把真实来访者身份、原始咨询记录、联系方式等敏感资料提交到版本库。
- 输出用于临床辅助和督导讨论，不替代持证专业人员的评估、诊断、伦理判断或危机处置。
- 涉及急性风险时，优先执行现实世界中的风险评估、机构流程和当地紧急支持安排。
