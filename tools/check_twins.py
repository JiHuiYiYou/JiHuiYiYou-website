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

下一轮把文档层也译出来 = 删掉 `i18n.TWIN_EXEMPT_PREFIXES` 那几行，
门逻辑一行不用动。

用法：
    python tools/check_twins.py
"""
from __future__ import annotations

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
