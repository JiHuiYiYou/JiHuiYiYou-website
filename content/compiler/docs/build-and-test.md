---
title: 构建与测试
description: 从源码构建编译器，跑回归与自举闭环门
layout: docs
project: compiler
zone: docs
---

# 构建与测试

这一页讲的是**改编译器**。只是**用**编译器，见 [[快速上手]]。

---

## 环境要求

**宿主：** Windows 10 + MSYS2（`C:\msys64\mingw64\bin\bash.exe`），外加
`mingw-w64-ucrt-x86_64-gcc` 与 `mingw-w64-ucrt-x86_64-binutils`。

```bash
pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-binutils
```

> [!IMPORTANT]
> **不要**用 Git Bash 自带的那个 MinGW `gcc`
> （`/c/Program\ Files/Git/mingw64/bin/gcc.exe`）——它不支持 PE+ 链接，会在链接阶段失败。

---

## 构建

```bash
git clone https://github.com/JiHuiYiYou/JiHuiYiYou-compiler.git
cd JiHuiYiYou-compiler
make all        # → compiler/build/bin/jhyy.exe
```

`make` 不只是编译：它会**把自举闭环迭代到不动点**。编译器编译自己，编译出来的那个
再编译自己，构建一直迭代，直到连续两代产出的汇编**逐字节相同**。这就是整个项目的
立身之本——不动点是跑出来的，不是假设出来的。

`make clean` 清掉构建产物。

工具链的完整故事——查找顺序、经典坑、多目标构建、版本号自动化——在仓库的
[构建文档](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/build.md)里。

---

## 测试

```bash
python regress.py                       # 全量
python regress.py --tests=hello.jhyy    # 单个用例
python regress.py --all                 # 带上受门控的用例
python regress.py --byte-equal          # 比对 .il / .s / .exe 三层
python regress.py --fixed-point         # 跨代不动点检查
```

> [!IMPORTANT]
> **测试要从仓库根目录跑。** 脚本按当前目录解析路径；在子目录里跑会把所有文件报成
> 缺失，看起来像漂移，其实不是。

测试覆盖 `compiler/tests/examples/` 下每一个 `.jhyy` 文件（下划线开头的辅助 fixture
除外）。通过数和门的清单写在
[FACTS.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md)
里——那是唯一写数字的地方。

### 断言强度

```bash
python scripts/dev/audit_test_assertions.py --strict
```

一个不可能失败的测试比没有测试更糟——它什么都没查却报成功。这个审计会报出多少用例
带着真断言，并在出现「零信号」用例时判红。

---

## 那些门

项目很清楚「测试全绿」比听上去弱得多，所以外面围了一圈**门**。完整且当前的清单在
[FACTS.md § 2](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md)
——CI 门和需要手工跑的本地门在那里分开列。

最值得知道的三道：

| 门 | 它证明什么 |
|---|---|
| **自举闭环** | 编译器精确地复现自己——这是关于生成确定性的陈述，不是关于语义正确性 |
| **产物新鲜度** | 提交进仓的那份 `jhyy.exe` 行为与按当前源码现编出来的一致 |
| **全量回归** | 真正的语义——语义回归是这一道抓的 |

> [!NOTE]
> 「编译器把自己编译得逐字节相同」**并不**意味着编译器是对的。一个确定性的错误编译器
> 也能完美闭环。这是经典的 "trusting trust" 缺口，由另一道门覆盖：回归套件。

---

## 交叉编译到 Linux

产出不限于 Windows。`amd64_sysv*` 目标产出 SysV 汇编，可以在 Linux 上链接并运行，
一共三步：

```bash
# 1. 在 Windows 上 —— 只产出 .s（交叉目标不能链接）
./compiler/build/bin/jhyy.exe compile --target=amd64_sysv_freestanding --no-link prog.jhyy -o prog
#    ⇒ prog.s

# 2. 在 Linux 上 —— 链成静态 ELF
gcc -nostdlib -static -T runtime/linux_elf/link.ld -o prog.elf \
    runtime/linux_elf/crt0.S prog.s

# 3. 跑起来
./prog.elf
```

CI 在 Linux 上跑的就是这条链——见
[`compiler/tests/bootstrap/sysv_link_run.sh`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/compiler/tests/bootstrap/sysv_link_run.sh)。

Linux 运行时调的是 `main_jhyy`（不是 `main`），并以它的返回值退出，所以入口约定与
托管侧一致——但链接是 `-nostdlib`，所以 freestanding 程序不能调 libc。

---

## 发一个版本

版本号**不是手改的**。仓库根的 `VERSION` 是单一真相源，下面这个顺序不能反：

```bash
python scripts/dev/bump_version.py set <新版本号>   # ① 刷 VERSION 与各处版本串
make                                            # ② 编译器把版本编进去
pwsh -File installer/build.ps1 bundle           # ③ 构建产物
python scripts/dev/bump_version.py finalize     # ④ 回填实测的校验和与体积
python scripts/dev/bump_version.py check        # ⑤ 零漂移门
```

> [!WARNING]
> **不能跳过第 ② 步。** 版本是编译器源码里的字符串字面量，自举产物必须重编——否则
> 编译器报的还是上一个版本，第 ⑤ 步的漂移门会（正确地）判红。

---

## 周边工具

### Claude Code 的 MCP 服务

`mcp-jhyy/` 把编译器暴露给 AI 编码助手：编译、运行、检查语法、导出中间表示、跑回归套件、
查 workaround 台账、查询语言规范与 ABI。

```bash
pip install fastmcp     # ⚠️ 不是 `mcp[cli]` —— fastmcp 是另一个分发包
```

细节见 [mcp-jhyy/README.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/mcp-jhyy/README.md)。

### VS Code 扩展

`vscode-ext/` 提供语法高亮、原生的 ▶ **Run JHYY File** 命令（`Ctrl+F5`）和
**Compile JHYY File (no run)** 命令。装编译器安装包时也会一并装上扩展。

---

## 接下来

- [[架构]] —— `make` 到底在构建什么。
- [[常见问题]] —— 关于构建与运行的问题。
- [CONTRIBUTING.md](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md)
  —— 贡献者的工作流程。
