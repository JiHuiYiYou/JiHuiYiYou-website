"""JHYY 官网的 i18n 层 —— 术语表、界面字符串、孪生页契约。

三件事被钉在这里，理由都是「让错误在构建期暴露，而不是上线后靠人眼」：

1. **术语表**（`GLOSSARY`）—— 同一个概念，中英文各只准一种说法。
   写作规约与翻译都查这一张表；术语 lint 也查它。
2. **界面字符串**（`UI`）—— 构建器只通过 `t(lang, key)` 取值，
   取不到就 `KeyError` ⇒ 漏译在构建期崩，不会漏到线上。
3. **孪生页契约**（`TWIN_REQUIRED` / `TWIN_EXEMPT_PREFIXES`）—— 哪几页必须
   有中英两版。下一轮把文档层也译出来 = 删掉豁免前缀那几行，门逻辑不动。

站点是**构建期双树**：`content/**` = 中文 → `/`，`content/en/**` = 英文 → `/en/`。
现有中文 URL 不变。
"""

from __future__ import annotations

LANGS = ("zh", "en")

# ── 术语表 ────────────────────────────────────────────────────────────────
# 概念 → {中文, English}。**一个概念只准出现表里的这一种说法。**
#
# 新增条目前先确认：这个词在两种语言里是不是真的只有一个固定说法？
# 译名会变的（同一个词在不同上下文有不同惯例）就别进表 —— 表里只放
# 「全站必须统一」的那批。
GLOSSARY = {
    "self_hosted": {"zh": "自举", "en": "self-hosted"},
    "expression_oriented": {"zh": "面向表达式", "en": "expression-oriented"},
    "artifact_checks": {"zh": "产物级门", "en": "artifact checks"},
    "bare_metal": {"zh": "裸机", "en": "bare metal"},
    "arena": {"zh": "arena", "en": "arena"},
    "workaround_ledger": {"zh": "问题台账", "en": "workaround ledger"},
    "workbench": {"zh": "工作台", "en": "workbench"},
    "target_triple": {"zh": "目标三元组", "en": "target triple"},
    "contract_version": {"zh": "契约版本", "en": "contract version"},
    "emitter": {"zh": "发射器", "en": "emitter"},
    "regression_suite": {"zh": "回归套件", "en": "regression suite"},
    "byte_equal": {"zh": "逐字节相同", "en": "byte-identical"},
    "fixed_point": {"zh": "不动点", "en": "fixed point"},
    "family": {"zh": "家族", "en": "family"},
    "landing_page": {"zh": "门脸层", "en": "landing page"},
}

# 两种语言里都会出现的专名 —— 语言自己的中文名。
# 它是这门语言的正式名字，英文页里也照写（JHYY (机会翼游)）⇒ CJK lint 不许误报。
KEEP_CJK = {"机会翼游"}

# 两种语言里都保持英文的词（不译）—— 来自 tools/CONTENT_GUIDE.md §4「文风」。
# 术语 lint 遇到这些不许报警。
KEEP_EN = {
    "arena", "IR", "ABI", "target", "backend", "freestanding", "no_std",
    "linker script", "sysroot", "calling convention", "IL", "PE/COFF", "SysV",
    "asm!", "defer", "volatile", "match", "enum", "extern fn", "struct",
    "uint8", "uint32", "uint64", "int32", "int64", "uintptr", "usize", "isize",
    "u8", "u16", "u32", "u64", "i8", "i16", "i32", "i64", "bool", "char",
    "string", "void", "main_jhyy", "Cap<T>", "amd64", "UEFI", "OVMF", "ARM",
    "Cortex-A9", "Xilinx", "Zynq", "VEX", "Blockly", "CodeMirror", "Electron",
    "SmartScreen", "MSI", "VSIX", "winget", "scoop", "GitHub", "SHA256",
    "PPTX", "PDF", "ISO", "RFC", "MIT", "VS Code", "Windows", "Linux", "MSYS2",
}

# ── 界面字符串 ────────────────────────────────────────────────────────────
# 构建器只经 `t(lang, key)` 取值 ⇒ 少一个 key 就构建期 KeyError。
# 占位符用 {name} 形式，调用方自己 format。
UI = {
    "zh": {
        "lang_name": "中文",
        "lang_other": "English",
        "lang_switch_label": "语言",
        "all_projects": "全部项目",
        "download_cta": "下载 v{version}",
        "latest_stable": "最新稳定版",
        "search_docs": "搜索文档",
        "on_this_page": "本页",
        "on_this_page_aria": "本页目录",
        "spec_sources": "规范原文",
        "lang_spec": "语言规范 v{version}",
        "abi_spec": "ABI v{version}",
        "binary_format": "二进制格式 v{version}",
        "changelog": "变更日志",
        "ledger": "问题台账",
        "edit_page": "编辑此页 ↗",
        "report_issue": "报告问题 ↗",
        "foot_family": "家族",
        "foot_compiler": "编译器",
        "foot_repos": "仓库",
        "foot_specs": "规范",
        "foot_community": "社区",
        "foot_tag": "机会翼游家族 · 编译器 / IDE / OS / for-VEX",
        "foot_issues": "Issues",
        "foot_contributing": "贡献指南",
        "foot_security": "安全披露",
        "foot_qq": "QQ 群 {number}",
        "foot_copy_qq": "复制 QQ 群号",
        "foot_copyright": "© 2026 机会翼游 · MIT License",
        "foot_status": "v{version} · spec v{spec} · main",
        "doc_toc": "文档目录",
        "zh_only": "仅中文",
        "en_only": "仅英文",
        "primary_nav": "主导航",
        "family_nav": "机会翼游家族",
        "brand_home": "机会翼游 · JHYY 首页",
        "github": "GitHub",
    },
    "en": {
        "lang_name": "English",
        "lang_other": "English",
        "lang_switch_label": "Language",
        "all_projects": "All projects",
        "download_cta": "Download v{version}",
        "latest_stable": "Latest stable",
        "search_docs": "Search docs",
        "on_this_page": "On this page",
        "on_this_page_aria": "On this page",
        "spec_sources": "Spec sources",
        "lang_spec": "Language spec v{version}",
        "abi_spec": "ABI v{version}",
        "binary_format": "Binary format v{version}",
        "changelog": "Changelog",
        "ledger": "Workaround ledger",
        "edit_page": "Edit this page ↗",
        "report_issue": "Report an issue ↗",
        "foot_family": "Family",
        "foot_compiler": "Compiler",
        "foot_repos": "Repositories",
        "foot_specs": "Specs",
        "foot_community": "Community",
        "foot_tag": "The JHYY family · Compiler / IDE / OS / for-VEX",
        "foot_issues": "Issues",
        "foot_contributing": "Contributing",
        "foot_security": "Security disclosure",
        "foot_qq": "QQ group {number}",
        "foot_copy_qq": "Copy the QQ group number",
        "foot_copyright": "© 2026 机会翼游 · MIT License",
        "foot_status": "v{version} · spec v{spec} · main",
        "doc_toc": "Table of contents",
        "zh_only": "Chinese only",
        "en_only": "English only",
        "primary_nav": "Primary",
        "family_nav": "The JHYY family",
        "brand_home": "机会翼游 · JHYY home",
        "github": "GitHub",
    },
}


def t(lang: str, key: str, **fmt) -> str:
    """取界面字符串。**取不到就 KeyError** —— 这是故意的。

    漏译必须炸在构建期；返回一个空串或者原文，等于把漏译推上线。
    """
    table = UI[lang]
    if key not in table:
        raise KeyError(f"界面字符串缺 {lang} 的 {key!r}")
    return table[key].format(**fmt) if fmt else table[key]


# ── 孪生页契约 ────────────────────────────────────────────────────────────
# 本轮必须中英双版的 route（相对站点根，不带语言段）。
TWIN_REQUIRED = [
    "index",
    "compiler/index",
    "ide/index",
    "os/index",
    "vex/index",
]

# 豁免前缀 —— **空**。文档层 24 页已全部译出（2026-11-10），
# 以前那四行（compiler/docs/ download/ community/ governance/）在这里，
# 现在删掉了 ⇒ **全站每一页都必须有中英两版**，加新页面没有豁免可钻。
#
# 规则是前缀驱动的：将来若真要豁免某一段，加回前缀即可，门逻辑一行不用动。
TWIN_EXEMPT_PREFIXES: list[str] = []

# ── 字面量事实 lint 的契约 ────────────────────────────────────────────────
# 这些字符串在本站没有别的含义 ⇒ 出现在正文里几乎一定是「手写了事实」。
# 扫到就报「用 {{key}} 占位符代替」。
#
# 扫描范围：**全站**（门脸页 + 文档层，中英各一版）。
#
# ⚠️ 2026-11-10 修一个自己踩的坑：这一栏原来写的是 `content/ide/index.md` ——
# 那三个项目页从 .md 改成 .html 之后，路径对不上了，而门里是
# `if not path.exists(): continue` ⇒ **那三页直接不再被扫**（没人报错，门就空了）。
# ⇒ 范围改成**目录**（目录会递归扫），路径写错当场就看得出来（扫到 0 个文件）。
FACT_LINT_SCOPE = [
    "content/index.html",
    "content/en/index.html",
    "content/compiler/index.html",
    "content/en/compiler/index.html",
    "content/ide/index.html",
    "content/en/ide/index.html",
    "content/os/index.html",
    "content/en/os/index.html",
    "content/vex/index.html",
    "content/en/vex/index.html",
    # 文档层（中英）
    "content/compiler/docs",
    "content/compiler/download",
    "content/compiler/community",
    "content/compiler/governance",
    "content/en/compiler/docs",
    "content/en/compiler/download",
    "content/en/compiler/community",
    "content/en/compiler/governance",
]

# 字面量事实 lint 的**例外** —— 文档层里的**历史**版本引用。
#
# 「v4.1.5 已修」说的是「某个版本修的某件事」：把它换成 {{site_version}} 等于把
# 历史改成当前（下一个版本发布后那句话就会变成假的）。所以这些地方必须逐字保留。
# 每条都带理由，且按「文件 + 上下文正则」限定 —— 不是把整个文件的版本号放行。
FACT_LINT_EXCEPTIONS = [
    ("content/compiler/docs/arena.md", r"v4\.1\.5"),
    ("content/en/compiler/docs/arena.md", r"v4\.1\.5"),
    ("content/compiler/docs/osdev.md", r"v4\.1\.5"),
    ("content/en/compiler/docs/osdev.md", r"v4\.1\.5"),
    ("content/compiler/governance/index.md", r"v4\.0\.0-rc1"),
    ("content/en/compiler/governance/index.md", r"v4\.0\.0-rc1"),
]

# 事实字面量 —— **从 siteconfig.FACTS 派生**，这里只声明「哪个事实 +
# 它在正文里长什么样」。
#
# ⚠️ 上一版这里写死了一串字面量（"4.1.4" / "279" / "299" …）⇒ 编译器仓把版本
# 刷到 4.1.5、回归数改成 281 之后，这张表**只抓得到旧数字、抓不到新数字** ——
# 等于放了几个月的空门。手写的清单必然随版本漂，值必须现算。
#
# 后缀是上下文：裸数字（"20"、"8"）在正文里太常见，只按「数字 + 后缀」匹配。
LITERAL_FACT_PATTERNS = [
    # (事实键, 正文里的后缀)
    #
    # ⚠️ 后缀是**按语言写死**的：中文「281 PASS / 301 条 / 8 个模块」，
    # 英文「281 PASS / 301 in total / 8 modules」。只写中文后缀 ⇒ 英文页的数字
    # 事实没人管（2026-11-10 扩到文档层时发现）。所以两种语言的后缀都列，
    # 写页面时按哪套说法就用哪条。
    ("site_version", ""),
    ("spec_version", ""),
    ("abi_version", ""),
    ("binary_format_version", ""),
    ("ide_version", ""),
    ("regress_pass", " PASS"),
    ("regress_skip", " SKIP"),
    ("regress_total", " 条"),
    ("regress_total", " in total"),
    ("regress_total", " cases"),
    ("assertions", " 条"),
    ("assertions", " assertions"),
    ("artifact_checks", " 道"),
    ("artifact_checks", " checks"),
    ("artifact_checks", " PASS"),
    ("workarounds_total", " 条"),
    ("workarounds_total", " entries"),
    ("ide_gate_pass", "/"),
    ("stdlib_modules", " 个模块"),
    ("stdlib_modules", " modules"),
]

# ── 路由工具 ──────────────────────────────────────────────────────────────
# route = 去掉语言段与后缀后的相对路径。
#   content/index.html              → "index"
#   content/compiler/docs/tour.md  → "compiler/docs/tour"
#   content/en/compiler/index.html  → "compiler/index"


def lang_of(rel: str) -> str:
    """由源文件相对路径判定语言。`en/` 开头 = 英文。"""
    return "en" if rel == "en" or rel.startswith("en/") else "zh"


def route_of(rel: str) -> str:
    """由源文件相对路径算出 route（跨语言同一 route 即孪生页）。"""
    parts = rel.split("/")
    if parts and parts[0] == "en":
        parts = parts[1:]
    name = parts[-1] if parts else ""
    if name.endswith(".md"):
        name = name[:-3]
    elif name.endswith(".html"):
        name = name[:-5]
    return "/".join(parts[:-1] + [name]) if len(parts) > 1 else name


def is_exempt(route: str) -> bool:
    """route 是否在「本轮只做中文」的豁免名单里。"""
    return any(route.startswith(p) for p in TWIN_EXEMPT_PREFIXES)
