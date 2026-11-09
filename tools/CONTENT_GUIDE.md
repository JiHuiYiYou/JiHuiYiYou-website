# 官网内容写作规约

> 所有 `content/**` 下的页面都按这份写。改这份之前先想清楚——六个区块的页面必须读起来像同一个人写的。

## 1. 你产出什么

- 只写 `content/` 下的 Markdown 源文件。
- **不要**改 `tools/`、`assets/`、任何 `.html`、任何 `downloads/` 里的二进制。
- 写完**不要**运行 `python tools/build.py`（统一构建由主控执行）。

## 1.5 两棵树

- `content/**` = **中文**（站点根 `/`）
- `content/en/**` = **英文**（`/en/`）

（机制与目录结构见 `ARCHITECTURE.md` §3 / §4；这里只讲怎么写。）

两棵树同构：同一个 route 的中英两页互为**孪生页**。
每个页面都要有孪生页 —— `tools/check_twins.py` 守。

写英文源时：

- 站内链接**照抄中文源的目标**（`/compiler/docs/tour.html`）—— 构建器
  会按当前语言改写到英文孪生页；没有英文孪生页的（文档层本轮还没译）
  保留指向中文页，并在 Markdown 链接上加标题：`[快速上手](/compiler/docs/getting-started.html "Chinese only")`
- **不要**在英文源里写相对路径
- 英文源**不许出现中文**（专名 `机会翼游` 除外）—— `tools/check_i18n.py` 守

---

## 2. front matter（必须，原样保留字段名）

```markdown
---
title: 页面标题
description: 一句话描述（会进 <meta name="description">，也进站内搜索索引）
layout: docs
project: compiler
zone: docs
---
```

| 字段 | 取值 |
|---|---|
| `layout` | `docs`（浅色三栏，信息密集）/ `page`（深色门脸，产品落地页） |
| `project` | `compiler` / `ide` / `os` / `vex` |
| `zone` | `docs` / `download` / `community` / `governance` / `home` / `ide` / `os` / `vex` |

`zone` 决定左侧栏用哪一套目录，必须和页面实际所属的区一致。

## 3. Markdown 方言（全站统一，别混用）

支持：ATX 标题 `#`~`######`；段落；无序列表 `-`、有序列表 `1.`（支持两级缩进嵌套）；
围栏代码块 ```lang（`jhyy` / `bash` / `rust` / `c` / `asm` / `json` / `mermaid`）；
行内代码；**粗体**；*斜体*；链接；表格；引用块；`---` 分隔线；`mermaid` 围栏块（会渲染成图）。

**不支持**：任何 HTML 标签、setext 标题、脚注、emoji、`> [!NOTE]` 以外的扩展语法。

### 站内链接必须写成根绝对路径

```markdown
[下载](/compiler/download/index.html)      ✓
[下载](../download/)                       ✗ 构建器按输出目录算深度，写不对
[规范原文](https://github.com/.../x.md)    ✓ 外链就写完整 URL
```

构建时根绝对路径会被自动改写成相对路径，所以站点挂在 `user.github.io/<repo>/` 下也不会 404。

### 已知可用的站内链接（写的时候照抄，别自己拼）

```
/index.html                              家族首页
/compiler/index.html                     编译器首页
/compiler/docs/index.html                文档首页
/compiler/docs/getting-started.html      快速上手
/compiler/docs/tour.html                 语言导览
/compiler/docs/reference.html            参考总览
/compiler/docs/spec.html                 语言规范
/compiler/docs/abi.html                  ABI
/compiler/docs/stdlib.html               标准库
/compiler/docs/arena.html                Arena 内存管理
/compiler/docs/osdev.html                裸机与内核开发
/compiler/docs/cli.html                  CLI 参考
/compiler/docs/compiler.html             编译器实现
/compiler/docs/build-and-test.html       构建与测试
/compiler/docs/faq.html                  常见问题
/compiler/download/index.html            下载首页
/compiler/download/targets.html          目标与交叉编译
/compiler/download/bootstrap.html        源码构建与自举
/compiler/download/verify.html           校验与签名
/compiler/community/index.html           社区首页
/compiler/community/conduct.html         行为准则
/compiler/community/contributing.html    贡献指南
/compiler/community/security.html        安全披露
/compiler/governance/index.html          治理总览
/compiler/governance/license.html        许可证
/compiler/governance/repo-map.html       仓库地图
/ide/index.html  /os/index.html  /vex/index.html
```

## 4. 文风（硬要求）

- 中文正文；技术术语保留英文原词：`arena` / `IR` / `ABI` / `target` / `linker script` / `sysroot` / `calling convention` / `backend` / `freestanding` / `no_std`。
- **禁止 emoji。**
- **禁止营销腔**：「震撼」「史无前例」「我们很高兴地宣布」「打造极致体验」。官网的读者是来查事实的。
- **每个断言都要能追溯到一个文件**。数字、版本号、命令、API 签名、文件路径都必须来自下面的事实来源。
- **查不到就不要写**。宁可少写一段，也不要编一个看起来合理的数字。
- 表格优先于长段落；命令块给完整可粘贴的版本（不是片段）。
- 每页 800–2000 字；专项长页可以到 2500。
- 页面第一句就说清这页解决什么问题，不要「欢迎来到……」。

### 版本号的处理

**不要在正文里手写版本号。** 全部链接到 `/compiler/download/index.html` 或写「当前稳定版」，
让下载页承担版本事实。唯一例外是「语言规范 v4.0.0」「ABI v4.0.0」这种**契约版本**
——它们和工具链版本是两件事，写清楚即可。

### 事实用占位符，不要写字面量

正文里写 `{{key}}`，构建器从 `tools/siteconfig.py` 的 `FACTS` 取值：

```markdown
回归 {{regress_pass}} PASS / {{regress_failed}} FAIL（共 {{regress_total}} 条）
```

取值表在 `tools/siteconfig.py` 的 `FACTS`（**唯一副本**，机制见 `ARCHITECTURE.md` §4.2）。
`tools/check_i18n.py` 会把正文里手写的特征值（当前版本号、回归数、门数……
**取值从 `siteconfig.FACTS` 现算**，不手写）当**错误**报出来；
`tools/check_facts.py` 负责跟编译器仓那份真相对拍。

常用键：`site_version` `site_version_date` `spec_version` `abi_version`
`binary_format_version` `ide_version` `regress_total` `regress_pass`
`regress_skip` `regress_failed` `assertions` `artifact_checks`
`workarounds_total` `workarounds_active` `stdlib_modules` `ide_gate_pass`
`ide_gate_total` `os_spike_measured` `vex_baseline_total` `vex_baseline_done`
`vex_baseline_pending` `legacy_abi_version`

### 资源路径

正文里的资源路径写**根绝对**（`/assets/img/…`）—— 构建器按页面深度改写成
相对路径。英文树尤其不能写相对路径（`/en/` 下会解析到 `/en/assets/…`）。

## 4.5 术语

一个概念**只准一种说法**。术语表在 `tools/i18n.py` 的 `GLOSSARY` —— **唯一副本**。

```bash
python tools/check_i18n.py --dump-glossary   # 打印当前全表（概念 / 中文 / English）
```

**不要把表抄进本文件** —— 抄了就是第二个副本，加词时必然只改一处、两处开始漂。
`tools/check_i18n.py` 按表检查正文用词，对不上报**警告**。

两种语言里都**保持英文**的词（`KEEP_EN`）：`ABI` `IL` `IR` `arena` `backend`
`freestanding` `no_std` `linker script` `sysroot` `calling convention` `target` …
（完整名单同样用 `--dump-glossary` 看。）

---

## 5. 事实来源（只读）

| 主题 | 位置 |
|---|---|
| 全站常量（版本号、目标表、产物表、状态数字） | `tools/siteconfig.py` |
| 编译器总览 | `C:\Users\liuzhen\Desktop\coding\JiHuiYiYou\README.md` / `README.zh-CN.md` |
| 版本变更 | `C:\Users\liuzhen\Desktop\coding\JiHuiYiYou\CHANGELOG.md` |
| 语言契约 | `...\JiHuiYiYou\docs\abis\jhyy-lang-spec-v4.0.0.md` |
| ABI 契约 | `...\JiHuiYiYou\docs\abis\jhyy-abi-v4.0.0.md` |
| 二进制格式 | `...\JiHuiYiYou\docs\abis\jhyy-binary-format-v1.0.0.md` |
| 架构 / 状态数字 | `...\JiHuiYiYou\docs\internal\architecture.md` / `FACTS.md` |
| 问题台账 | `...\JiHuiYiYou\docs\internal\workarounds.md` |
| 标准库真实 API | `...\JiHuiYiYou\compiler\src0\std\*.jhyy` |
| 贡献 / 行为准则 / 安全 | `...\JiHuiYiYou\CONTRIBUTING.md` / `CODE_OF_CONDUCT.md` / `SECURITY.md` |
| 许可证 | `...\JiHuiYiYou\LICENSE` |
| IDE | `C:\Users\liuzhen\Desktop\coding\JiHuiYiYou-IDE\README.zh-CN.md` / `docs\wiki\*.zh-CN.md` |
| OS | `C:\Users\liuzhen\Desktop\coding\JiHuiYiYou-OS\spike\` |
| for-VEX | `C:\Users\liuzhen\Desktop\coding\jhyy-for-vex\README.md` / `docs\00-事实基线.md` |

## 6. 几条容易踩的坑

1. **JHYY 只有 amd64。** 没有 aarch64、没有 riscv、没有 wasm。目标只有
   `amd64_win` / `amd64_sysv` / `amd64_win_freestanding` / `amd64_sysv_freestanding`。
2. **后端是自研的 amd64 发射器**，不是 LLVM，也不是「vendor 进来的 QBE」。
   QBE 只贡献了**中间文本的语法**作为起点。
3. **宿主只有 Windows x64。** 产物可以到 Linux（SysV 汇编 → 外部 ld → ELF），但编译器本身不在 Linux 上跑。
4. **安装器和 MSI 都没有代码签名。** 官网必须写明这一点，别绕。
5. **「预 1.0」是项目自己的说法**：自举成立、回归全绿，但还不是 C/Rust 的替代品。
6. **arena 不是「没有 free」**：JHYY 的 arena 同时提供 `arena_reset`（复用内存）和 `arena_free`（整块释放）。
   别照抄别的语言的 arena 模型。
