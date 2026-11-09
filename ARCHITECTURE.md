# JHYY 家族官网 — 站点结构与现状

> 这份文档讲**站是怎么搭的**：路由、内容骨架、构建管线、门、组件，
> 以及**现在建成什么样**。
>
> 为什么这么设计 ⇒ [`DESIGN.md`](DESIGN.md)；
> 还没做的事 ⇒ [`Task.md`](Task.md)；
> 写页面的规约 ⇒ [`tools/CONTENT_GUIDE.md`](tools/CONTENT_GUIDE.md)。
>
> **一条规则只写一处** —— 别处只留指针。

---

## 1. 路由

```
/                                  家族首页（四个项目）
/compiler/                         编译器首页（门脸层）
/compiler/docs/                    文档区（浅色三栏）
  /compiler/docs/getting-started.html
  /compiler/docs/tour.html
  /compiler/docs/reference.html
  /compiler/docs/spec.html
  /compiler/docs/abi.html
  /compiler/docs/stdlib.html
  /compiler/docs/arena.html
  /compiler/docs/osdev.html
  /compiler/docs/cli.html
  /compiler/docs/compiler.html
  /compiler/docs/build-and-test.html
  /compiler/docs/faq.html
/compiler/download/                下载区（浅色三栏）
  /targets.html  /bootstrap.html  /verify.html
/compiler/community/               社区区（浅色三栏）
  /conduct.html  /contributing.html  /security.html
/compiler/governance/              治理区（浅色三栏）
  /license.html  /repo-map.html
/ide/  /os/  /vex/                 另外三个项目的落地页（门脸层）
```

## 2. 家族结构

```
                       ┌─ /          （枢纽：四项目分流）
                       │
   进来 ── 看完 ──────►├─ /compiler/ （编译器：完整五区）
                       │
                       ├─ /ide/  /os/  /vex/   （各自一页 + 仓库文档外链）
                       │
                       └─ /compiler/community/  （怎么参与）
```

**三个早项目的分栏不指向站内空页**，直接链各自仓库里的真实文档——
不为凑导航栏造一个没有内容的站内页面。

---

## 3. 内容骨架

```
content/
├─ index.html                     家族首页（门脸）
├─ compiler/
│  ├─ index.html                  编译器首页（门脸）
│  ├─ docs/*.md                   12 页文档
│  ├─ download/*.md               4 页下载
│  ├─ community/*.md              4 页社区
│  └─ governance/*.md             3 页治理
├─ ide/index.html os/index.html vex/index.html   三个项目的门脸页
└─ en/                            **英文树** —— 与上面同构
   ├─ index.html
   ├─ compiler/index.html + docs/ download/ community/ governance/
   └─ ide/index.html os/index.html vex/index.html
```

`en/` 下的每个文件都有中文孪生页（`route` 相同即孪生）：
`content/en/compiler/docs/tour.md` ↔ `content/compiler/docs/tour.md`。
孪生关系由 `tools/i18n.py` 的 route 契约管，`tools/check_twins.py` 守。

---

## 4. 内容流水线

```
content/**/*.md     ──┐
content/**/*.html   ──┤
                      ├─→ tools/build.py ──→ *.html（提交进仓库，GH Pages 直出）
tools/siteconfig.py ──┘         │
tools/i18n.py ──────────────────┤
                                ├─→ search-index.json
                                └─→ tools/build.py --check（链接与锚点检查）
```

- `tools/siteconfig.py` —— **全站唯一真相源**：版本号、目标表、产物表、
  状态数字、导航与侧栏、以及 `FACTS`（事实占位符的取值表）。
- `tools/i18n.py` —— 术语表（`GLOSSARY`）、界面字符串（`UI`）、专名白名单
  （`KEEP_CJK`）、孪生页契约（`TWIN_REQUIRED` / `TWIN_EXEMPT_PREFIXES`）。
- `tools/mdrender.py` —— 零依赖 Markdown 渲染器（CommonMark 子集 +
  callout + mermaid + `[[Wiki 链接]]`）。
- `tools/build.py` —— 站点生成器 + 链接检查 + **双语双树**。
- `tools/check_examples.py` —— 把文档里的 `.jhyy` 代码块抽出来交给真编译器验。
- `tools/CONTENT_GUIDE.md` —— 内容写作规约（文风 / 方言 / 事实来源 / 常见坑）。

### 4.1 双语双树

`content/**` = 中文（`/`），`content/en/**` = 英文（`/en/`）——
**语言是构建的一部分**，不是各页各自为政。构建期建立 route → {zh, en} 的
映射，同一 route 的两页互为**孪生页**；语言切换器是普通 `<a>`（无 JS 依赖）。

搜索索引只有一份（`search-index.json`），每条带 `lang` 字段，
`docs.js` 按当前页语言过滤。

### 4.2 事实只有一份

正文里写 `{{site_version}}` / `{{regress_pass}}` 这类占位符，
构建器从 `siteconfig.FACTS` 取值 —— **两种语言拿的是同一份常量，不可能对不上
数字**。`check_facts.py` 负责跟编译器仓那份真相对拍（之前官网写着「回归 279
PASS」，编译器仓已经改成 281 了，没有任何门会红）。

未知占位符在构建期**直接报错**（报出 key 与源文件），不静默留空。

### 4.3 术语只有一份

术语表在 `tools/i18n.py` 的 `GLOSSARY`（**唯一副本**）：
`python tools/check_i18n.py --dump-glossary` 打印当前全表。
一个概念只准一种说法；两种语言里都保持英文的词在 `KEEP_EN`。

### 4.4 路径约定

正文用**根绝对路径**写站内链接（`/compiler/docs/tour.html`），
构建时按页面深度自动改写成相对路径——站点挂在 `user.github.io/<repo>/`
下也不会 404。资源路径同理（`/assets/img/…`）。

---

## 5. 门

本地可跑，CI 也跑：

| 门 | 查什么 | 级别 |
|---|---|---|
| `tools/check_facts.py` | `siteconfig.FACTS` ↔ 编译器仓 `docs/internal/FACTS.md` 对拍（17 项） | 错误 |
| `tools/check_twins.py` | 每个页面都要有中英两版 | 错误 |
| `tools/check_i18n.py` | 正文里不许手写事实（改用 `{{key}}`）、英文页里不许出现中文、术语说法一致 | 错误 + 警告 |
| `tools/build.py --check` | 站内链接与锚点不断（两棵树都扫） | 错误 |
| 同步门（CI 里 `git diff` + `git ls-files --others`） | `content/` 改了要重建；**未跟踪的生成物也算** | 错误 |

事实门上线以来抓到过两次真漂移：产物级门数从 19 漂到 21，以及编译器仓发 v4.1.5
之后官网的版本号没跟上。**它不是空门。**

**但它的对拍范围只有编译器仓**：`siteconfig.FACTS` 里的 `ide_version` /
`ide_gate_*` / `os_spike_measured` / `vex_baseline_*` 来自另外三个仓，
编译器仓的 `FACTS.md` 里没有这几行 ⇒ **它们不会自动变红**。
这三个仓各自发版或补测之后，要人工核一遍（单子在 [`Task.md`](Task.md) § 5）。
for-VEX 那一组已经这样漂过一次：官网还写着「消息泵 tick 频率待测」，
而 for-VEX 仓 2026-11-09 已经在真 Brain 上测得（100 Hz）。

---

## 6. 组件清单

### Atoms（门脸 + 文档复用）
- `Icon`：内联 SVG
- `CodeBlock`：语言标识 / 复制按钮
- `Link`：内 / 外链接区分样式

### 门脸层专属
`Hero`（大字 + CTA + 版本闸门）· `Bento` · `Card` · `ToolCard` ·
`PerfCell` · `EcoCard` · `DocCard` · `VersionGate` · `CTA` ·
`FamilyGraph`（共享层 → 编译器 → 三分支）· `ChangeGrid`（最近变化 / 诚实的边界）

### 文档层专属
`DocTopbar`（含项目切换与搜索）· `TOC` · `OnThisPage` · `Callout`
（note / warn / danger）· `RefTable` · `SearchModal`

### 两层共用（只有 atoms）
`Icon`（内联 SVG）· `CodeBlock`（语言标识 / 复制按钮）· `Link` ·
**`LangSwitch`**（语言切换，普通 `<a>`，无 JS 依赖）

---

## 7. 现状

**已完成**：四项目枢纽、编译器五区 24 页、站内搜索、链接检查、
文档示例真编译验证、下载镜像与校验和同步到 v4.1.5；
**首页重做**（纯枢纽四屏：Hero / 四个项目 / 一门语言撑起四个项目 / 最近变化与诚实的边界）；
**双语地基**（构建期双树、语言切换器、术语表、事实占位符）+ 5 页门脸中英双版；
**四道新门**（事实对拍 / 孪生页 / i18n 一致性 / 同步门补未跟踪产物）。

**四个门脸页统一了屏语法**：首页、编译器、IDE、OS、for-VEX 现在是同一套版式
（Hero → 分屏 → 现状与边界 → 看数字 → 文档与仓库 → CTA），中英同构。
IDE / OS / for-VEX 三页原来各是一整页 Markdown 散文墙，现已按这套语法重做 ——
OS 页用 `showcase` 展示 `spike/boot.s` 的原话，for-VEX 页用八张卡展示规格书八项。
编译器落地页也按同一条判据收了一遍：hero 的代码窗口删掉（同一段 `dist_sq`
原本在页面上出现三次）、01 屏的两处代码片段换成事实戳、04 屏的「安装器」卡
（与 02 屏重复）换成 arena 运行时、「关于作者」屏挪到最后（09），
08 屏的标题从**没定义过的** `sec-title` 改回 `section-title`。

**跟版 v4.1.5**：三条真修（`std::arena` 的 reset 越界 / `#[naked]` 的标签与体分离 /
side-file 路径相对 CWD）进发行版 ⇒ 文档层里那三处「已修却仍写成缺口」的表述一并改掉，
首页中英两版的「最近变化」换成这一版，产物镜像与校验和换成 4.1.5（与线上逐字节一致）。

**还没做的事在 [`Task.md`](Task.md)**。
