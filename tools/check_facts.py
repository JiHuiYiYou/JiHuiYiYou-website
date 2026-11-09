#!/usr/bin/env python3
"""事实门 —— 官网的 `siteconfig.FACTS` ↔ 编译器仓的 `docs/internal/FACTS.md` 对拍。

**为什么要有这道门**：官网把「回归 279 PASS」「台账 217 条」这类数字抄进了正文。
抄的时候一定会漂 —— 2026-11 编译器仓把回归数从 279 改成 281 之后，官网还写着
279，而链接门过、同步门过、孪生页门过，**没有任何一道门会红**。这道门就是那个红。

编译器仓的真相源（都在 `JiHuiYiYou/` 里）：
  `VERSION`                       版本号唯一真相源
  `docs/internal/FACTS.md` § 1    版本 / 产物 / 发布日期
                     § 2.1        回归与门的数字
                     § 3           问题台账的桶
  `docs/abis/jhyy-*-v*.md`       语言规范 / ABI / 二进制格式的契约版本

用法：
    python tools/check_facts.py               # 对拍
    python tools/check_facts.py --self-test   # 注入一条错值，确认这道门真的会红

找不到编译器仓时**打印「跳过」并退出 0** —— 但 CI 里必须 checkout 它
（见 .github/workflows/site.yml），否则这道门就是空转。
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import siteconfig as C  # noqa: E402

# 受这道门管的键 —— 全部来自编译器仓。
# siteconfig.FACTS 里 IDE / OS / for-VEX 的那几个来自各自的仓，本轮还没 checkout
# 它们进来对拍（见 i18n.py 的说明），所以不在这个列表里。
GATED = (
    "site_version",
    "site_version_date",
    "spec_version",
    "abi_version",
    "binary_format_version",
    "regress_total",
    "regress_pass",
    "regress_skip",
    "regress_failed",
    "assertions",
    "artifact_checks",
    "workarounds_total",
    "workarounds_active",
    "workarounds_deferred",
    "workarounds_resolved",
    "workarounds_superseded",
    "workarounds_invalid",
)


def compiler_repo() -> Path | None:
    """找编译器仓。环境变量优先，其次同级目录。"""
    cands: list[Path] = []
    env = os.environ.get("JHYY_REPO")
    if env:
        cands.append(Path(env))
    cands.append(ROOT.parent / "JiHuiYiYou")
    cands.append(ROOT / "vendor" / "JiHuiYiYou")
    for c in cands:
        if (c / "docs" / "internal" / "FACTS.md").exists():
            return c
    return None


def parse_facts(text: str) -> dict:
    """从 FACTS.md 里抠出受管的那些数字。

    每条都对应 FACTS.md 里的**一张表的某一行** —— 行格式变了就抠不出来，
    抠不出来会被当成漂移报出来（而不是静默跳过）。
    """
    out: dict = {}

    def grab(pattern: str, cast=int):
        m = re.search(pattern, text)
        return cast(m.group(1)) if m else None

    # § 2.1 回归与门
    m = re.search(r"\*\*(\d+) PASS \+ 0 XFAIL \+ 0 failed \+ (\d+) SKIP\*\*（(\d+) total）", text)
    if m:
        out["regress_pass"] = int(m.group(1))
        out["regress_skip"] = int(m.group(2))
        out["regress_total"] = int(m.group(3))
        out["regress_failed"] = 0
    out["assertions"] = grab(r"扫描 \d+ · 可跑 \d+ · 真断言 (\d+)")
    out["artifact_checks"] = grab(r"产物级门数 \| `?artifact-checks`?[^|]*\*\*(\d+) 道\*\*")

    # § 3 问题台账
    out["workarounds_total"] = grab(r"条目总数 \| \*\*(\d+)\*\*")
    out["workarounds_active"] = grab(r"\| ACTIVE \| \*\*(\d+)\*\*")
    out["workarounds_deferred"] = grab(r"\| DEFERRED \| (\d+) \|")
    m = re.search(r"\| RESOLVED / SUPERSEDED / INVALID \| (\d+) / (\d+) / (\d+) \|", text)
    if m:
        out["workarounds_resolved"] = int(m.group(1))
        out["workarounds_superseded"] = int(m.group(2))
        out["workarounds_invalid"] = int(m.group(3))

    # § 1 版本与发布
    m = re.search(r"最新 release \| `v([\d.]+)`（([\d-]+)）", text)
    if m:
        out["site_version"] = m.group(1)
        out["site_version_date"] = m.group(2)

    return {k: v for k, v in out.items() if v is not None}


def parse_abi_versions(repo: Path) -> dict:
    """契约版本 —— 真相源是 docs/abis/ 下的文件名（文件名的版本号就是契约版本）。"""
    out: dict = {}
    abis = repo / "docs" / "abis"
    if not abis.is_dir():
        return out
    for key, prefix in (
        ("spec_version", "jhyy-lang-spec-v"),
        ("abi_version", "jhyy-abi-v"),
        ("binary_format_version", "jhyy-binary-format-v"),
    ):
        for p in sorted(abis.glob(prefix + "*.md")):
            out[key] = p.stem[len(prefix):]
            break
    return out


def collect_truth(repo: Path) -> dict:
    facts_md = (repo / "docs" / "internal" / "FACTS.md").read_text(encoding="utf-8")
    truth = parse_facts(facts_md)
    truth.update(parse_abi_versions(repo))
    ver = repo / "VERSION"
    if ver.exists():
        truth["site_version"] = ver.read_text(encoding="utf-8").strip()
    return truth


def compare(truth: dict) -> list[str]:
    """官网的 FACTS 与编译器仓的真相逐项对拍。"""
    diffs: list[str] = []
    for key in GATED:
        want = C.FACTS.get(key)
        got = truth.get(key)
        if got is None:
            diffs.append(f"{key}: 编译器仓里抠不出这一项（FACTS.md 的行格式可能变了）")
        elif want is None:
            diffs.append(f"{key}: 官网的 FACTS 里没有这一项")
        elif str(want) != str(got):
            diffs.append(f"{key}: 官网 {want!r} ≠ 编译器仓 {got!r}")
    return diffs


def self_test() -> int:
    """注入一条错值，确认这道门真的会红 —— 不会红的门比没有门更糟。"""
    truth = collect_truth(compiler_repo()) if compiler_repo() else {}
    if not truth:
        print("!! 自测需要编译器仓 —— 找不到，跳过")
        return 2
    doctored = dict(truth)
    doctored["regress_pass"] = 1  # 故意写错
    diffs = compare(doctored)
    if not diffs:
        print("!! 自测失败：注入了错值，这道门却没有报出来 —— 门是坏的", file=sys.stderr)
        return 1
    print(f"✓ 自测通过：注入错值后这道门报出了 {len(diffs)} 条")
    for d in diffs:
        print("   ", d)
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()

    repo = compiler_repo()
    if repo is None:
        print("::notice::找不到编译器仓（docs/internal/FACTS.md），跳过事实对拍")
        print("::notice::CI 里必须 checkout JiHuiYiYou/JiHuiYiYou-compiler，否则这道门空转")
        return 0

    truth = collect_truth(repo)
    diffs = compare(truth)
    if diffs:
        print(f"!! 事实漂移 {len(diffs)} 条：")
        for d in diffs:
            print("   ", d)
        print(f"   （真相源：{repo / 'docs' / 'internal' / 'FACTS.md'}）")
        return 1
    print(f"✓ 事实一致（{len(GATED)} 项，对拍源：{repo}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
