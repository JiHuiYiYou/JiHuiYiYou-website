# JHYY 编译器官网 — 设计文档

> 服务于 **Next.js (App Router) + Tailwind + Vercel** 实现。
> 涵盖：双层架构（门脸 + 文档）+ 个人介绍层。
> 本文档讲"是什么 / 为什么"；视觉 tokens 实施时由 `stitch-design-taste` / `design-taste-frontend` 细化产出。

---

## 1. 北极星

**进站 5 秒要传达的事：让一个不懂编译器的开发者也想往下看，看完想装。**

要做到这条靠三股力：

| 层级 | 目标 | 实现路径 |
|---|---|---|
| **视觉冲击** | "这站不是 AI 套壳" | 暗黑主调 + 琥珀强调色 + serif 大字符句 + 一行可运行代码嵌入 hero |
| **继续阅读** | "这内容值得看完" | swimlane 节奏（一屏一主题），不堆叠，每个 section 都有"具体可说的事" |
| **内容质量** | "看完想装" | 准确、有细节、不空泛；数字 / 案例 / 可操作的 CTA |

**反北极星（要避开的）：**
- "Hello World"式 hero（"为 X 而生" + "为 Y 而设计"堆叠）
- AI-generic 三栏卡片 + 蓝紫渐变
- 没有可运行代码的"语言介绍"页
- 没有 install 入口的"快来用"按钮

---

## 2. 设计总规则

### 2.1 双层切换原则

| 层级 | 调性 | 字体 | 配色 |
|---|---|---|---|
| 门脸层 | **炫、有戏、可看** | Serif 大字 + 代码穿插 | 黑底 + 琥珀 accents |
| 文档层 | **克制、密、可学** | Sans 为主 + Mono 代码 | 近白底 + 深灰文本 |

两层切换时要有"视觉门"的过渡：从 hero 上的"看文档"点击过去，不是 URL 变了就没了，要有一次明确的"进入学习模式"动效（e.g., 顶部短闪过琥珀色，盖住门脸调性，落到文档白底）。

### 2.2 微动效原则（Stripe 哲学）

**每个动效都有功能目的，不为炫而炫：**

- 入场 fade-up（reveal）：传达"模块就位"
- 代码 typewriter：传达"程序在跑"
- scroll-driven 段落揭示：让长文有节奏
- hover transform（150-200ms）：操作反馈
- 永远不要：循环闪烁、悬浮跳出来、强视差

时长预算：单次动效不超过 600ms，绝大部分 200-400ms。

### 2.3 组件复用规则

门脸层和文档层**绝不复用同一组件**：
- 文档层的卡片 / 列表 / 导航组件，全部按"信息密集、安静"设计
- 门脸层的卡片 / 列表 / 章节组件，按"视觉强、可玩"设计
- 共享的只有 atoms：Button / Input / CodeBlock / Icon

---

## 3. 信息架构

### 3.1 路由

```
/                  → 门脸层 Landing
/docs              → 文档层（带 layout：左 TOC + 中 + 右）
  /docs/quick-start
  /docs/tour
  /docs/tutorials/*
  /docs/reference/*
  /docs/cli
/about             → 关于作者（个人介绍层）
/download          → 下载落地（GitHub Releases 跳转）
```

### 3.2 门脸层 → 文档层 → 个人介绍层的关系

```
                    ┌─ /          (门脸：5 秒钩子)
                    │
  进来 ── 看完 ────►├─ /docs      (文档：系统学习)
                    │
                    └─ /about     (个人：关系建立)
```

**门脸不写完所有内容**——它讲"为什么要看 / 怎么开始"，把"深入学"和"了解作者"分到 `/docs` 和 `/about`。

---

## 4. 门脸层设计（暗 + 琥珀 + 大字）

### 4.1 Hero

**结构：** 占满 viewport (min-h-svh)
- 左侧：大字符句标语 + 一句话定位 + 双 CTA
- 右侧：嵌入的 10-15 行可运行 hello world 代码块（语法高亮，跑 typewriter 动效）

**视觉：**
- 背景：近黑 (var(--bg-deep))
- 标语字符：serif display，字号 64-96px，琥珀色 (var(--accent-amber))
- 代码块：Mono 字体，深炭底 + 关键字琥珀 / 字符串浅米
- CTA：主按钮琥珀底黑字，副按钮描边

**动效（intent-driven）：**
- 入场：左上标语字符 stagger fade-up
- 代码块：typewriter 一次后停止（不是循环！传达"程序在跑"的感觉）
- 滚动：CTA 浮住；hero 区滚动后变暗（Stripe 同款）

### 4.2 Why JHYY

**结构：** 一屏，3-4 个价值主张卡片
- 每张：一句宣言式短句 + 一段 50-80 字解释 + 一句反问/邀请

**反模式警告：** 不要再用 "Fast ⚡ / Simple ✨ / Powerful 💪" 这种 AI-generic 卖点。要写具体的、能落地的声明。

### 4.3 Toolchain

**结构：** 横向 4 列（移动端纵向）
- compiler / IDE / VS Code ext / MCP
- 每列：图标（一笔风 SVG）+ 名字 + 一句能力

**这是真实强项**：用户拥有的不只是编译器，是全套工具链。把"做一整套"的努力显性化，比"我们编译器很快"更有说服力。

### 4.4 Build with JHYY

**结构：** 取代 MS 那个"受到开发者喜爱 / 受企业信任"。我们没这块社会证明，换成：

- 用户项目卡片 3-6 个（用 JHYY 写的小工具 / 编译生成的 demo）
- 每个卡片：项目名 + 一句话能力 + 跳转链接（GitHub / 演示）

### 4.5 Performance

**结构：** 一屏 + 数字 + bullet
- 数字示例：编译速度 / 二进制大小 / 启动时间
- Bullet：QBE 后端的优势、可移植性、跨平台支持

**视觉：** 克制，不炫。数字大、说明小、密集排版。

### 4.6 About the Author（叠加层）

**结构：** 不是独立屏，**作为叠加层**：
- 选项 A：作为 footer 上方的小段（"made by ... 一段 2-3 句话简介 + 链接"）
- 选项 B：作为 hero 浮动卡片（最不打扰的入口）

**选定 A**。理由：hero 已经够"自我"了，不要让"自我"再侵蚀第一屏的视觉冲击力。

### 4.7 Get started CTA

**结构：** 一屏
- 大字 "Get Started" 或 "立刻开始"
- 双 CTA："安装 JHYY（跳 /download）" + "读文档（跳 /docs）"
- 比 hero 大，因为这是收尾，必须留存转化窗口

---

## 5. 文档层设计（白底 + 干净 + 信息密度）

### 5.1 Layout

三栏（参考 learn.microsoft.com/dotnet/csharp）：

```
┌─────────────────────────────────────────────────┐
│ 顶栏：搜索 / 版本切换 / 主题切换 / GitHub 链接    │
├───────┬─────────────────────────────┬───────────┤
│       │                             │           │
│ 左    │   中：内容主区                │ 右        │
│ TOC   │   - h1 / h2 / h3             │ On this  │
│ 可折  │   - 段落 + 列表 + 代码       │ page     │
│ 叠    │   - Callout (note/tip/warn)  │ anchor   │
│       │                             │           │
└───────┴─────────────────────────────┴───────────┘
```

- 顶栏：固定头部，整页可滚动时跟随
- 左 TOC：sticky，`max-height: calc(100vh - 80px)`，可折叠分组
- 中内容：`max-width: 720px` 居中（阅读舒适宽度）
- 右 anchor：sticky 在主区右侧 16-24px

### 5.2 内容骨架

```
/docs
  /quick-start       一页跑通的 hello world（5 分钟内）
  /tour              语言巡礼（5-10 分钟讲清形态）
  /tutorials
    /01-basic
    /02-functions
    /03-types
    /...
  /reference
    /syntax
    /semantics
    /stdlib
  /cli               编译器命令手册
  /editor-setup      IDE / VS Code ext 配置
```

### 5.3 关键页面规格

- **教程页**：左 TOC + 中 markdown + 可运行代码块（语法高亮、有"复制"按钮；不需要内置 playground，那是 v2）
- **参考页**：表格密、可跳转 ID 链接、关键词高亮
- **搜索**：⌘K 弹 dialog，全文搜索、关键词高亮、键盘导航（参考 Stripe Docs 同款）

### 5.4 调性

- 文字优先，图形极少（最多代码块）
- 字体：sans (Inter) 正文、mono (JetBrains Mono) 代码
- 配色：近白底 (#FAFAFA) + 深灰文本 (#1A1A1A) + 琥珀强调（用于 `<a>` hover / 关键字 / callout 标题）
- **不动效**（除 scroll-revealed progress indicator）

---

## 6. 个人介绍层 / `/about`

### 6.1 内容

- 头像（大尺寸，琥珀边框）
- 一段 2-3 句话简介（第一人称，"我是 X，做 Y，因为 Z"）
- 项目列表：编译器官网 / 其他个人项目
- 联系方式：GitHub / 邮箱 / 其他社交
- 时间表 / 现在在做什么（1-2 条）

### 6.2 风格

- 文本驱动，**不靠视觉**
- 字体跟文档层一致（白底 + 干净），但用琥珀 accents 加点个人味
- 留白多
- 调性跟文档层接近，但可以有 1-2 张大图（用户头像 / 项目截图）

---

## 7. 组件清单

### Atoms（门脸 + 文档复用）

- `Button`：主 / 次 / 幽灵三态
- `Icon`：内联 SVG，统一来自 `lucide-react`
- `CodeBlock`：语言标识 / 复制按钮 / 主题切换跟随
- `Link`：内 / 外链接区分样式

### 门脸层专属

- `Hero`（首屏大字 + CTA + 代码示例）
- `SwimLane`（满屏章节容器 + 章节锚点）
- `ValueCard`（宣言式卖点卡）
- `ToolchainShowcase`（横向 4 列工具展示）
- `ProjectShowcaseCard`（用户项目展示）
- `StatBlock`（性能数字）
- `CTAFinal`（收尾强 CTA）

### 文档层专属

- `TOC`（左侧目录，sticky）
- `OnThisPage`（右侧 anchor）
- `DocLayout`（三栏容器）
- `SearchDialog`（⌘K 搜索弹窗）
- `Callout`（note / tip / warning 三种）
- `RefTable`（参考文档表格）
- `Breadcrumb`

---

## 8. Reference 映射（已确定）

| JHYY 的部分 | Reference | 借鉴点 |
|---|---|---|
| Hero、toolchain、build、performance | `dotnet.microsoft.com/zh-cn/languages/csharp` | swimlane 节奏、工具链横向叙事、双 CTA hero |
| 文档三栏 + 搜索 + 代码 | `learn.microsoft.com/zh-cn/dotnet/csharp` | 完整 docs 模板 |
| 微动效用 intent | Stripe 哲学 | "动效得有功能目的" |
| 渐进披露 + 便当盒 | Stripe 哲学 | "信息密但不堆" |
| 抗平庸 | Stripe 哲学 | "接受足够好就输" |

**不抄的部分：**

- MS 那套企业蓝紫渐变 + 严肃感 → 我们的琥珀 + 暗，更"个人"
- 商业库贴图 → 我们的 hero 直接用可运行代码演示
- "Loved by millions"社会证明 → 我们没这块，换成"用户项目小卡片"

---

## 9. 反模式（明确禁止）

- ❌ Tailwind 默认 `bg-blue-500` 类配色
- ❌ "Fast ⚡ Simple ✨ Powerful 💪" AI-generic 卖点
- ❌ Hero 区贴一张"团队微笑"或者办公室的 stock photo
- ❌ 字体 fallback 到 system-ui 不设 fallback stack
- ❌ 文档层加 scroll-reveal 动效（除 progress indicator）
- ❌ 用 emoji 当 UI 元素（hero 那行 mono 代码里可有，那是 code，不是 UI）
- ❌ 复制粘贴 MS 站原句（要换字、要做出"这是个人项目"的语气）

---

## 10. 决策记录（per conversation log）

- **框架**：Next.js App Router 全套（不用静态导出）—— 用户明确反对"静态"
- **样式**：Tailwind + 可能的 `tailwindcss-animate` 微动效库
- **部署**：Vercel（用户明确不备案）
- **下载追踪**：GitHub Releases API（前端构建时拉，SSR 注入数据）
- **视频托管**：暂不用，文档层不需要视频
- **搜索**：v1 用 Algolia DocSearch（免费 OSS 计划）/ FlexSearch（自建）；v2 评估 Algolia
- **代码高亮**：Shiki 或 Prism（Next.js 生态成熟）
- **不引入**：backend、自建数据库、自建 admin

---

## 11. 下一步

1. 起 Next.js 14+ App Router 项目骨架到 `projects/JiHuiYiYou官网/`
2. 调 `stitch-design-taste` 跑一遍，输出 `DESIGN_TOKENS.md`（colors / spacing / typography exact values）
3. 调 `imagegen-frontend-web` 给 Hero、Toolchain、About 出参考图
4. 实施 Design System（tokens + atoms）
5. 实施门脸层（先做骨架，迭代视觉）
6. 实施文档层
7. 实施 `/about` 个人页
8. 接 GitHub Releases API 接 Vercel 部署
9. 接 Algolia 搜索
10. 上线
