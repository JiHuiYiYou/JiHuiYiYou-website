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
import i18n as I18N  # noqa: E402
from mdrender import Renderer, render_inline, slugify  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
TOOLS = ROOT / "tools"

# 每次生成都清掉的输出目录（只清我们自己产出的那几个）
# "en" 是英文树；"docs" 从来不存在（文档实际在 content/compiler/docs/ 下），删掉。
OUTPUT_ROOTS = ("compiler", "ide", "os", "vex", "en")

# ── 事实占位符 ────────────────────────────────────────────────────────────
# 正文里写 {{key}}，构建器从 siteconfig.FACTS 取值。
# 目的只有一个：**两种语言不可能对不上数字** —— 它们拿的是同一份常量。
FACT_PATTERN = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")

# 值里不许出现这些 —— 替换后的正文会被 mdrender 再解释一遍
MARKDOWN_ACTIVE = "*_`[]|<>"


def substitute_facts(text: str, where: str) -> str:
    """把 {{key}} 换成 siteconfig.FACTS 里的值。

    未知 key ⇒ 报错并列出 key 与出处。**静默留空会把「忘了写」变成线上
    一处空白**，而空白比报错难查得多。
    """
    unknown: list[str] = []
    bad: list[str] = []

    def repl(m: re.Match) -> str:
        key = m.group(1)
        if key not in C.FACTS:
            unknown.append(key)
            return m.group(0)
        value = str(C.FACTS[key])
        if any(ch in value for ch in MARKDOWN_ACTIVE):
            bad.append(f"{key}={value!r}")
            return m.group(0)
        return value

    out = FACT_PATTERN.sub(repl, text)
    if unknown:
        raise KeyError(f"{where}: 未知的事实占位符 {sorted(set(unknown))}")
    if bad:
        raise ValueError(f"{where}: 事实值含 markdown 活跃字符 → {bad}")
    return out


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
    """拆 front matter。

    收尾栅栏必须是**整行**的 `---` —— 正文里的分隔线（`---`，CONTENT_GUIDE
    §3 明写是支持的）不能被当成 front matter 的结束标记。否则
    ``---\\nIntro\\n\\n---\\n\\n## S\\n`` 会被解析成「没有 front matter」，
    开头那段被静默吞掉。
    """
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end() :].lstrip("\n")
    meta: dict = {}
    for line in raw.split("\n"):
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


# ── 导航 / 页脚 ─────────────────────────────────────────────────────────────

def project_switcher(active: str, lang: str, routes: dict) -> str:
    """项目切换器 —— 纯 HTML/CSS 的下拉（<details>），不依赖 JS。"""
    cur = next((p for p in C.PROJECTS if p["key"] == active), None)
    # 英文页上当前项目要写英文名 —— 主标签跟页面语言一致，中文名退到副标签。
    label = (cur["name"] if lang == "zh" else cur["en"]) if cur else I18N.t(lang, "all_projects")
    items = []
    for p in C.PROJECTS:
        state = " is-active" if p["key"] == active else ""
        name, sub = (p["name"], p["en"]) if lang == "zh" else (p["en"], p["name"])
        items.append(
            f'<a class="proj-item{state}" href="{normalize_href(localize_href(p["path"], lang, routes)[0])}">'
            f'<span class="proj-item-name">{html.escape(name)}</span>'
            f'<span class="proj-item-en">{html.escape(sub)}</span>'
            f'<span class="proj-item-tag">{html.escape(pick(p, "tagline", lang))}</span>'
            f"</a>"
        )
    return (
        '<details class="proj-switch">'
        f'<summary class="proj-summary"><span class="proj-dot" aria-hidden="true"></span>'
        f'{html.escape(label)}<span class="proj-caret" aria-hidden="true">▾</span></summary>'
        f'<div class="proj-menu" role="navigation" aria-label="{html.escape(I18N.t(lang, "family_nav"))}">{"".join(items)}</div>'
        "</details>"
    )


def pick(d: dict, key: str, lang: str) -> str:
    """按语言取字段。**缺字段就 KeyError** —— 漏译在构建期崩，不上线。"""
    field = key if lang == "zh" else key + "_en"
    if field not in d:
        raise KeyError(f"i18n: {key!r} 缺 {lang} 的 {field!r}")
    return d[field]


def fill_facts(s: str) -> str:
    """把标签里的 {key} 填上 FACTS 的值。

    导航 / 侧栏标签里的版本号**不许手写** —— 它们跟正文一样从同一份常量来。
    """

    def repl(m: re.Match) -> str:
        key = m.group(1)
        if key not in C.FACTS:
            raise KeyError(f"标签里未知的事实占位符 {key!r}")
        return str(C.FACTS[key])

    return re.sub(r"\{([A-Za-z0-9_]+)\}", repl, s)


def lang_switcher(ctx: dict) -> str:
    """语言切换器 —— 普通 <a>，**无 JS 依赖**。

    另一种语言的树还不存在时**整个不渲染** —— 链到一个不存在的页面
    比没有切换器更糟（链接门会红，读者会点到一个 404）。
    树存在但本页没有孪生页时（文档层本轮还没英文），指向那种语言的语言首页。
    """
    lang = ctx["lang"]
    other = "en" if lang == "zh" else "zh"
    if other not in (ctx.get("langs") or ()):
        return ""
    routes = ctx.get("routes") or {}
    route = ctx.get("route") or ""
    pair = routes.get(route) or {}
    zh_url = pair.get("zh") or "/index.html"
    en_url = pair.get("en") or "/en/index.html"
    items = []
    for code, url in (("zh", zh_url), ("en", en_url)):
        is_cur = code == lang
        cls = "lang-opt is-active" if is_cur else "lang-opt"
        cur = ' aria-current="true"' if is_cur else ""
        label = I18N.t(code, "lang_name")
        items.append(f'<a class="{cls}" href="{url}" hreflang="{code}"{cur}>{label}</a>')
    return (
        f'<div class="lang-switch" role="navigation" aria-label="{html.escape(I18N.t(lang, "lang_switch_label"))}">'
        + "".join(items)
        + "</div>"
    )


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


def route_from_href(href: str) -> str | None:
    """站内 href → route（用于跨语言本地化）。资源路径不算 route。"""
    if not href.startswith("/"):
        return None
    p = href.lstrip("/")
    if p.startswith("assets/"):
        return None
    if p.endswith("/"):
        p = p[:-1] + "/index"
    if p.endswith(".html"):
        p = p[:-5]
    return p


def localize_href(href: str, lang: str, routes: dict) -> tuple[str, bool]:
    """把站内链接本地化到当前语言。

    返回 (href, zh_only)。中文页原样返回（零改动）；英文页有英文孪生就指
    过去，没有就保留指向中文页的链接并标「仅中文」—— 不假装它有英文版。
    """
    if lang == "zh" or not href.startswith("/"):
        return href, False
    base, _, _frag = href.partition("#")
    route = route_from_href(base)
    if route is None:
        return href, False
    target = (routes.get(route) or {}).get("en")
    if not target:
        return href, True
    # 跨语言 → 锚点去掉（英文孪生页上不会有中文锚点）
    return target, False


def _link(href: str, lang: str, routes: dict, cls: str = "", inner: str = "") -> str:
    """一个站内 <a>：本地化 + 跨语言时挂「仅中文」提示。"""
    h, xlang = localize_href(href, lang, routes)
    title = f' title="{html.escape(I18N.t(lang, "zh_only"))}"' if xlang else ""
    c = f' class="{cls}"' if cls else ""
    return f'<a{c}{title} href="{normalize_href(h)}">{inner}</a>'


_A_TAG = re.compile(r"<a\b([^>]*?)href=\"([^\"]+)\"([^>]*)>")


def localize_body_links(body_html: str, lang: str, routes: dict) -> str:
    """英文页**正文**里的站内链接指到英文孪生页。

    导航/页脚的链接由 `_link` 处理；正文里的链接来自内容源 —— 源里写的是
    根绝对路径，两棵树写法相同 ⇒ 由构建器按当前语言改写。

    没有英文孪生页时（文档层本轮还没译）⇒ 保留指向中文页的链接，并挂
    「仅中文」提示 —— 不假装它有英文版。
    """
    if lang == "zh":
        return body_html

    def repl(m: re.Match) -> str:
        pre, href, post = m.group(1), m.group(2), m.group(3)
        if not href.startswith("/"):
            return m.group(0)
        new, zh_only = localize_href(href, lang, routes)
        if new == href and not zh_only:
            return m.group(0)
        title = f' title="{html.escape(I18N.t(lang, "zh_only"))}"' if zh_only else ""
        pre = re.sub(r'\s*title="[^"]*"', "", pre)
        post = re.sub(r'\s*title="[^"]*"', "", post)
        return f'<a{pre}href="{new}"{post}{title}>'

    return _A_TAG.sub(repl, body_html)


def dark_nav(project: str, zone: str | None, prefix: str, lang: str, ctx: dict) -> str:
    """门脸层导航（深色玻璃胶囊）。所有非文档页共用。"""
    routes = ctx.get("routes") or {}
    if project == "compiler":
        nav = C.COMPILER_NAV
        repo = C.PROJECTS[0]["repo"]
    elif project == "home":
        nav = []
        repo = C.ORG_SITE
    else:
        nav = C.PROJECT_NAV.get(project, [])
        repo = next((p["repo"] for p in C.PROJECTS if p["key"] == project), C.ORG_SITE)
    links = []
    for it in nav:
        cur = " is-active" if it.get("key") == zone or it["href"] == zone else ""
        href, xlang = localize_href(it["href"], lang, routes)
        title = f' title="{html.escape(I18N.t(lang, "zh_only"))}"' if xlang else ""
        label = html.escape(fill_facts(pick(it, "label", lang)))
        links.append(f'<a class="{cur.strip()}"{title} href="{normalize_href(href)}">{label}</a>')
    zone_links = '<div class="nav-links" role="navigation">' + "".join(links) + "</div>" if links else ""
    dl_href, _ = localize_href("/compiler/download/", lang, routes)
    return f"""
  <nav class="floating-nav" aria-label="{html.escape(I18N.t(lang, "primary_nav"))}">
    <div class="nav-pill">
      <a href="{prefix}index.html" class="nav-logo" aria-label="{html.escape(I18N.t(lang, "brand_home"))}">
        <img src="{prefix}assets/img/jhyy-logo.png" class="logo-img" height="30" alt="机会翼游 · JHYY" />
      </a>
      {project_switcher(project, lang, routes)}
      {zone_links}{lang_switcher(ctx)}
      <div class="nav-cta-group">
        <a href="{repo}" class="nav-icon-btn" aria-label="{html.escape(I18N.t(lang, "github"))}">{GITHUB_ICON}</a>
        <a href="{normalize_href(dl_href)}" class="nav-cta magnetic" data-magnetic>
          <span>{html.escape(I18N.t(lang, "download_cta", version=C.SITE_VERSION))}</span>
          <span class="btn-icon-wrap">{ARROW_ICON}</span>
        </a>
      </div>
    </div>
  </nav>
"""


def docs_nav(project: str, prefix: str, zone: str | None, lang: str, ctx: dict) -> str:
    """文档层顶栏（浅色、信息密集）。"""
    routes = ctx.get("routes") or {}
    nav = C.COMPILER_NAV
    repo = C.PROJECTS[0]["repo"]
    links = []
    for it in nav:
        cur = " is-active" if it.get("key") == zone else ""
        href, xlang = localize_href(it["href"], lang, routes)
        title = f' title="{html.escape(I18N.t(lang, "zh_only"))}"' if xlang else ""
        label = html.escape(fill_facts(pick(it, "label", lang)))
        links.append(f'<a class="{cur.strip()}"{title} href="{normalize_href(href)}">{label}</a>')
    return f"""
  <header class="doc-topbar">
    <div class="doc-topbar-inner">
      <a href="{prefix}index.html" class="doc-brand" aria-label="{html.escape(I18N.t(lang, "brand_home"))}">
        <img src="{prefix}assets/img/jhyy-logo.png" alt="机会翼游 · JHYY" />
        <span class="doc-brand-name">JHYY</span>
      </a>
      {project_switcher("compiler", lang, routes)}
      <nav class="doc-zones" aria-label="{html.escape(I18N.t(lang, "primary_nav"))}">{"".join(links)}</nav>
      <div class="doc-topbar-right">
        <button class="doc-search-btn" type="button" data-search-open data-search-index="{prefix}search-index.json" data-search-lang="{lang}" aria-label="{html.escape(I18N.t(lang, "search_docs"))}">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
          <span>{html.escape(I18N.t(lang, "search_docs"))}</span><kbd>/</kbd>
        </button>
        <span class="doc-version" title="{html.escape(I18N.t(lang, "latest_stable"))}">v{C.SITE_VERSION}</span>
        {lang_switcher(ctx)}
        <a href="{repo}" class="doc-gh" aria-label="{html.escape(I18N.t(lang, "github"))}">{GITHUB_ICON}</a>
      </div>
    </div>
  </header>
"""


def footer(project: str, prefix: str, lang: str, ctx: dict) -> str:
    routes = ctx.get("routes") or {}
    repo = C.PROJECTS[0]["repo"]
    proj_links = "\n            ".join(
        f'<li>{_link(p["path"], lang, routes, inner=html.escape(p["name"]) + f"""<span class="foot-sub">{html.escape(p["en"])}</span>""")}</li>'
        for p in C.PROJECTS
    )
    zone_items = [
        ("/compiler/docs/", "文档", "Docs"),
        ("/compiler/download/", "下载", "Download"),
        ("/compiler/community/", "社区", "Community"),
        ("/compiler/governance/", "治理", "Governance"),
    ]
    zone_links = "\n            ".join(
        f'<li>{_link(href, lang, routes, inner=html.escape(zh if lang == "zh" else en))}</li>'
        for href, zh, en in zone_items
    )
    spec_rows = "\n            ".join(
        f'<li><a href="{url}">{html.escape(I18N.t(lang, key, version=ver))}</a></li>'
        for key, url, ver in (
            ("lang_spec", f"{C.DOC_SOURCE_REPO}/blob/main/docs/abis/jhyy-lang-spec-v{C.SPEC_VERSION}.md", C.SPEC_VERSION),
            ("abi_spec", f"{C.DOC_SOURCE_REPO}/blob/main/docs/abis/jhyy-abi-v{C.ABI_VERSION}.md", C.ABI_VERSION),
            ("binary_format", f"{C.DOC_SOURCE_REPO}/blob/main/docs/abis/jhyy-binary-format-v{C.BINARY_FORMAT_VERSION}.md", C.BINARY_FORMAT_VERSION),
        )
    )
    return f"""
  <footer class="site-foot">
    <div class="container foot-grid">
      <div class="foot-brand">
        <a href="{prefix}index.html" class="nav-logo foot-logo">
          <img src="{prefix}assets/img/jhyy-logo.png" class="logo-img logo-img--foot" alt="机会翼游 · JHYY" />
        </a>
        <p class="foot-tag">{html.escape(I18N.t(lang, "foot_tag"))}</p>
      </div>
      <div class="foot-cols">
        <div class="foot-col">
          <h4 class="foot-h">{html.escape(I18N.t(lang, "foot_family"))}</h4>
          <ul>
            {proj_links}
          </ul>
        </div>
        <div class="foot-col">
          <h4 class="foot-h">{html.escape(I18N.t(lang, "foot_compiler"))}</h4>
          <ul>
            {zone_links}
          </ul>
        </div>
        <div class="foot-col">
          <h4 class="foot-h">{html.escape(I18N.t(lang, "foot_repos"))}</h4>
          <ul>
            <li><a href="{repo}">Compiler</a></li>
            <li><a href="{C.ORG_SITE}/JiHuiYiYou-IDE">IDE</a></li>
            <li><a href="{C.ORG_SITE}/JiHuiYiYou-OS">OS</a></li>
            <li><a href="{C.ORG_SITE}/JiHuiYiYou-for-VEX">for-VEX</a></li>
          </ul>
        </div>
        <div class="foot-col">
          <h4 class="foot-h">{html.escape(I18N.t(lang, "foot_specs"))}</h4>
          <ul>
            {spec_rows}
            <li><a href="{C.DOC_SOURCE_REPO}/blob/main/CHANGELOG.md">{html.escape(I18N.t(lang, "changelog"))}</a></li>
          </ul>
        </div>
        <div class="foot-col">
          <h4 class="foot-h">{html.escape(I18N.t(lang, "foot_community"))}</h4>
          <ul>
            <li><span class="foot-text-strong">{html.escape(I18N.t(lang, "foot_qq", number="429807125"))}</span><button class="ci-copy ci-copy--inline ci-copy--foot" type="button" aria-label="{html.escape(I18N.t(lang, "foot_copy_qq"))}" data-copy-text="429807125"></button></li>
            <li><a href="{repo}/issues">{html.escape(I18N.t(lang, "foot_issues"))}</a></li>
            <li><a href="{repo}/blob/main/CONTRIBUTING.md">{html.escape(I18N.t(lang, "foot_contributing"))}</a></li>
            <li>{_link("/compiler/community/security.html", lang, routes, inner=html.escape(I18N.t(lang, "foot_security")))}</li>
          </ul>
        </div>
      </div>
    </div>
    <div class="foot-bar">
      <div class="container foot-bar-row">
        <span class="foot-copy">{html.escape(I18N.t(lang, "foot_copyright"))}</span>
        <div class="foot-status">
          <span class="status-led"></span>
          <span>{html.escape(I18N.t(lang, "foot_status", version=C.SITE_VERSION, spec=C.SPEC_VERSION))}</span>
        </div>
      </div>
    </div>
  </footer>
"""


# ── 布局 ────────────────────────────────────────────────────────────────────

FONTS = (
    # 字体**自托管**（assets/fonts/）——不走 Google Fonts CDN：
    # fonts.googleapis.com 在中国大陆取不到，取不到就整站掉回系统默认字体。
    # @font-face 规则在 assets/css/fonts.css。
    '<link rel="stylesheet" href="{p}assets/css/fonts.css" />'
)


def head(meta: dict, prefix: str, layout: str, lang: str = "zh", ctx: dict | None = None) -> str:
    title = meta.get("title", "机会翼游 · JHYY")
    desc = meta.get("description", "")
    css = "assets/css/docs.css" if layout == "docs" else "assets/css/main.css"
    extra = ""
    if layout == "docs":
        extra = '<link rel="stylesheet" href="{p}assets/css/main.css" />'.format(p=prefix)
    lang_code = "zh-CN" if lang == "zh" else "en"
    alternates = []
    routes = (ctx or {}).get("routes") or {}
    route = (ctx or {}).get("route") or ""
    pair = routes.get(route) or {}
    # 只声明**另一种语言**的 alternate —— 自引用没有意义
    other = "zh" if lang == "en" else "en"
    if pair.get(other):
        hreflang = "zh-CN" if other == "zh" else "en"
        alternates.append(f'<link rel="alternate" hreflang="{hreflang}" href="{pair[other]}" />')
    alt_html = "\n  ".join(alternates)
    return f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0a0a0a" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc, quote=True)}" />
  <meta property="og:title" content="{html.escape(title, quote=True)}" />
  <meta property="og:description" content="{html.escape(desc, quote=True)}" />
  <meta property="og:type" content="website" />
  {alt_html}
  {FONTS.format(p=prefix)}
  <link rel="stylesheet" href="{prefix}{css}" />
  {extra}
  <link rel="icon" type="image/png" sizes="any" href="{prefix}assets/img/jhyy-icon.png" />
  <noscript><style>
    /* reveal 系列的初始态是 opacity:0，靠 JS 加 .in 才显形 ——
       没有 JS 时整页会是一片黑。这里补一条兜底。 */
    .reveal, .reveal-card, .reveal-scale {{ opacity: 1 !important; transform: none !important; }}
    .reveal-line .line-inner {{ transform: none !important; }}
  </style></noscript>
</head>
"""


def render_docs_layout(meta: dict, body: str, prefix: str, out_path: Path, headings: list, ctx: dict) -> str:
    """文档层：三栏（左 TOC / 中内容 / 右锚点）。"""
    lang = ctx["lang"]
    routes = ctx.get("routes") or {}
    zone = meta.get("zone", "docs")
    groups = C.ZONE_SIDEBARS.get(zone, C.DOC_SIDEBAR)
    self_url = meta.get("self", "")
    sidebar = []
    for group in groups:
        items = []
        for label, label_en, href in group["items"]:
            text = html.escape(fill_facts(label if lang == "zh" else label_en))
            if not href:
                items.append(f'<li><span class="doc-nav-text">{text}</span></li>')
                continue
            if href.startswith("http"):
                items.append(f'<li><a href="{href}" target="_blank" rel="noopener">{text} ↗</a></li>')
                continue
            lhref, zh_only = localize_href(href, lang, routes)
            title = f' title="{html.escape(I18N.t(lang, "zh_only"))}"' if zh_only else ""
            cur = " is-active" if normalize_href(lhref) == normalize_href(self_url) else ""
            items.append(f'<li><a class="{cur.strip()}"{title} href="{normalize_href(lhref)}">{text}</a></li>')
        gtitle = html.escape(fill_facts(group["title"] if lang == "zh" else group["title_en"]))
        sidebar.append(
            f'<div class="doc-nav-group"><h4>{gtitle}</h4><ul>{"".join(items)}</ul></div>'
        )

    anchors = []
    for level, text, slug in headings:
        if level > 3:
            continue
        anchors.append(
            f'<a class="anchor-l{level}" href="#{slug}">{html.escape(re.sub(r"[`*]", "", text))}</a>'
        )

    onthis = (
        f'<nav class="doc-anchors" aria-label="{html.escape(I18N.t(lang, "on_this_page_aria"))}"><h4>{html.escape(I18N.t(lang, "on_this_page"))}</h4>'
        + "".join(anchors)
        + "</nav>"
        if anchors
        else ""
    )

    edit = meta.get("edit")
    edit_html = (
        f'<a class="doc-edit" href="{edit}" target="_blank" rel="noopener">{html.escape(I18N.t(lang, "edit_page"))}</a>' if edit else ""
    )

    external = ""
    if zone == "docs":
        external = f"""
    <div class="doc-nav-group doc-nav-external">
      <h4>{html.escape(I18N.t(lang, "spec_sources"))}</h4>
      <ul>
        <li><a href="{C.DOC_SOURCE_REPO}/blob/main/docs/abis/jhyy-lang-spec-v{C.SPEC_VERSION}.md" target="_blank" rel="noopener">{html.escape(I18N.t(lang, "lang_spec", version=C.SPEC_VERSION))} ↗</a></li>
        <li><a href="{C.DOC_SOURCE_REPO}/blob/main/docs/abis/jhyy-abi-v{C.ABI_VERSION}.md" target="_blank" rel="noopener">{html.escape(I18N.t(lang, "abi_spec", version=C.ABI_VERSION))} ↗</a></li>
        <li><a href="{C.DOC_SOURCE_REPO}/blob/main/docs/internal/workarounds.md" target="_blank" rel="noopener">{html.escape(I18N.t(lang, "ledger"))} ↗</a></li>
      </ul>
    </div>"""

    return f"""{head(meta, prefix, "docs", lang, ctx)}
<body class="doc-body">
{docs_nav("compiler", prefix, zone, lang, ctx)}
<div class="doc-shell">
  <aside class="doc-sidebar" aria-label="{html.escape(I18N.t(lang, "doc_toc"))}">
    {''.join(sidebar)}
    {external}
  </aside>
  <main class="doc-main" id="main">
    <div class="doc-article">
      {body}
      <div class="doc-foot-row">
        {edit_html}
        <a href="https://github.com/{C.ORG}/JiHuiYiYou-website/issues/new" target="_blank" rel="noopener">{html.escape(I18N.t(lang, "report_issue"))}</a>
      </div>
    </div>
  </main>
  {onthis}
</div>
{footer("compiler", prefix, lang, ctx)}
<script src="{prefix}assets/js/docs.js" defer></script>
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({{ startOnLoad: true, theme: "neutral", securityLevel: "loose" }});
</script>
</body>
</html>
"""


def render_page_layout(meta: dict, body: str, prefix: str, project: str, zone: str | None, ctx: dict) -> str:
    """门脸层页面（深色）。"""
    lang = ctx["lang"]
    project_key = project
    nav_html = dark_nav(project_key, zone, prefix, lang, ctx)
    # 装饰层：main.js 依赖 .mist / .cracks-layer / .cursor-dot 三者，缺一个就报错
    decor = """
  <div class="mist mist-1" aria-hidden="true"></div>
  <div class="mist mist-2" aria-hidden="true"></div>
  <div class="mist mist-3" aria-hidden="true"></div>
  <div class="mist mist-4" aria-hidden="true"></div>
  <svg id="cracks" class="cracks" aria-hidden="true"><g class="cracks-layer"></g></svg>
  <div class="cursor-dot" aria-hidden="true"></div>
"""
    return f"""{head(meta, prefix, "page", lang, ctx)}
<body class="bg-bg text-text font-sans antialiased">
{decor}
{nav_html}
{body}
{footer(project_key, prefix, lang, ctx)}
<script src="{prefix}assets/js/main.js" defer></script>
</body>
</html>
"""


# ── 页面发现与渲染 ──────────────────────────────────────────────────────────

def derive_project(route: str) -> str:
    """按 route 推导项目归属 —— front matter 没写时的兜底。

    没有它，一个没写 front matter 的 en 文件会被当成编译器页
    （默认值是 project="compiler"）。
    """
    head = route.split("/")[0]
    return head if head in ("compiler", "ide", "os", "vex") else "home"


def derive_zone(route: str, layout: str) -> str | None:
    """landing 页的 zone 恒为 home；文档层按第二段（docs/download/…）。"""
    if layout != "docs":
        return "home"
    parts = route.split("/")
    if len(parts) >= 2 and parts[1] in C.ZONE_SIDEBARS:
        return parts[1]
    return None


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
        lang = I18N.lang_of(rel)
        route = I18N.route_of(rel)
        if lang == "en" and not meta:
            raise ValueError(f"content/{rel}: 英文源必须有 front matter")
        # 事实占位符：两种语言共用同一份常量 —— 数字不可能对不上
        for k, v in list(meta.items()):
            meta[k] = substitute_facts(v, f"content/{rel} (front matter {k})")
        body = substitute_facts(body, f"content/{rel}")
        layout = meta.get("layout", "page")
        meta.setdefault("project", derive_project(route))
        meta.setdefault("zone", derive_zone(route, layout))
        meta["lang"] = lang
        meta["route"] = route
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
        candidates = [m.group(1) for m in re.finditer(r'(?<![-\w])(?:href|src)="([^"]+)"', text)]
        # <object data="..."> 是资源引用（内联 SVG 用的就是它）—— 也要查，
        # 但不能把 data-src 这种代码样本当链接，所以只认 object 标签里的 data。
        candidates += [
            m.group(1)
            for m in re.finditer(r"<object\b[^>]*?\sdata=\"([^\"]+)\"", text)
        ]
        for href in candidates:
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
    # ⚠️ 必须把 src 一起带上 —— 下面渲染时要靠它判断源是 .html 还是 .md。
    #    （曾经只存 out，于是 src 是上一轮循环的残留值，.html 的原始通道成了死代码。）
    index_entries = []
    for src, meta, body in pages:
        out = out_path_for(src)
        index_entries.append((src, out, meta, body))

    # 清旧输出
    for d in OUTPUT_ROOTS:
        p = ROOT / d
        if p.is_dir() and not (p / ".keep").exists():
            shutil.rmtree(p)

    # route → {语言: 站点绝对 URL}。同一 route 的中英两页互为孪生。
    # 语言切换器与「跨语言本地化」都靠它。
    routes: dict[str, dict[str, str]] = {}
    for src, out, meta, body in index_entries:
        url = "/" + out.relative_to(ROOT).as_posix()
        routes.setdefault(meta["route"], {})[meta["lang"]] = url
    # 站上实际存在的语言（另一种语言的树还没有时，切换器整个不渲染）
    langs_present = {lg for pair in routes.values() for lg in pair}

    written = []
    search_index = []

    for src, out, meta, body in index_entries:
        prefix = rel_prefix(out)
        layout = meta.get("layout", "page")
        project = meta.get("project", "compiler")
        zone = meta.get("zone")
        lang = meta["lang"]
        ctx = {"lang": lang, "route": meta["route"], "routes": routes, "langs": langs_present}

        if layout == "docs":
            headings: list = []
            renderer = Renderer(C.WIKI_LINKS, lambda lv, t, s: headings.append((lv, t, s)))
            body_html = renderer.render(body)
            body_html = localize_body_links(body_html, lang, routes)
            page = render_docs_layout(meta, body_html, prefix, out, headings, ctx)
            # 侧栏当前项高亮：按 self 匹配
            page = page.replace('class="doc-nav-group"', 'class="doc-nav-group"', 1)
            written.append(out)
            search_index.append(
                {
                    "url": "/" + out.relative_to(ROOT).as_posix(),
                    "lang": lang,
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
                # 手写的 HTML 源走**原始通道**（不经 Markdown 渲染器）。
                # 它必须自带 <main>；没有就补一层 —— .page-main 在两份 CSS 里
                # 都没有规则，纯语义，不影响版式。
                body_html = (
                    body
                    if body.lstrip().startswith("<main")
                    else '<main id="top" class="page-main">\n' + body + "\n</main>"
                )
            else:
                body_html = '<main id="top" class="page-main">\n' + Renderer(C.WIKI_LINKS).render(body) + "\n</main>"
            body_html = localize_body_links(body_html, lang, routes)
            page = render_page_layout(meta, body_html, prefix, project, zone, ctx)
            written.append(out)
            if meta.get("search", "true") != "false":
                search_index.append(
                    {
                        "url": "/" + out.relative_to(ROOT).as_posix(),
                        "lang": lang,
                        "title": meta.get("title", ""),
                        "desc": meta.get("description", ""),
                        "text": re.sub(
                            r"\s+", " ", re.sub(r"<!--.*?-->", " ", re.sub(r"<[^>]+>", " ", body), flags=re.S)
                        )[:600],
                        "headings": [],
                    }
                )

        page = rewrite_links(page, prefix)
        # 逐行去掉尾随空白 —— 生成的 HTML 进仓，尾随空白只会让 diff 变脏
        page = "\n".join(line.rstrip() for line in page.split("\n"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8", newline="\n")

    # 搜索索引
    idx_path = ROOT / "search-index.json"
    idx_path.write_text(
        json.dumps(search_index, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n"
    )

    print(f"✓ 生成 {len(written)} 页 + search-index.json")
    for w in sorted(written):
        print("   ", w.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        rc = check_links()
        sys.exit(rc)
    sys.exit(build())
