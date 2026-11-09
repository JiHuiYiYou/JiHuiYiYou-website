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

# 豁免前缀 —— 这些 route 目前只有中文。**下一轮删掉这四行**，
# 门逻辑一行不用动（规则是前缀驱动的）。
TWIN_EXEMPT_PREFIXES = [
    "compiler/docs/",
    "compiler/download/",
    "compiler/community/",
    "compiler/governance/",
]

# ── 字面量事实 lint 的契约 ────────────────────────────────────────────────
# 这些字符串在本站没有别的含义 ⇒ 出现在正文里几乎一定是「手写了事实」。
# 扫到就报「用 {{key}} 占位符代替」。
#
# 扫描范围：本轮 = 5 页门脸（中英各一版）。文档层下一轮有英文孪生时，
# 把范围扩到那里 —— 那时这些页面的硬编码事实会一并被逼成占位符。
FACT_LINT_SCOPE = [
    "content/index.html",
    "content/en/index.html",
    "content/compiler/index.html",
    "content/en/compiler/index.html",
    "content/ide/index.md",
    "content/en/ide/index.md",
    "content/os/index.md",
    "content/en/os/index.md",
    "content/vex/index.md",
    "content/en/vex/index.md",
]

# 特征字面量 → 对应的占位符键（键只用于报错文案，不参与替换）。
LITERAL_FACTS = {
    "4.1.4": "site_version",
    "4.0.0": "spec_version / abi_version",
    "1.0.0": "binary_format_version",
    "0.2.1": "ide_version",
    "279": "regress_pass",
    "299": "regress_total",
    "217": "workarounds_total",
    "215": "assertions",
    "277": "ide_gate_pass",
    "20 SKIP": "regress_skip",
    "8 个模块": "stdlib_modules",
    "20 道": "artifact_checks",
    "20 PASS": "artifact_checks",
    "19 PASS": "artifact_checks",
    "19 道": "artifact_checks",
}

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
