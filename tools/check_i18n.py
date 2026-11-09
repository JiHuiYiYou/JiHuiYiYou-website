#!/usr/bin/env python3
"""i18n 一致性 lint —— 三档严格度，理由各不相同。

| 规则 | 级别 | 为什么是这个级别 |
|---|---|---|
| **字面量事实**：正文里手写了「4.1.4 / 279 / 299」这类特征数字 | 错误 | 这些数字在本站没有别的含义 ⇒ 误报率≈0 ⇒ 可以当硬错误。**这是保证「两种语言不可能对不上数字」的主力机制** |
| **英文页里出现中文** | 错误 | 「翻译没做完」的唯一可靠信号，误报≈0（代码块 / 行内代码 / HTML 属性 / 注释除外） |
| **术语说法不一致** | 警告 | 中文页合法地用英文技术词（arena / no_std）⇒ 一刀切会误报 |

用法：
    python tools/check_i18n.py
    python tools/check_i18n.py --dump-glossary   # 打印术语表（贴进 CONTENT_GUIDE 用）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import i18n as I18N  # noqa: E402

# CJK 汉字 + CJK 标点 + 全角形式（不含日文假名以外的非汉字字符）
CJK = re.compile(r"[⺀-鿿豈-﫿＀-￯]")


def code_spans(text: str) -> list[tuple[int, int]]:
    """代码与 URL 的字符区间 —— 里面的数字是代码/标识符，不是「叙述的事实」。"""
    spans: list[tuple[int, int]] = []
    for pat in (r"```.*?```", r"`[^`\n]*`", r"https?://\S+"):
        for m in re.finditer(pat, text, flags=re.S):
            spans.append(m.span())
    return spans


def tag_spans(text: str) -> list[tuple[int, int]]:
    """HTML 标签（含属性）区间。"""
    return [m.span() for m in re.finditer(r"<[^>]*>", text, flags=re.S)]


def in_spans(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(a <= pos < b for a, b in spans)


def line_of(text: str, pos: int) -> int:
    return text[:pos].count("\n") + 1


def literal_pattern(lit: str) -> re.Pattern:
    """特征字面量的匹配模式。

    数字边界用「前后不挨数字或小数点」而不是 `\\b` —— 因为 `v4.1.4` 里的
    版本号前面是字母（`\\b` 会把它挡掉）。
    """
    return re.compile(r"(?<![\d.])(?:" + re.escape(lit) + r")(?![\d.])")


def check_literal_facts() -> list[str]:
    """正文里不该手写事实 —— 要写 {{key}}。"""
    problems: list[str] = []
    for rel in I18N.FACT_LINT_SCOPE:
        path = ROOT / rel
        if not path.exists():
            continue  # 还没写的页面 —— 孪生页门管这个
        text = path.read_text(encoding="utf-8")
        spans = code_spans(text)
        for lit, key in I18N.LITERAL_FACTS.items():
            for m in literal_pattern(lit).finditer(text):
                if in_spans(m.start(), spans):
                    continue
                problems.append(
                    f"{rel}:{line_of(text, m.start())}: 手写了 {lit!r} —— 用 {{{{{key}}}}} 占位符"
                )
    return problems


def check_en_has_no_cjk() -> list[str]:
    """英文页的正文里不该出现中文。"""
    problems: list[str] = []
    en_root = CONTENT / "en"
    if not en_root.is_dir():
        return problems
    for path in sorted(en_root.rglob("*")):
        if path.suffix not in (".md", ".html"):
            continue
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        spans = code_spans(text) + tag_spans(text)
        for m in CJK.finditer(text):
            if in_spans(m.start(), spans):
                continue
            ctx = text[max(0, m.start() - 20): m.start() + 20].replace("\n", " ")
            problems.append(
                f"{rel}:{line_of(text, m.start())}: 英文页里出现中文 {m.group(0)!r} —— 上下文：…{ctx}…"
            )
    return problems


def twins() -> dict[str, dict[str, Path]]:
    """route → {语言: 源文件}"""
    out: dict[str, dict[str, Path]] = {}
    for path in sorted(CONTENT.rglob("*")):
        if path.suffix not in (".md", ".html"):
            continue
        rel = path.relative_to(CONTENT).as_posix()
        out.setdefault(I18N.route_of(rel), {})[I18N.lang_of(rel)] = path
    return out


def check_glossary() -> list[str]:
    """术语说法不一致 —— 只警告。"""
    warns: list[str] = []
    pairs = twins()
    for route, pair in sorted(pairs.items()):
        if "zh" not in pair or "en" not in pair:
            continue
        zh_text = pair["zh"].read_text(encoding="utf-8")
        en_text = pair["en"].read_text(encoding="utf-8")
        for key, forms in I18N.GLOSSARY.items():
            zh_term, en_term = forms["zh"], forms["en"]
            if zh_term == en_term:
                continue  # 两种语言同一个词（arena）—— 没有「说法不一致」这回事
            zh_has = zh_term in zh_text
            en_has = en_term in en_text
            if zh_has and not en_has:
                warns.append(
                    f"route {route!r}：中文页用了 {zh_term!r}，英文页却没用术语表里的 {en_term!r}"
                )
            if zh_has and en_term in zh_text:
                warns.append(
                    f"route {route!r}：中文页同时出现 {zh_term!r} 和 {en_term!r} —— 一个概念只准一种说法"
                )
    return warns


def dump_glossary() -> int:
    """打印术语表（Markdown），贴进 tools/CONTENT_GUIDE.md 用。"""
    print("| 概念 | 中文 | English |")
    print("|---|---|---|")
    for key, forms in I18N.GLOSSARY.items():
        print(f"| `{key}` | {forms['zh']} | {forms['en']} |")
    print()
    print("以下词两种语言都不译（`KEEP_EN`）：")
    print()
    print("、".join(f"`{k}`" for k in sorted(I18N.KEEP_EN)))
    return 0


def main() -> int:
    if "--dump-glossary" in sys.argv:
        return dump_glossary()

    errors = check_literal_facts() + check_en_has_no_cjk()
    warns = check_glossary()

    if warns:
        print(f"⚠ 术语警告 {len(warns)} 条：")
        for w in warns:
            print("   ", w)
    if errors:
        print(f"!! {len(errors)} 条红：")
        for e in errors:
            print("   ", e)
        return 1
    print("✓ i18n 一致性检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
