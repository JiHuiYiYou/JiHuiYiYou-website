#!/usr/bin/env python3
"""把文档里的 `.jhyy` 代码块抽出来，逐个交给真编译器验一遍。

改版报告 §9 的一条硬要求：「文档示例的可执行验证必须一期做」。
文档里的代码如果编不过，读者照抄就白费一次——这是最便宜也最该自动化的
一类回归。

用法：
    python tools/check_examples.py            # 只检查
    python tools/check_examples.py --run      # 顺便执行（示例必须能跑出预期）

代码块分三类：
    runnable  —— 完整程序（有 fn main_jhyy），编译 + 执行
    compile   —— 有入口但会崩/需要特权，只编译不执行
    snippet   —— 片段（只有函数签名或局部代码），跳过
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

# 编译器位置：先看环境变量 JHYY，再退回本机开发时的默认路径。
JHYY = Path(
    os.environ.get("JHYY")
    or r"C:\Users\liuzhen\Desktop\coding\JiHuiYiYou\compiler\build\bin\jhyy.exe"
)

BLOCK = re.compile(r"```(jhyy|rust)\n(.*?)```", re.S)

# 明确跳过编译的片段：只展示签名 / 片段 / 故意写错的反例
SKIP_HINTS = (
    "fn arena_reset(a: *Arena) -> i32",     # 签名表里的行
    "arena::Arena { ... }",                  # 文档里说明「解析不了」的反例
)


def classify(code: str) -> str:
    if "fn main_jhyy" in code:
        return "runnable"
    return "snippet"


def extract() -> list[tuple[str, int, str, str]]:
    """抽出所有 .jhyy 代码块。

    **按代码内容去重** —— 中英两棵树里同一段示例会各出现一次，
    编两遍是纯浪费；但英文页的示例同样要编（它坏了英文读者也照抄不动）。
    """
    out = []
    seen: set[str] = set()
    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for m in BLOCK.finditer(text):
            code = m.group(2)
            if code in seen:
                continue
            seen.add(code)
            line = text[: m.start()].count("\n") + 1
            out.append((path.relative_to(ROOT).as_posix(), line, code, classify(code)))
    return out


def main() -> int:
    if not JHYY.exists():
        print(f"!! 找不到编译器：{JHYY}", file=sys.stderr)
        return 2

    run = "--run" in sys.argv
    blocks = extract()
    failures = []
    skipped = 0
    checked = 0

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for rel, line, code, kind in blocks:
            if any(h in code for h in SKIP_HINTS):
                skipped += 1
                continue
            if kind == "snippet":
                skipped += 1
                continue

            src = td / f"ex_{checked}.jhyy"
            src.write_text(code, encoding="utf-8")

            r = subprocess.run(
                [str(JHYY), "compile", str(src), "-o", str(td / f"ex_{checked}.exe")],
                capture_output=True,
                text=True,
                cwd=str(td),
            )
            if r.returncode != 0:
                failures.append((rel, line, "编译失败", (r.stdout + r.stderr)[-500:]))
                checked += 1
                continue

            if run:
                r2 = subprocess.run(
                    [str(td / f"ex_{checked}.exe")], capture_output=True, text=True
                )
                if r2.returncode != 0:
                    failures.append(
                        (rel, line, f"运行退出码 {r2.returncode}", (r2.stdout + r2.stderr)[-500:])
                    )
            checked += 1

    print(f"示例检查：{checked} 个编译，{skipped} 个跳过（片段或反例）")
    if failures:
        print(f"!! {len(failures)} 个没过：")
        for rel, line, why, out in failures:
            print(f"   {rel}:{line}  {why}")
            for l in out.strip().split("\n")[-6:]:
                print("      ", l)
        return 1
    print("✓ 文档示例全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
