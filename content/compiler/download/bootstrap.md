---
title: 源码构建与自举
description: 从源码构建编译器，以及两阶段自举闭环怎么跑
layout: docs
project: compiler
zone: download
---

# 源码构建与自举

这一页讲怎么从源码把编译器编出来，以及「自举闭环」到底**证明**什么、
**不证明**什么。第二件事比第一件重要。

---

## 构建前置

| 需求 | 说明 |
|---|---|
| 宿主 | **Windows x64**——`jhyy.exe` 是 PE 可执行文件，自举闭环必须能执行它 |
| MSYS2 | 构建宿主。**这是「从源码构建编译器」的需求；用安装器装编译器不需要 MSYS2** |
| `mingw-w64-ucrt-x86_64-gcc` | C 编译器 |
| `mingw-w64-ucrt-x86_64-binutils` | as / ld / objdump 等 |

```bash
pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-binutils
```

> [!IMPORTANT]
> **不要**用 Git Bash 自带的那个 MinGW `gcc`
> （`/c/Program\ Files/Git/mingw64/bin/gcc.exe`）——它不支持 PE+ 链接，
> 会**一字不印**地卡在链接阶段。

> [!WARNING]
> PATH 里**先出现哪个 `gcc` / `ld` 就用哪个**。Windows runner 镜像自带旧 MSYS2
> 在 `C:\mingw64` 且排在前面，是最常见的翻车姿势。构建时把 MSYS2 根目录显式
> 传下去。

---

## 构建

```bash
git clone https://github.com/JiHuiYiYou/JiHuiYiYou-compiler.git
cd JiHuiYiYou-compiler
make all        # → compiler/build/bin/jhyy.exe（~2 MB）
```

`make` 现在只有两个 target：

| target | 做什么 |
|---|---|
| `all` | 默认目标：编 `runtime.o` / `helpers.o`，跑自举闭环检查，产出 `jhyy.exe` 与它的副本 `jhyy_v1.exe.exe` |
| `clean` | 清构建产物（**保留** `jhyy.exe`——删了仓库当场不可用） |

`make stage0`、`make selfhost`、`make test` **都已经删掉了**，别照着旧文档找：
C 端编译器在 v4.0.21 整体删除，`stage0` 随之消失；`selfhost` 与 `test` 在
2026-11-03 删除——前者跑的检查 `make` 自己已经保证（恒绿的门是噪音），
后者原本只是一句 `echo "TODO: test runner"` 的空壳。

### 目录结构

**本仓没有 stage0 了。** 引导件就是仓库里**已提交的那份**
`compiler/build/bin/jhyy.exe`——fresh clone 里就有，它是 git 跟踪的产物。
编译器**自己**编 `compiler/src0/`：

```
JiHuiYiYou-compiler/
├── compiler/
│   ├── src0/                   编译器源码（唯一实现，31 个模块）
│   │   ├── std/                标准库 {{stdlib_modules}} 个模块：mem / fmt / io / math / string / vec / os / arena
│   │   └── codegen_amd64_*.jhyy 自研后端：IL lexer / emit_* / peephole / 寄存器缓存
│   ├── runtime/runtime.c       C 运行时（arena + main 入口）
│   ├── src0/jhyy_helpers.c     C 桥：编译器与 Win32 之间的 extern
│   ├── tests/
│   │   ├── examples/           回归用例 {{regress_total}} 条
│   │   └── bootstrap/          fixed_point.sh · closure_check.sh · artifact_checks.sh · byte_equal*.sh
│   └── build/
│       ├── obj/                预编 _jhyy_runtime.o / _jhyy_helpers.o
│       └── bin/                jhyy.exe（git 跟踪的锚点）+ jhyy_v1.exe.exe（每次 make 生成的同内容副本）
├── runtime/linux_elf/          Linux ELF 运行时（crt0.S + link.ld）
├── bench/                      基准套件
├── regress.py                  回归测试套件（仓库根）
└── installer/                  WiX 安装器 + 内置 ucrt64 工具链
```

`jhyy_v1.exe.exe` 的双扩展名不是笔误：`make` 每次构建都重新生成它（是
`jhyy.exe` 的逐字节副本），本地几个闭环门按这个名字引用它。

---

## 自举闭环

`make` 的 `jhyy.exe` 规则做三件事：

1. 把**当前这个**（已提交的）`jhyy.exe` 复制成 `_boot_anchor.exe`；
2. `_boot_anchor.exe` 编 `src0/main.jhyy` → `_boot_new`（连 `.s`），
   `_boot_new.exe` 再编一遍 → `_boot_new2`（连 `.s`）；
3. **闭环检查**：`cmp -s _boot_new.s _boot_new2.s`——新编译器编 src0 的产物必须
   与它自己编的**逐字节相同**。

第三步不是「编两代比一次」，而是**迭代到不动点**：不相等就把锚点推进一代，
最多 3 轮；**收敛的那一轮，第 N 代就是不动点**（第 N+1 代与它同产物），
装它是对的。3 轮仍不收敛 ⇒ 硬失败。

> [!IMPORTANT]
> **不动点是跑出来的，不是假设出来的。** 而且这一步带非空守卫：比两个**空
> 文件**也会判「相同」，编译器「静默 exit 0 但不产 `.s`」时会假绿——
> 2026-11-03 才补上这道守卫。

后面还有一道**漂移检查**：当 `src0` / `runtime` 与 HEAD 一致时，新产物必须与
**提交进仓的那份**逐字节相同，否则 `make` 失败（`STRICT_TOOLCHAIN=1`，默认开）。
CI 传 `STRICT_TOOLCHAIN=0`——不是放宽判据，是划清职责：CI 不发布，它验的是
提交进仓的那份产物；漂移检查管的是「这个编译器该不该被发布」，不是「能不能
编出来」。

比 `.s` 不比 `.exe`，是刻意的：`.s` 是（源码 × 编译器）的函数，与宿主 gcc 版本
无关；`.exe` 是（源码 × gcc 版本）的函数，跨 toolchain 比必假阳性。

---

## 三道闭环门分别在哪跑

| 脚本 | 判据 | 在哪跑 |
|---|---|---|
| `compiler/tests/bootstrap/fixed_point.sh` | N=10 跨代 `.il` + `.s` 逐字节相等（另加 `cap_test.jhyy` 跨代退出码 = 42）。N=3 是主门，N=4..10 是信息项 | **本地门**：`python regress.py --fixed-point` |
| `compiler/tests/bootstrap/closure_check.sh` | `v2.s == v3.s`（Stage 2 与 Stage 3 逐字节相同） | **本地门**：`bash compiler/tests/bootstrap/closure_check.sh` |
| `compiler/tests/bootstrap/artifact_checks.sh` | {{artifact_checks}} 道产物级断言（expected-FAIL 模型） | **CI 门**：`bash compiler/tests/bootstrap/artifact_checks.sh` |

> [!NOTE]
> `fixed_point.sh` 与 `closure_check.sh` **都不接 CI**。前者是发版级流程
> （改 `src0` 之后跑），后者在 2026-11-03 从 CI 里删掉了——CI 里那道闭环由
> `make` 自己兜，再单跑一遍只是复述同一个结论，恒绿的门是噪音。
> `artifact_checks.sh` 才是 CI 门，{{artifact_checks}} 道产物级断言在 CI 里跑。

`artifact_checks.sh` 的价值在于它验的失效模式**不在程序返回值里**，而在产物
的字节布局里：per-fn 表 1024 上限那类缺陷，写 `.jhyy` 用例会 PASS（结果全对、
递归深度没变），只有 `.s` 里 `subq $N, %rsp` 从 8368 跳到 96928 才看得出。

---

## 确定性 ≠ 正确性

这条是本页最重要的一句。

**自举闭环证明的是「世代确定性」**：同一份源码，第二代与第一代产出的汇编
逐字节相同。

**它不证明语义正确性。** 一个确定性的错误编译器也能完美闭环——把 `+` 编译成
`-`，两代照样一致。这是经典的 trusting trust 缺口。

语义正确性由**回归套件**覆盖：**{{regress_pass}} PASS / {{regress_failed}} FAIL / {{regress_skip}} SKIP，共 {{regress_total}} 条**。
断言强度审计另外统计了 **{{assertions}} 条真断言**，零信号用例 0 条（没有一个用例在没检查
任何东西的情况下报通过）。

```bash
python regress.py                       # 全量回归
python scripts/dev/audit_test_assertions.py --strict   # 断言强度审计
```

两条门分工明确：**闭环管「同一份源码两次编译一样」，回归管「编译出来的东西
行为对不对」。** 前者过了后者没过，说明编译器稳定地做错同一件事；后者过了
前者没过，说明 emit 层有不确定性——两种情况都得停。

---

## 可复现构建要固定什么

仓库里能确证的部分：

| 固定项 | 值 / 做法 |
|---|---|
| 时间戳 | `SOURCE_DATE_EPOCH = 1234567890`（Makefile 里钉死；编译器在拉起链接子进程前也会设它） |
| 调试信息 | `-g0`——否则 mingw-w64 CRT 链进来的构建路径会破坏逐字节比对 |
| build-id | `-Wl,--build-id=none`——同上 |
| 编译标志 | `CFLAGS_REPRO = -std=c11 -Wall -Wextra -g0 -Wl,--build-id=none` |
| 工具链布局 | gcc 按自身位置推导 `cc1` / `collect2` / `as` / `ld`；工具链目录**不能拍平**，`ucrt64/` 这一层**不能改名** |

> [!NOTE]
> 完整的**跨机可复现**还差一环：`.exe` 是（源码 × gcc 版本）的函数，换一个
> gcc 版本编出来的东西必然不同。所以跨机比对要比 `.s`，不能比 `.exe`。
>
> 另外，仓库目前**没有**随 tarball 分发一份「提交态 sha 清单」——从
> GitHub codeload 下来的压缩包没有 git 元数据，字节级漂移检查没有参照物，
> `make` 会明确提示「跳过」而不是假装通过。

---

## 接下来

- [构建与测试](/compiler/docs/build-and-test.html)——仓库里的完整构建与测试说明。
- [目标与交叉编译](/compiler/download/targets.html)——四个 target 与裸机工具链。
- [校验与签名](/compiler/download/verify.html)——发布产物怎么核对。
