#!/usr/bin/env python3
"""孪生页门 —— 每个页面都要有中英两版。

**为什么要有这道门**：官网是构建期双树（`content/**` 中文 / `content/en/**` 英文）。
两棵树一旦长短不一，中文读者点「English」会落到 404，英文读者点「中文」会落到
404 —— 而链接门只查**站内已存在的链接**，查不到「本该存在却没生成」的页面。

规则：
1. `i18n.TWIN_REQUIRED` 里列的 route 必须中英双版（点名报缺哪一边）
2. **非豁免**的 route 必须中英双版 —— 新加的页面不能悄悄只有一种语言
3. 反向：有英文版却没有中文版 ⇒ 同样红
4. 豁免名单陈旧（豁免的 route 已经有英文版）⇒ 警告，提醒该清名单了
5. 每个源文件都要有对应的构建产物（源加了没重建 ⇒ 红）
6. **结构对拍**（只查 `.md` 的孪生页）：中英两页的标题层级、代码块行数、
   表格行数、列表条数、callout、事实占位符必须一致 —— 翻译最怕的不是译错，
   是**漏译**：少一节、少一行表格、少一段代码，没有任何别的门会红

用法：
    python tools/check_twins.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import i18n as I18N  # noqa: E402


def collect() -> dict[str, dict[str, str]]:
    """route → {语言: 源文件相对路径}"""
    routes: dict[str, dict[str, str]] = {}
    for path in sorted(CONTENT.rglob("*")):
        if path.suffix not in (".md", ".html"):
            continue
        rel = path.relative_to(CONTENT).as_posix()
        routes.setdefault(I18N.route_of(rel), {})[I18N.lang_of(rel)] = rel
    return routes


def output_path(rel: str) -> Path:
    """源文件（相对 content/）→ 构建产物路径。

    content/X.md → ROOT/X.html ；content/en/X.md → ROOT/en/X.html
    """
    p = Path(rel)
    return ROOT.joinpath(*p.parts[:-1], p.stem + ".html")


# ── 结构对拍（规则 6）────────────────────────────────────────────────────
# 只查 `.md` 的孪生页：门脸页是手写 HTML，两边的屏序本来就可能有意不同
# （首页与四个项目页就是各自写的），文档层才是「一篇译一篇」的地方。
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
_FENCE_BLOCK = re.compile(r"^```[^\n]*\n(.*?)^```", re.M | re.S)
_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
_CALLOUT = re.compile(r"^>\s*\[!(NOTE|IMPORTANT|WARNING|TIP|CAUTION|DANGER)\]", re.M)
_LIST_ITEM = re.compile(r"^\s*[-*+]\s+", re.M)


def structure(path: Path) -> dict:
    """一页的「结构指纹」—— 与文字无关，只看骨架。"""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    blocks = _FENCE_BLOCK.findall(text)
    tables, run = [], 0
    for line in text.splitlines():
        if line.strip().startswith("|"):
            run += 1
        elif run:
            tables.append(run)
            run = 0
    if run:
        tables.append(run)
    return {
        "标题层级": [len(m.group(1)) for m in _HEADING.finditer(text)],
        "代码块行数": [len(b.strip().splitlines()) for b in blocks],
        "表格行数": tables,
        "列表条数": len(_LIST_ITEM.findall(text)),
        "callout": sorted(_CALLOUT.findall(text)),
        "事实占位符": sorted(set(_PLACEHOLDER.findall(text))),
        "wiki 链接": len(_WIKILINK.findall(text)),
        "链接": sorted(_LINK.findall(text)),
    }


def compare_structures(routes: dict[str, dict[str, str]]) -> tuple[list[str], list[str]]:
    """中英两页的结构对拍 ⇒ (错误, 警告)。"""
    errors: list[str] = []
    warnings: list[str] = []
    for route, pair in sorted(routes.items()):
        if "zh" not in pair or "en" not in pair:
            continue
        zh_rel, en_rel = pair["zh"], pair["en"]
        if not zh_rel.endswith(".md") or not en_rel.endswith(".md"):
            continue  # 手写 HTML 的门脸页不在此列
        a, b = structure(CONTENT / zh_rel), structure(CONTENT / en_rel)
        for key in ("标题层级", "代码块行数", "表格行数", "列表条数", "callout", "事实占位符", "wiki 链接"):
            if a[key] != b[key]:
                errors.append(
                    f"route {route!r}：{key} 对不上 —— 中文 {a[key]} / 英文 {b[key]}"
                )
        if a["链接"] != b["链接"]:
            warnings.append(
                f"route {route!r}：链接集合不同 —— 中文 {a['链接']} / 英文 {b['链接']}"
            )
    return errors, warnings


def main() -> int:
    routes = collect()
    errors: list[str] = []
    warnings: list[str] = []

    # 1. 必须双语的 route —— 点名报
    for route in I18N.TWIN_REQUIRED:
        pair = routes.get(route)
        if not pair:
            errors.append(f"route {route!r}：中英两版都不存在")
            continue
        missing = [lg for lg in ("zh", "en") if lg not in pair]
        if missing:
            errors.append(
                f"route {route!r}：缺 {'/'.join(missing)} 版（现有：{', '.join(sorted(pair))}）"
            )

    # 2. 非豁免 route 必须双语（新增页面不能悄悄单语言）
    #    TWIN_REQUIRED 里点名的 route 规则 1 已经报过了，不重复。
    for route, pair in sorted(routes.items()):
        if I18N.is_exempt(route) or route in I18N.TWIN_REQUIRED:
            continue
        missing = [lg for lg in ("zh", "en") if lg not in pair]
        if missing:
            errors.append(
                f"route {route!r}：缺 {'/'.join(missing)} 版（非豁免 route）"
            )

    # 3. 反向：英文页必须有中文孪生
    for route, pair in sorted(routes.items()):
        if "en" in pair and "zh" not in pair:
            errors.append(f"route {route!r}：有英文版却没有中文版")

    # 4. 豁免名单陈旧
    for route, pair in sorted(routes.items()):
        if I18N.is_exempt(route) and "en" in pair:
            warnings.append(
                f"route {route!r}：已在豁免名单里却有英文版 —— 豁免名单该清了"
            )

    # 5. 源文件要有构建产物
    for route, pair in sorted(routes.items()):
        for lang, rel in sorted(pair.items()):
            out = output_path(rel)
            if not out.exists():
                errors.append(f"content/{rel}：没有构建产物（{out.relative_to(ROOT)}）—— 跑 python tools/build.py")

    # 6. 结构对拍 —— 漏译是没有任何别的门能拦的那类错
    par_err, par_warn = compare_structures(routes)
    errors.extend(par_err)
    warnings.extend(par_warn)

    print(f"孪生页检查：{len(routes)} 个 route")
    if warnings:
        print(f"⚠ {len(warnings)} 条警告：")
        for w in warnings:
            print("   ", w)
    if errors:
        print(f"!! {len(errors)} 条红：")
        for e in errors:
            print("   ", e)
        return 1
    print("✓ 每个页面都有中英两版")
    return 0


if __name__ == "__main__":
    sys.exit(main())
