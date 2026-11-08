"""极简 Markdown 渲染器 —— 零第三方依赖。

只覆盖官网实际用到的语法子集：
  ATX 标题 / 段落 / 有序无序列表（含嵌套）/ 围栏代码块 / 行内代码 /
  粗体斜体 / 链接 / 图片 / 引用块 / 分隔线 / 表格 / 任务列表 / 原始 HTML 块 /
  `[[Wiki 链接]]`（由调用方传入链接表解析）

设计原则：渲染失败宁缺毋滥——无法识别的行按纯文本原样输出，不吞内容。
"""

from __future__ import annotations

import html
import re
import unicodedata
from typing import Callable

# ── 基础工具 ────────────────────────────────────────────────────────────────

_SLUG_STRIP = re.compile(r"[^\w一-鿿\- ]+", re.UNICODE)


def slugify(text: str) -> str:
    """标题 → 锚点 id。中文保留（可读），英文小写连字符化。"""
    text = re.sub(r"`([^`]*)`", r"\1", text)          # 去掉行内代码标记
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)    # 去掉粗体标记
    text = re.sub(r"\*([^*]*)\*", r"\1", text)        # 去掉斜体标记
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = _SLUG_STRIP.sub("", text).strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    return text or "section"


def _esc(text: str) -> str:
    return html.escape(text, quote=False)


# ── 行内渲染 ────────────────────────────────────────────────────────────────

_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)")
_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
_WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<![\*\w])\*([^*\n]+)\*(?!\*)")
# 行内代码：支持 ``双反引号``（内容里可以含单个反引号）
_CODE = re.compile(r"(`{1,2})(.+?)\1", re.S)
_AUTOLINK = re.compile(r"<((?:https?|mailto):[^>\s]+)>")
_BARE_URL = re.compile(r"(?<![\"'>=(])(https?://[^\s<>\")]+)")


def render_inline(text: str, links: dict[str, str] | None = None) -> str:
    """行内 Markdown → HTML。链接表用于解析 `[[Wiki 链接]]`。"""
    links = links or {}
    out: list[str] = []
    pos = 0

    # 先抽出代码片段，避免代码里的 * _ 被当强调
    stash: list[str] = []

    def _stash_code(m: re.Match) -> str:
        stash.append(m.group(2))
        return f"\x00{len(stash) - 1}\x00"

    text = _CODE.sub(_stash_code, text)

    # 图片先于链接处理（避免 ![alt](src) 被链接规则吃掉方括号）
    def _img(m: re.Match) -> str:
        alt, src = _esc(m.group(1)), m.group(2)
        return f'<img src="{html.escape(src, quote=True)}" alt="{alt}" loading="lazy" />'

    text = _IMAGE.sub(_img, text)

    def _link(m: re.Match) -> str:
        label, href = m.group(1), m.group(2)
        title = m.group(3)
        attrs = f' title="{html.escape(title, quote=True)}"' if title else ""
        if href.startswith(("http://", "https://")):
            attrs += ' target="_blank" rel="noopener noreferrer"'
        return f'<a href="{html.escape(href, quote=True)}"{attrs}>{label}</a>'

    text = _LINK.sub(_link, text)

    def _wiki(m: re.Match) -> str:
        target = m.group(1).strip()
        label = (m.group(2) or target).strip()
        href = links.get(target)
        if not href:
            return f'<span class="wl-missing">{_esc(label)}</span>'
        return f'<a href="{html.escape(href, quote=True)}">{_esc(label)}</a>'

    text = _WIKILINK.sub(_wiki, text)

    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)
    text = _AUTOLINK.sub(r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', text)
    text = _BARE_URL.sub(
        r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', text
    )

    # 放回代码片段
    text = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{html.escape(stash[int(m.group(1))])}</code>", text)
    return text


# ── 块级渲染 ────────────────────────────────────────────────────────────────

_FENCE = re.compile(r"^```\s*([A-Za-z0-9_+-]*)\s*$")
_TABLE_SEP = re.compile(r"^\|?[\s:|-]+\|[\s:|-]*$")


class Renderer:
    """把 Markdown 文本渲染成 HTML。

    `links`  : `[[Wiki 链接]]` → href 的解析表
    `heading_hook`: 每渲染一个标题回调 (level, text, slug)，用于生成目录
    """

    def __init__(
        self,
        links: dict[str, str] | None = None,
        heading_hook: Callable[[int, str, str], None] | None = None,
    ) -> None:
        self.links = links or {}
        self.heading_hook = heading_hook

    # -- 入口 ---------------------------------------------------------------

    def render(self, text: str) -> str:
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        return "\n".join(self._blocks(lines))

    # -- 块分发 -----------------------------------------------------------

    def _blocks(self, lines: list[str]) -> list[str]:
        out: list[str] = []
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            stripped = line.strip()

            if not stripped:
                i += 1
                continue

            # 围栏代码块
            m = _FENCE.match(stripped)
            if m:
                lang = m.group(1)
                i += 1
                buf: list[str] = []
                while i < n and not _FENCE.match(lines[i].strip()):
                    buf.append(lines[i])
                    i += 1
                i += 1  # 吃掉收尾围栏
                body = html.escape("\n".join(buf), quote=False)
                if lang.lower() == "mermaid":
                    out.append(f'<pre class="mermaid">{body}\n</pre>')
                    continue
                cls = f' class="language-{html.escape(lang, quote=True)}"' if lang else ""
                out.append(f"<pre><code{cls}>{body}\n</code></pre>")
                continue

            # 原始 HTML 块（整行以 < 开头）——原样透传
            if stripped.startswith("<") and re.match(r"^</?[a-zA-Z]", stripped):
                buf = []
                while i < n and lines[i].strip():
                    buf.append(lines[i])
                    i += 1
                out.append("\n".join(buf))
                continue

            # 标题
            m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", stripped)
            if m:
                level = len(m.group(1))
                raw = m.group(2)
                # 显式锚点：`## 当前稳定版 {#current}` —— 标题用中文，锚点保持 ASCII
                explicit = None
                am = re.search(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$", raw)
                if am:
                    explicit = am.group(1)
                    raw = raw[: am.start()].rstrip()
                slug = explicit or slugify(raw)
                if self.heading_hook:
                    self.heading_hook(level, raw, slug)
                out.append(f'<h{level} id="{slug}">{render_inline(raw, self.links)}</h{level}>')
                i += 1
                continue

            # 分隔线
            if re.match(r"^([-*_])\s*(\1\s*){2,}$", stripped):
                out.append("<hr />")
                i += 1
                continue

            # 表格
            if "|" in line and i + 1 < n and _TABLE_SEP.match(lines[i + 1].strip()):
                out.append(self._table(lines, i))
                i = self._skip_table(lines, i)
                continue

            # 引用块
            if stripped.startswith(">"):
                buf = []
                while i < n and (lines[i].strip().startswith(">") or not lines[i].strip()):
                    buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                    i += 1
                inner, variant = self._callout(buf)
                out.append(f'<blockquote class="callout{variant}">{inner}</blockquote>')
                continue

            # 列表
            if re.match(r"^(\s*)([-*+]|\d+[.)])\s+", line):
                list_html, i = self._list(lines, i)
                out.append(list_html)
                continue

            # 段落
            buf = []
            while i < n and lines[i].strip():
                nxt = lines[i].strip()
                if (
                    nxt.startswith(("#", ">", "```", "|"))
                    or re.match(r"^(\s*)([-*+]|\d+[.)])\s+", lines[i])
                    or _FENCE.match(nxt)
                ):
                    break
                buf.append(lines[i].strip())
                i += 1
            if buf:
                para = " ".join(buf)
                out.append(f"<p>{render_inline(para, self.links)}</p>")

        return out

    # -- Callout -----------------------------------------------------------

    _CALLOUT_KINDS = {
        "NOTE": "",
        "TIP": "",
        "INFO": "",
        "IMPORTANT": " warn",
        "WARNING": " warn",
        "CAUTION": " danger",
        "DANGER": " danger",
    }

    def _callout(self, buf: list[str]) -> tuple[str, str]:
        """渲染引用块；首行的 `[!NOTE]` 之类标记映射成 callout 变体。"""
        variant = ""
        if buf:
            m = re.match(r"^\s*\[!(NOTE|TIP|INFO|IMPORTANT|WARNING|CAUTION|DANGER)\]\s*$", buf[0])
            if m:
                variant = self._CALLOUT_KINDS.get(m.group(1), "")
                buf = buf[1:]
        return self.render("\n".join(buf)), variant

    # -- 表格 -------------------------------------------------------------
    def _table(self, lines: list[str], i: int) -> str:
        header = _split_row(lines[i])
        align = _split_row(lines[i + 1])
        body = []
        j = i + 2
        while j < len(lines) and lines[j].strip() and "|" in lines[j]:
            body.append(_split_row(lines[j]))
            j += 1

        def _cell(tag: str, text: str, a: str) -> str:
            attr = ""
            if a == "center":
                attr = ' style="text-align:center"'
            elif a == "right":
                attr = ' style="text-align:right"'
            return f"<{tag}{attr}>{render_inline(text, self.links)}</{tag}>"

        cols = []
        for k, h in enumerate(header):
            cols.append(_cell("th", h, align[k] if k < len(align) else ""))
        rows = []
        for r in body:
            cells = []
            for k in range(len(header)):
                cells.append(_cell("td", r[k] if k < len(r) else "", align[k] if k < len(align) else ""))
            rows.append("<tr>" + "".join(cells) + "</tr>")
        return (
            '<div class="table-wrap"><table class="ref-table"><thead><tr>'
            + "".join(cols)
            + "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></div>"
        )

    def _skip_table(self, lines: list[str], i: int) -> int:
        j = i + 2
        while j < len(lines) and lines[j].strip() and "|" in lines[j]:
            j += 1
        return j

    # -- 列表 -------------------------------------------------------------

    def _list(self, lines: list[str], i: int) -> tuple[str, int]:
        """渲染一个列表，返回 (html, 列表结束后的行号)。

        **结束行号必须由本函数给出。** 早期版本让 `_list` 和 `_skip_list` 各自
        算一遍边界，两套规则只要有一处不一致，列表尾巴就会被再渲染一遍
        （页面上表现为同一段话重复两三次）。现在边界只有一个来源。
        """
        base_indent = len(lines[i]) - len(lines[i].lstrip())
        ordered = bool(re.match(r"^\s*\d+[.)]\s", lines[i]))
        items: list[dict] = []          # {"text": [...], "nested": [...]}
        j = i
        end = i

        while j < len(lines):
            line = lines[j]
            if not line.strip():
                # 空行后若还是列表项，视为同一个（松散）列表继续
                nxt = lines[j + 1] if j + 1 < len(lines) else ""
                if nxt.strip() and re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", nxt):
                    j += 1
                    continue
                break
            m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
            if not m:
                break
            indent = len(m.group(1))
            if indent < base_indent:
                break                       # 列表结束
            if indent > base_indent:
                # 缩进更深 ⇒ 上一项的子列表
                if not items:
                    break
                items[-1]["nested"].append(line)
                end = j + 1
                j += 1
                continue
            items.append({"text": [m.group(3)], "nested": []})
            end = j + 1
            j += 1
            # 收续行：不是列表标记、也不是更深的缩进 ⇒ 并入本项
            while j < len(lines) and lines[j].strip():
                mm = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", lines[j])
                if mm:
                    break                   # 同级下一项 / 子列表，交给外层
                items[-1]["text"].append(lines[j].strip())
                end = j + 1
                j += 1

        tag = "ol" if ordered else "ul"
        html_items = []
        for item in items:
            text_lines = list(item["text"])
            task = ""
            tm = re.match(r"^\[([ xX])\]\s+(.*)$", text_lines[0]) if text_lines else None
            if tm:
                checked = tm.group(1).lower() == "x"
                task = f'<input type="checkbox" disabled{" checked" if checked else ""} /> '
                text_lines = [tm.group(2)] + text_lines[1:]
            inner = render_inline(" ".join(text_lines).strip(), self.links)
            nested_html = ""
            if item["nested"]:
                sub = Renderer(self.links, self.heading_hook)
                nested_html = sub.render("\n".join(item["nested"]))
            html_items.append(f"<li>{task}{inner}{nested_html}</li>")
        return f"<{tag} class='md-list'>" + "".join(html_items) + f"</{tag}>", end


def _split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]
