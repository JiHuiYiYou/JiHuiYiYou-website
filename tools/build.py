#!/usr/bin/env python3
"""JHYY 官网静态生成器 —— 零第三方依赖。

    python tools/build.py            # 全量生成
    python tools/build.py --check    # 只检查链接与事实，不写文件

设计约束（来自改版报告 §8「不要押注单一重型框架」）：
  * 长文用 Markdown 源（content/），生成静态 HTML
  * 首页 / 下载矩阵是数据驱动（tools/siteconfig.py）
  * 标准库签名等「编译器才知道的事实」由编译器 CI 注入 JSON，本生成器只做聚合
  * 不混用 Markdown 方言：全站只用 CommonMark 子集，渲染器见 tools/mdrender.py
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import siteconfig as C  # noqa: E402
from mdrender import Renderer, render_inline, slugify  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
TOOLS = ROOT / "tools"

# 每次生成都清掉的输出目录（只清我们自己产出的那几个）
OUTPUT_ROOTS = ("compiler", "ide", "os", "vex", "docs")


# ── 工具 ────────────────────────────────────────────────────────────────────

def rel_prefix(out_path: Path) -> str:
    """输出文件所在目录到站点根的相对前缀。"""
    rel = out_path.relative_to(ROOT)
    depth = len(rel.parts) - 1
    return "../" * depth


def normalize_href(href: str) -> str:
    """目录式 URL 补成显式 index.html —— Pages / file:// / 裸静态托管都能用。"""
    if href.endswith("/"):
        return href + "index.html"
    return href


def rewrite_links(html_text: str, prefix: str) -> str:
    """把根绝对链接（/compiler/...）改写成相对链接。

    站点可能挂在 user.github.io/<repo>/ 下，纯根绝对路径会 404；
    相对路径在任何前缀下都成立。depth 0 时 prefix 为空串，
    于是 "/assets/x" → "assets/x"——同样成立。
    """
    return re.sub(r'(?<![-\w])(href|src|data)="/', rf'\1="{prefix}', html_text)


def slug_of(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1] or "index"


# ── front matter ────────────────────────────────────────────────────────────

def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    meta: dict = {}
    for line in raw.split("\n"):
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


# ── 导航 / 页脚 ─────────────────────────────────────────────────────────────

def project_switcher(active: str) -> str:
    """项目切换器 —— 纯 HTML/CSS 的下拉（<details>），不依赖 JS。"""
    cur = next((p for p in C.PROJECTS if p["key"] == active), None)
    label = cur["name"] if cur else "全部项目"
    items = []
    for p in C.PROJECTS:
        state = " is-active" if p["key"] == active else ""
        items.append(
            f'<a class="proj-item{state}" href="{normalize_href(p["path"])}">'
            f'<span class="proj-item-name">{html.escape(p["name"])}</span>'
            f'<span class="proj-item-en">{html.escape(p["en"])}</span>'
            f'<span class="proj-item-tag">{html.escape(p["tagline"])}</span>'
            f"</a>"
        )
    return (
        '<details class="proj-switch">'
        f'<summary class="proj-summary"><span class="proj-dot" aria-hidden="true"></span>'
        f'{html.escape(label)}<span class="proj-caret" aria-hidden="true">▾</span></summary>'
        f'<div class="proj-menu" role="navigation" aria-label="机会翼游家族">{"".join(items)}</div>'
        "</details>"
    )


def zone_nav(items: list[dict], active: str | None) -> str:
    links = []
    for it in items:
        cur = " is-active" if it.get("key") == active or it["href"] == active else ""
        links.append(f'<a class="{cur.strip()}" href="{normalize_href(it["href"])}">{html.escape(it["label"])}</a>')
    return '<div class="nav-links" role="navigation">' + "".join(links) + "</div>"


GITHUB_ICON = (
    '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" '
    'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7'
    'A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0'
    'C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7'
    'A3.37 3.37 0 0 0 9 18.13V22"/></svg>'
)

ARROW_ICON = (
    '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M7 17 L17 7 M9 7 L17 7 L17 15"/></svg>'
)


def dark_nav(project: str, zone: str | None, prefix: str) -> str:
    """门脸层导航（深色玻璃胶囊）。所有非文档页共用。"""
    if project == "compiler":
        nav = C.COMPILER_NAV
        repo = C.PROJECTS[0]["repo"]
    elif project == "home":
        nav = []
        repo = C.ORG_SITE
    else:
        nav = C.PROJECT_NAV.get(project, [])
        repo = next((p["repo"] for p in C.PROJECTS if p["key"] == project), C.ORG_SITE)
    return f"""
  <nav class="floating-nav" aria-label="Primary">
    <div class="nav-pill">
      <a href="{prefix}index.html" class="nav-logo" aria-label="机会翼游 · JHYY 首页">
        <img src="{prefix}assets/img/jhyy-logo.png" class="logo-img" height="30" alt="机会翼游 · JHYY" />
      </a>
      {project_switcher(project)}
      {zone_nav(nav, zone)}
      <div class="nav-cta-group">
        <a href="{repo}" class="nav-icon-btn" aria-label="GitHub">{GITHUB_ICON}</a>
        <a href="{normalize_href('/compiler/download/')}" class="nav-cta magnetic" data-magnetic>
          <span>下载 v{C.SITE_VERSION}</span>
          <span class="btn-icon-wrap">{ARROW_ICON}</span>
        </a>
      </div>
    </div>
  </nav>
"""


def docs_nav(project: str, prefix: str, zone: str | None = None) -> str:
    """文档层顶栏（浅色、信息密集）。"""
    nav = C.COMPILER_NAV
    repo = C.PROJECTS[0]["repo"]
    links = []
    for it in nav:
        cur = " is-active" if it.get("key") == zone else ""
        links.append(f'<a class="{cur.strip()}" href="{normalize_href(it["href"])}">{html.escape(it["label"])}</a>')
    return f"""
  <header class="doc-topbar">
    <div class="doc-topbar-inner">
      <a href="{prefix}index.html" class="doc-brand" aria-label="机会翼游 · JHYY 首页">
        <img src="{prefix}assets/img/jhyy-logo.png" alt="机会翼游 · JHYY" />
        <span class="doc-brand-name">JHYY</span>
      </a>
      {project_switcher("compiler")}
      <nav class="doc-zones" aria-label="主导航">{"".join(links)}</nav>
      <div class="doc-topbar-right">
        <button class="doc-search-btn" type="button" data-search-open data-search-index="{prefix}search-index.json" aria-label="搜索文档">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
          <span>搜索文档</span><kbd>/</kbd>
        </button>
        <span class="doc-version" title="最新稳定版">v{C.SITE_VERSION}</span>
        <a href="{repo}" class="doc-gh" aria-label="GitHub">{GITHUB_ICON}</a>
      </div>
    </div>
  </header>
"""


def footer(project: str, prefix: str) -> str:
    repo = C.PROJECTS[0]["repo"]
    proj_links = "".join(
        f'<li><a href="{normalize_href(p["path"])}">{html.escape(p["name"])}'
        f'<span class="foot-sub">{html.escape(p["en"])}</span></a></li>'
        for p in C.PROJECTS
    )
    return f"""
  <footer class="site-foot">
    <div class="container foot-grid">
      <div class="foot-brand">
        <a href="{prefix}index.html" class="nav-logo foot-logo">
          <img src="{prefix}assets/img/jhyy-logo.png" class="logo-img logo-img--foot" alt="机会翼游 · JHYY" />
        </a>
        <p class="foot-tag">机会翼游家族 · 编译器 / IDE / OS / for-VEX</p>
      </div>
      <div class="foot-cols">
        <div class="foot-col">
          <h4 class="foot-h">家族</h4>
          <ul>{proj_links}</ul>
        </div>
        <div class="foot-col">
          <h4 class="foot-h">编译器</h4>
          <ul>
            <li><a href="{normalize_href('/compiler/docs/')}">文档</a></li>
            <li><a href="{normalize_href('/compiler/download/')}">下载</a></li>
            <li><a href="{normalize_href('/compiler/community/')}">社区</a></li>
            <li><a href="{normalize_href('/compiler/governance/')}">治理</a></li>
          </ul>
        </div>
        <div class="foot-col">
          <h4 class="foot-h">仓库</h4>
          <ul>
            <li><a href="{repo}">Compiler</a></li>
            <li><a href="{C.ORG_SITE}/JiHuiYiYou-IDE">IDE</a></li>
            <li><a href="{C.ORG_SITE}/JiHuiYiYou-OS">OS</a></li>
            <li><a href="{C.ORG_SITE}/JiHuiYiYou-for-VEX">for-VEX</a></li>
          </ul>
        </div>
        <div class="foot-col">
          <h4 class="foot-h">规范</h4>
          <ul>
            <li><a href="{C.DOC_SOURCE_REPO}/blob/main/docs/abis/jhyy-lang-spec-v{C.SPEC_VERSION}.md">语言规范 v{C.SPEC_VERSION}</a></li>
            <li><a href="{C.DOC_SOURCE_REPO}/blob/main/docs/abis/jhyy-abi-v{C.ABI_VERSION}.md">ABI v{C.ABI_VERSION}</a></li>
            <li><a href="{C.DOC_SOURCE_REPO}/blob/main/docs/abis/jhyy-binary-format-v{C.BINARY_FORMAT_VERSION}.md">二进制格式 v{C.BINARY_FORMAT_VERSION}</a></li>
            <li><a href="{C.DOC_SOURCE_REPO}/blob/main/CHANGELOG.md">变更日志</a></li>
          </ul>
        </div>
        <div class="foot-col">
          <h4 class="foot-h">社区</h4>
          <ul>
            <li><span class="foot-text-strong">QQ 群 429807125</span><button class="ci-copy ci-copy--inline ci-copy--foot" type="button" aria-label="复制 QQ 群号" data-copy-text="429807125"></button></li>
            <li><a href="{repo}/issues">Issues</a></li>
            <li><a href="{repo}/blob/main/CONTRIBUTING.md">贡献指南</a></li>
            <li><a href="{normalize_href('/compiler/community/security.html')}">安全披露</a></li>
          </ul>
        </div>
      </div>
    </div>
    <div class="foot-bar">
      <div class="container foot-bar-row">
        <span class="foot-copy">© 2026 机会翼游 · MIT License</span>
        <div class="foot-status">
          <span class="status-led"></span>
          <span>v{C.SITE_VERSION} · spec v{C.SPEC_VERSION} · main</span>
        </div>
      </div>
    </div>
  </footer>
"""


# ── 布局 ────────────────────────────────────────────────────────────────────

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1'
    '&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700'
    '&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />'
)


def head(meta: dict, prefix: str, layout: str, extra_css: str = "") -> str:
    title = meta.get("title", "机会翼游 · JHYY")
    desc = meta.get("description", "")
    css = "assets/css/docs.css" if layout == "docs" else "assets/css/main.css"
    extra = ""
    if layout == "docs":
        extra = '<link rel="stylesheet" href="{p}assets/css/main.css" />'.format(p=prefix)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#050505" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc, quote=True)}" />
  <meta property="og:title" content="{html.escape(title, quote=True)}" />
  <meta property="og:description" content="{html.escape(desc, quote=True)}" />
  <meta property="og:type" content="website" />
  {FONTS}
  <link rel="stylesheet" href="{prefix}{css}" />
  {extra}
  <link rel="icon" type="image/png" sizes="any" href="{prefix}assets/img/jhyy-icon.png" />
</head>
"""


def render_docs_layout(meta: dict, body: str, prefix: str, out_path: Path, headings: list) -> str:
    """文档层：三栏（左 TOC / 中内容 / 右锚点）。"""
    zone = meta.get("zone", "docs")
    groups = C.ZONE_SIDEBARS.get(zone, C.DOC_SIDEBAR)
    self_url = meta.get("self", "")
    sidebar = []
    for group in groups:
        items = []
        for label, href in group["items"]:
            if not href:
                items.append(f'<li><span class="doc-nav-text">{html.escape(label)}</span></li>')
                continue
            if href.startswith("http"):
                items.append(f'<li><a href="{href}" target="_blank" rel="noopener">{html.escape(label)} ↗</a></li>')
                continue
            cur = " is-active" if normalize_href(href) == normalize_href(self_url) else ""
            items.append(f'<li><a class="{cur.strip()}" href="{normalize_href(href)}">{html.escape(label)}</a></li>')
        sidebar.append(
            f'<div class="doc-nav-group"><h4>{html.escape(group["title"])}</h4><ul>{"".join(items)}</ul></div>'
        )

    anchors = []
    for level, text, slug in headings:
        if level > 3:
            continue
        anchors.append(
            f'<a class="anchor-l{level}" href="#{slug}">{html.escape(re.sub(r"[`*]", "", text))}</a>'
        )

    onthis = (
        '<nav class="doc-anchors" aria-label="本页目录"><h4>本页</h4>'
        + "".join(anchors)
        + "</nav>"
        if anchors
        else ""
    )

    edit = meta.get("edit")
    edit_html = (
        f'<a class="doc-edit" href="{edit}" target="_blank" rel="noopener">编辑此页 ↗</a>' if edit else ""
    )

    external = ""
    if zone == "docs":
        external = f"""
    <div class="doc-nav-group doc-nav-external">
      <h4>规范原文</h4>
      <ul>
        <li><a href="{C.DOC_SOURCE_REPO}/blob/main/docs/abis/jhyy-lang-spec-v{C.SPEC_VERSION}.md" target="_blank" rel="noopener">语言规范 v{C.SPEC_VERSION} ↗</a></li>
        <li><a href="{C.DOC_SOURCE_REPO}/blob/main/docs/abis/jhyy-abi-v{C.ABI_VERSION}.md" target="_blank" rel="noopener">ABI v{C.ABI_VERSION} ↗</a></li>
        <li><a href="{C.DOC_SOURCE_REPO}/blob/main/docs/internal/workarounds.md" target="_blank" rel="noopener">问题台账 ↗</a></li>
      </ul>
    </div>"""

    return f"""{head(meta, prefix, "docs")}
<body class="doc-body">
{docs_nav("compiler", prefix, zone)}
<div class="doc-shell">
  <aside class="doc-sidebar" aria-label="文档目录">
    {''.join(sidebar)}
    {external}
  </aside>
  <main class="doc-main" id="main">
    <div class="doc-article">
      {body}
      <div class="doc-foot-row">
        {edit_html}
        <a href="https://github.com/{C.ORG}/JiHuiYiYou-website/issues/new" target="_blank" rel="noopener">报告问题 ↗</a>
      </div>
    </div>
  </main>
  {onthis}
</div>
{footer("compiler", prefix)}
<script src="{prefix}assets/js/docs.js" defer></script>
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({{ startOnLoad: true, theme: "neutral", securityLevel: "loose" }});
</script>
</body>
</html>
"""


def render_page_layout(meta: dict, body: str, prefix: str, project: str, zone: str | None) -> str:
    """门脸层页面（深色）。"""
    project_key = project
    nav_html = dark_nav(project_key, zone, prefix)
    # 装饰层：main.js 依赖 .mist / .cracks-layer / .cursor-dot 三者，缺一个就报错
    decor = """
  <div class="mist mist-1" aria-hidden="true"></div>
  <div class="mist mist-2" aria-hidden="true"></div>
  <div class="mist mist-3" aria-hidden="true"></div>
  <div class="mist mist-4" aria-hidden="true"></div>
  <svg id="cracks" class="cracks" aria-hidden="true"><g class="cracks-layer"></g></svg>
  <div class="cursor-dot" aria-hidden="true"></div>
"""
    return f"""{head(meta, prefix, "page")}
<body class="bg-bg text-text font-sans antialiased">
{decor}
{nav_html}
{body}
{footer(project_key, prefix)}
<script src="{prefix}assets/js/main.js" defer></script>
</body>
</html>
"""


# ── 页面发现与渲染 ──────────────────────────────────────────────────────────

def discover() -> list[tuple[Path, dict, str]]:
    """扫 content/ 下的 .md / .html，返回 (源文件, meta, 正文)。"""
    pages = []
    for path in sorted(CONTENT.rglob("*")):
        if path.suffix not in (".md", ".html"):
            continue
        rel = path.relative_to(CONTENT).as_posix()
        text = path.read_text(encoding="utf-8")
        # .md 与 .html 都允许 front matter——.html 内容文件用它来声明 layout/project/zone
        meta, body = split_front_matter(text)
        if not body.strip():
            meta, body = {}, text
        meta.setdefault("self", "/" + rel[: -len(path.suffix)] + ".html")
        pages.append((path, meta, body))
    return pages


def out_path_for(src: Path) -> Path:
    rel = src.relative_to(CONTENT).as_posix()
    rel = rel[: -len(src.suffix)]
    if rel == "index":
        return ROOT / "index.html"
    return ROOT / (rel + ".html")


def check_links() -> int:
    """检查站内链接与锚点是否都指得到东西。

    报告要求「所有内部链接在 CI 中检查」——这是最便宜的一类回归：
    内容改版时链接最容易悄悄断掉，而它断掉时用户看到的只是一个死按钮。
    """
    broken: list[str] = []
    checked = 0

    SKIP_DIRS = ("content/", "tools/", "downloads/")

    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(SKIP_DIRS):
            continue
        text = path.read_text(encoding="utf-8")
        ids = set(re.findall(r'\sid="([^"]+)"', text))
        # 只看真正的 href / src，别把 data-src 这类属性当成链接
        for m in re.finditer(r'(?<![-\w])(?:href|src)="([^"]+)"', text):
            href = m.group(1)
            if href.startswith(("http://", "https://", "mailto:", "data:", "#")):
                continue
            if href.startswith("#"):
                if href[1:] and href[1:] not in ids:
                    broken.append(f"{rel}: 锚点不存在 → {href}")
                continue
            checked += 1
            target, _, frag = href.partition("#")
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{rel}: 文件不存在 → {href}")
                continue
            if frag and resolved.suffix == ".html":
                tids = set(re.findall(r'\sid="([^"]+)"', resolved.read_text(encoding="utf-8")))
                if frag not in tids:
                    broken.append(f"{rel}: 目标文件里没有锚点 #{frag} → {href}")

    print(f"链接检查：{checked} 条站内链接")
    if broken:
        print(f"!! {len(broken)} 条断了：")
        for b in broken:
            print("   ", b)
        return 1
    print("✓ 没有断链")
    return 0


def build() -> int:
    pages = discover()
    if not pages:
        print("!! content/ 是空的 —— 没有页面可生成", file=sys.stderr)
        return 1

    # 第一遍：收集所有输出路径 + 标题，用于搜索索引和 wiki 链接
    index_entries = []
    for src, meta, body in pages:
        out = out_path_for(src)
        index_entries.append((out, meta, body))

    # 清旧输出
    for d in OUTPUT_ROOTS:
        p = ROOT / d
        if p.is_dir() and not (p / ".keep").exists():
            shutil.rmtree(p)

    written = []
    search_index = []

    for out, meta, body in index_entries:
        prefix = rel_prefix(out)
        layout = meta.get("layout", "page")
        project = meta.get("project", "compiler")
        zone = meta.get("zone")

        if layout == "docs":
            headings: list = []
            renderer = Renderer(C.WIKI_LINKS, lambda lv, t, s: headings.append((lv, t, s)))
            body_html = renderer.render(body)
            page = render_docs_layout(meta, body_html, prefix, out, headings)
            # 侧栏当前项高亮：按 self 匹配
            page = page.replace('class="doc-nav-group"', 'class="doc-nav-group"', 1)
            written.append(out)
            search_index.append(
                {
                    "url": "/" + out.relative_to(ROOT).as_posix(),
                    "title": meta.get("title", ""),
                    "desc": meta.get("description", ""),
                    "text": re.sub(r"\s+", " ", re.sub(r"[#*`>|\[\]]", " ", body))[:600],
                    "headings": [
                        {"text": re.sub(r"[`*]", "", t), "slug": s}
                        for lv, t, s in headings
                        if lv <= 3
                    ],
                }
            )
        else:
            if src.suffix == ".html":
                body_html = body
            else:
                body_html = '<main id="top" class="page-main">\n' + Renderer(C.WIKI_LINKS).render(body) + "\n</main>"
            page = render_page_layout(meta, body_html, prefix, project, zone)
            written.append(out)
            if meta.get("search", "true") != "false":
                search_index.append(
                    {
                        "url": "/" + out.relative_to(ROOT).as_posix(),
                        "title": meta.get("title", ""),
                        "desc": meta.get("description", ""),
                        "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))[:600],
                        "headings": [],
                    }
                )

        page = rewrite_links(page, prefix)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")

    # 搜索索引
    idx_path = ROOT / "search-index.json"
    idx_path.write_text(json.dumps(search_index, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"✓ 生成 {len(written)} 页 + search-index.json")
    for w in sorted(written):
        print("   ", w.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        rc = check_links()
        sys.exit(rc)
    sys.exit(build())
