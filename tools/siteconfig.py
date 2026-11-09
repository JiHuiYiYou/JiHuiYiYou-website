"""JHYY 官网站点配置 —— 全站唯一真相源。

**这里出现的版本号是全站唯一一处。** 以前官网散落着 1.8.3、spec v1.3.0、
ABI v1.0.0、两个不同的安装包体积，改一次要动十几个字符串——那是 1.8.3 页面
在 4.1.4 时代还挂着的根因。现在改这里，全站跟着改。

改版本号后跑 `python tools/build.py` 重新生成。
"""

from __future__ import annotations

# ── 版本闸门 ────────────────────────────────────────────────────────────────

SITE_VERSION = "4.1.5"
SITE_VERSION_DATE = "2026-11-09"
SPEC_VERSION = "4.0.0"
# 规范文档头部原文是「随 v4.0.0 final promote 一同锁版」——**没有写具体日期**。
# 编译器 README 写的是 "(locked 2026-10-24)"，但那个日期在规范文档里的实际含义是
# 「v1.3.0 与 17 份 supplement 归档进 git 历史」的日期。两处口径不一致，所以官网
# 只写「locked」，不编一个精确日期。
SPEC_LOCK_NOTE = "locked"
ABI_VERSION = "4.0.0"
BINARY_FORMAT_VERSION = "1.0.0"
IDE_VERSION = "0.2.1"
IDE_VERSION_DATE = "2026-10-30"

ORG = "JiHuiYiYou"
ORG_SITE = "https://github.com/JiHuiYiYou"

# ── 编译器状态数字（全部来自 docs/internal/FACTS.md） ────────────────────────

REGRESS_TOTAL = 301
REGRESS_PASS = 281
REGRESS_SKIP = 20
REGRESS_FAILED = 0
ASSERTIONS = 217
# 产物级门数 —— 真相源是编译器仓的 docs/internal/FACTS.md § 2.1。
# 这个数已经漂过两次：19 → 20（#[naked] 补门）→ 21。官网曾经一直跟着旧数走，
# 而没有任何门会红；现在 check_facts.py 每次都跟编译器仓对拍。
ARTIFACT_CHECKS = 21
BENCH_TASKS = 9
BENCH_AXES = 4

WORKAROUNDS_TOTAL = 220
WORKAROUNDS_ACTIVE = 0
WORKAROUNDS_DEFERRED = 1
WORKAROUNDS_RESOLVED = 197
WORKAROUNDS_SUPERSEDED = 19
WORKAROUNDS_INVALID = 3

# ── 事实占位符（两种语言共用这一份） ──────────────────────────────────────
# 正文里写 {{key}}，构建器替换 —— **任何语言都拿不到第二份数字**。
# 改数字只改这里；tools/check_facts.py 负责跟编译器仓的 FACTS.md 对拍。
#
# 值里不许出现 markdown 活跃字符（* _ ` [ ] | < >），否则替换后的正文会被
# mdrender 二次解释。构建器会当场拒绝。
FACTS = {
    # 版本
    "site_version": SITE_VERSION,
    "site_version_date": SITE_VERSION_DATE,
    "spec_version": SPEC_VERSION,
    "spec_lock_note": SPEC_LOCK_NOTE,
    "abi_version": ABI_VERSION,
    "binary_format_version": BINARY_FORMAT_VERSION,
    "ide_version": IDE_VERSION,
    "ide_version_date": IDE_VERSION_DATE,
    # 编译器状态
    "regress_total": REGRESS_TOTAL,
    "regress_pass": REGRESS_PASS,
    "regress_skip": REGRESS_SKIP,
    "regress_failed": REGRESS_FAILED,
    "assertions": ASSERTIONS,
    "artifact_checks": ARTIFACT_CHECKS,
    "bench_tasks": BENCH_TASKS,
    "bench_axes": BENCH_AXES,
    "workarounds_total": WORKAROUNDS_TOTAL,
    "workarounds_active": WORKAROUNDS_ACTIVE,
    "workarounds_deferred": WORKAROUNDS_DEFERRED,
    "workarounds_resolved": WORKAROUNDS_RESOLVED,
    "workarounds_superseded": WORKAROUNDS_SUPERSEDED,
    "workarounds_invalid": WORKAROUNDS_INVALID,
    "targets_count": 4,
    "stdlib_modules": 8,
    # 编译器 C 宿主时代（v1.8.3）那批已作废的 ABI 版本 —— **历史引用**，
    # 不是当前契约。OS 页在讲「旧设计稿写于什么时候」时会提到它。
    "legacy_abi_version": "1.0.0",
    # IDE —— 来源：JiHuiYiYou-IDE README「一致性门」一节（IDE 仓自己的口径）
    "ide_gate_pass": 277,
    "ide_gate_total": 277,
    # OS —— 来源：JiHuiYiYou-OS spike/boot.s 头部注释「实测到的四件事」
    "os_spike_measured": 4,
    # for-VEX —— 来源：JiHuiYiYou-for-VEX docs/00-事实基线.md（八件事，八件全部实测）
    # 2026-11-10 订正：最后一件（消息泵 tick 频率）已在真 Brain 上测得（100 Hz，
    # 2026-11-09）⇒ 八件全部有结论。**仍待测的是八项之外的屏显细节**
    # （bOpaque 语义、文字坐标单位）—— 那是两件事，不是一个数，所以不占 fact。
    "vex_baseline_total": 8,
    "vex_baseline_done": 8,
}

# ── 分发产物 ────────────────────────────────────────────────────────────────

ARTIFACTS = [
    {
        "name": f"jhyy-installer-{SITE_VERSION}.exe",
        "kind": "GUI 安装器",
        "size": "~55 MB",
        "note": "编译器 + .jhyy 文件关联 + VS Code 扩展 + PATH + 内置 ucrt64 工具链",
        "primary": True,
    },
    {
        "name": f"jhyy-compiler-{SITE_VERSION}.msi",
        "kind": "MSI（企业分发）",
        "size": "~28 MB",
        "note": "同样的载荷，无 GUI 向导；适合 SCCM / Intune / 组策略",
        "primary": False,
    },
    {
        "name": f"jhyy-lang-{SITE_VERSION}.vsix",
        "kind": "VS Code 扩展",
        "size": "~11 KB",
        "note": "语法高亮 + Run/Compile 命令（不含调试器、LSP server、IntelliSense、hover 文档）",
        "primary": False,
    },
]

CODE_SIGNING_NOTE = (
    "安装器和 MSI **都没有代码签名**。Windows SmartScreen 首次运行会弹"
    "「Windows 已保护你的电脑」，点「更多信息 → 仍要运行」。"
    "未签名二进制也更容易被第三方杀软拦。企业分发策略可能直接拒收未签名 MSI。"
)

# ── 目标三元组 ──────────────────────────────────────────────────────────────

TARGETS = [
    {
        "triple": "amd64_win",
        "abi": "MS x64",
        "output": "PE/COFF 可执行文件",
        "status": "stable",
        "note": "宿主默认目标。编译器自身就跑在这个目标上。",
    },
    {
        "triple": "amd64_sysv",
        "abi": "SysV AMD64",
        "output": "SysV 汇编（.s）→ 外部 ld 链成 ELF",
        "status": "stable",
        "note": "产物是汇编文本，链接由外部 linker 完成。",
    },
    {
        "triple": "amd64_win_freestanding",
        "abi": "MS x64",
        "output": "UEFI 可执行映像",
        "status": "beta",
        # 注意：freestanding 只切「调用约定归属 + 入口钩子」，**不切链接方式**——
        # 链接行是按源文件里有没有 `#[no_std]` 分支的，跟 `--target` 无关。
        # （ABI v4.0.0 § 1 / § 7）
        "note": "freestanding 只切调用约定归属与入口钩子，不切链接方式。UEFI 入口路径尚未完工（ABI § 12.8）。",
    },
    {
        "triple": "amd64_sysv_freestanding",
        "abi": "SysV AMD64",
        "output": "freestanding 汇编（.s）",
        "status": "beta",
        "note": "裸机内核的主要入口目标。同上，UEFI 入口路径尚未完工。",
    },
]

# ── 四个项目 ────────────────────────────────────────────────────────────────

PROJECTS = [
    {
        "key": "compiler",
        "name": "编译器",
        "en": "Compiler",
        "path": "/compiler/",
        "version": SITE_VERSION,
        "version_date": SITE_VERSION_DATE,
        "tagline": "自举的系统编程语言编译器",
        "tagline_en": "The self-hosted systems language compiler",
        "desc": "用 JHYY 写的 JHYY 编译器。后端是自研 amd64 发射器，不是 LLVM，也不是 vendor 进来的 QBE。",
        "desc_en": "The JHYY compiler, written in JHYY. The backend is a self-written amd64 emitter — not LLVM, and not a vendored QBE.",
        "repo": f"{ORG_SITE}/JiHuiYiYou-compiler",
        "status": "stable",
        "status_label": "稳定",
        "status_label_en": "Stable",
    },
    {
        "key": "ide",
        "name": "IDE",
        "en": "IDE",
        "path": "/ide/",
        "version": IDE_VERSION,
        "version_date": IDE_VERSION_DATE,
        "tagline": "拖块编程 + 文本编辑 + Claude Code",
        "tagline_en": "Block programming + text editing + Claude Code",
        "desc": "桌面工作台。Blockly 积木和 CodeMirror 文本共享同一棵 AST——改一边，另一边跟着变。",
        "desc_en": "A desktop workbench. Blockly blocks and CodeMirror text share one AST — change one, the other follows.",
        "repo": f"{ORG_SITE}/JiHuiYiYou-IDE",
        "status": "beta",
        "status_label": "测试中",
        "status_label_en": "Beta",
    },
    {
        "key": "os",
        "name": "OS",
        "en": "OS",
        "path": "/os/",
        "version": "spike",
        "version_date": "",
        "tagline": "用 JHYY 写的操作系统",
        "tagline_en": "An operating system written in JHYY",
        "desc": "设计基线正在重整。当前落地的只有 UEFI x64 引导 spike——把「能不能启动」这件事先变成实测值。",
        "desc_en": "The design baseline is being rebuilt. All that exists today is a UEFI x64 boot spike — turning “can it boot?” into a measured value first.",
        "repo": f"{ORG_SITE}/JiHuiYiYou-OS",
        "status": "incubating",
        "status_label": "孵化中",
        "status_label_en": "Incubating",
    },
    {
        "key": "vex",
        "name": "for-VEX",
        "en": "for-VEX",
        "path": "/vex/",
        "version": "day-0",
        "version_date": "2026-11-08",
        "tagline": "把 JHYY 编译到 VEX V5 Brain",
        "tagline_en": "Compiling JHYY to the VEX V5 Brain",
        "desc": "嵌入式目标：Xilinx Zynq / Cortex-A9。路线是 JHYY 直出 ARM 机器码，链官方 SDK 出 .bin。",
        "desc_en": "An embedded target: Xilinx Zynq / Cortex-A9. The route is JHYY emitting ARM machine code directly, linked against the official SDK into a .bin.",
        "repo": f"{ORG_SITE}/JiHuiYiYou-for-VEX",
        "status": "incubating",
        "status_label": "孵化中",
        "status_label_en": "Incubating",
    },
]

# ── 编译器五区导航 ──────────────────────────────────────────────────────────
# 每项带 label_en —— 门脸层与文档层的导航都要出英文版。
# 标签里的 {key} 由 FACTS 填充（版本号不许手写，见 FACTS）。

COMPILER_NAV = [
    {"key": "home", "label": "首页", "label_en": "Home", "href": "/compiler/"},
    {"key": "docs", "label": "文档", "label_en": "Docs", "href": "/compiler/docs/"},
    {"key": "download", "label": "下载", "label_en": "Download", "href": "/compiler/download/"},
    {"key": "community", "label": "社区", "label_en": "Community", "href": "/compiler/community/"},
    {"key": "governance", "label": "治理", "label_en": "Governance", "href": "/compiler/governance/"},
]

# 各项目自己的分栏（IDE / OS / VEX 页面用）
# 这三个项目还早，站内没有成套文档——正文入口直接指向各自仓库里的真实文档，
# 别为了凑导航栏造一个空的站内页面。
PROJECT_NAV = {
    "ide": [
        {"key": "ide", "label": "概览", "label_en": "Overview", "href": "/ide/"},
        {"label": "文档", "label_en": "Docs", "href": f"{ORG_SITE}/JiHuiYiYou-IDE/tree/main/docs/wiki"},
        {"label": "Releases", "label_en": "Releases", "href": f"{ORG_SITE}/JiHuiYiYou-IDE/releases"},
    ],
    "os": [
        {"key": "os", "label": "概览", "label_en": "Overview", "href": "/os/"},
        {"label": "Spike", "label_en": "Spike", "href": f"{ORG_SITE}/JiHuiYiYou-OS/tree/main/spike"},
    ],
    "vex": [
        {"key": "vex", "label": "概览", "label_en": "Overview", "href": "/vex/"},
        {"label": "事实基线", "label_en": "Fact baseline", "href": f"{ORG_SITE}/JiHuiYiYou-for-VEX/blob/main/docs/00-%E4%BA%8B%E5%AE%9E%E5%9F%BA%E7%BA%BF.md"},
    ],
}

# ── 文档侧栏 ────────────────────────────────────────────────────────────────
# items 的每一项是 (中文标签, English label, href)；href 为 None 表示纯文本项。
# 标签里的 {key} 由 FACTS 填充。

DOC_SIDEBAR = [
    {
        "title": "上手",
        "title_en": "Getting started",
        "items": [
            ("快速上手", "Getting started", "/compiler/docs/getting-started.html"),
            ("语言导览", "Language tour", "/compiler/docs/tour.html"),
        ],
    },
    {
        "title": "语言参考",
        "title_en": "Language reference",
        "items": [
            ("参考总览", "Reference overview", "/compiler/docs/reference.html"),
            ("语言规范 v{spec_version}", "Language spec v{spec_version}", "/compiler/docs/spec.html"),
            ("ABI v{abi_version}", "ABI v{abi_version}", "/compiler/docs/abi.html"),
            ("标准库", "Standard library", "/compiler/docs/stdlib.html"),
        ],
    },
    {
        "title": "专项指南",
        "title_en": "Deep dives",
        "items": [
            ("Arena 内存管理", "Arena memory management", "/compiler/docs/arena.html"),
            ("裸机与内核开发", "Bare metal and kernel development", "/compiler/docs/osdev.html"),
        ],
    },
    {
        "title": "工具与实现",
        "title_en": "Tools and internals",
        "items": [
            ("CLI 参考", "CLI reference", "/compiler/docs/cli.html"),
            ("编译器实现", "How the compiler works", "/compiler/docs/compiler.html"),
            ("构建与测试", "Build and test", "/compiler/docs/build-and-test.html"),
            ("常见问题", "FAQ", "/compiler/docs/faq.html"),
        ],
    },
]

DOWNLOAD_SIDEBAR = [
    {
        "title": "下载",
        "title_en": "Download",
        "items": [
            ("下载首页", "Download home", "/compiler/download/index.html"),
            ("目标与交叉编译", "Targets and cross-compilation", "/compiler/download/targets.html"),
            ("源码构建与自举", "Build from source and bootstrap", "/compiler/download/bootstrap.html"),
            ("校验与签名", "Verification and signing", "/compiler/download/verify.html"),
        ],
    },
    {
        "title": "产物",
        "title_en": "Artifacts",
        "items": [
            ("安装器（GUI）", "Installer (GUI)", "/compiler/download/index.html#installer"),
            ("MSI（企业分发）", "MSI (enterprise)", "/compiler/download/index.html#msi"),
            ("VS Code 扩展", "VS Code extension", "/compiler/download/index.html#vsix"),
            ("包管理器", "Package managers", "/compiler/download/index.html#pkgmgr"),
        ],
    },
    {
        "title": "版本",
        "title_en": "Versions",
        "items": [
            ("v{site_version}（当前稳定）", "v{site_version} (current stable)", "/compiler/download/index.html#current"),
            ("历史归档", "Archive", "/compiler/download/index.html#archive"),
        ],
    },
]

COMMUNITY_SIDEBAR = [
    {
        "title": "社区",
        "title_en": "Community",
        "items": [
            ("社区首页", "Community home", "/compiler/community/index.html"),
            ("行为准则", "Code of conduct", "/compiler/community/conduct.html"),
            ("贡献指南", "Contributing", "/compiler/community/contributing.html"),
            ("安全披露", "Security disclosure", "/compiler/community/security.html"),
        ],
    },
    {
        "title": "参与方式",
        "title_en": "How to take part",
        "items": [
            ("提 Issue", "Open an issue", "https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/issues"),
            ("提 PR", "Open a PR", "https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/pulls"),
            ("QQ 群 429807125", "QQ group 429807125", None),
            ("代码所有权", "Code ownership", "/compiler/governance/repo-map.html"),
        ],
    },
]

GOVERNANCE_SIDEBAR = [
    {
        "title": "治理",
        "title_en": "Governance",
        "items": [
            ("治理总览", "Governance overview", "/compiler/governance/index.html"),
            ("许可证", "License", "/compiler/governance/license.html"),
            ("仓库地图", "Repository map", "/compiler/governance/repo-map.html"),
        ],
    },
    {
        "title": "流程",
        "title_en": "Process",
        "items": [
            ("RFC 流程", "RFC process", "/compiler/governance/index.html#rfc"),
            ("发布节奏", "Release cadence", "/compiler/governance/index.html#release"),
            ("贡献指南", "Contributing", "/compiler/community/contributing.html"),
        ],
    },
]

# zone → 侧栏。docs / download / community / governance 各自一组。
ZONE_SIDEBARS = {
    "docs": DOC_SIDEBAR,
    "download": DOWNLOAD_SIDEBAR,
    "community": COMMUNITY_SIDEBAR,
    "governance": GOVERNANCE_SIDEBAR,
}

# ── 文档页的元信息（用于生成「编辑此页」和面包屑） ──────────────────────────

DOC_SOURCE_REPO = f"{ORG_SITE}/JiHuiYiYou-compiler"

# ── 编译器标准库模块 ─────────────────────────────────────────────────────────

STDLIB_MODULES = [
    ("arena", "Arena 分配器：init / alloc / calloc / reset / free", "/compiler/docs/arena.html"),
    ("mem", "内存操作：拷贝、清零、比较", None),
    ("string", "UTF-8 字符串：切分、拼接、查找、格式化", None),
    ("vec", "动态数组：push / pop / 索引 / 容量", None),
    ("fmt", "格式化输出：整数、浮点、指针", None),
    ("io", "标准输入输出：文件句柄、读写、缓冲", None),
    ("math", "数学函数：三角、对数、取模", None),
    ("os", "操作系统接口：进程、文件、时间、环境变量", None),
]

# ── `[[Wiki 链接]]` 解析表 ───────────────────────────────────────────────────

WIKI_LINKS = {
    # 英文 wiki（来自 jhyy-wiki-work）
    "Home": "/compiler/docs/index.html",
    "Getting-Started": "/compiler/docs/getting-started.html",
    "Language-Tour": "/compiler/docs/tour.html",
    "Build-and-Test": "/compiler/docs/build-and-test.html",
    "Architecture": "/compiler/docs/compiler.html",
    "FAQ": "/compiler/docs/faq.html",
    # 中文 wiki
    "首页": "/compiler/docs/index.html",
    "快速上手": "/compiler/docs/getting-started.html",
    "语言导览": "/compiler/docs/tour.html",
    "构建与测试": "/compiler/docs/build-and-test.html",
    "架构": "/compiler/docs/compiler.html",
    "常见问题": "/compiler/docs/faq.html",
}
