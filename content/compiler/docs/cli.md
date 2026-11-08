---
title: CLI 参考
description: jhyy 编译器的命令、子命令、选项与退出码
layout: docs
project: compiler
zone: docs
---

`jhyy` 只有一个二进制、四个子命令、两个全局选项。下面是逐条核实过的行为表 ——
含产物名和退出码 —— 以及三个会咬人的命令行怪癖。

---

## 1. 命令表

| 命令 | 用途 | 产物 |
|---|---|---|
| `jhyy compile <file.jhyy> [-o output]` | 编译 + 链接 | `<output>.exe`；中间的汇编（`<output>` + `.s`）也留在盘上 |
| `jhyy build <file.jhyy> [-o base]` | 只编译，**不**链接 | `<base>.s` |
| `jhyy run <file.jhyy>` | 编译 + 链接 + 执行 | 临时产物 `<name>_run.exe`（跑完留在盘上） |
| `jhyy dump <file.jhyy>` | 只解析，打印 AST 树 | 打到 stdout |

不带 `-o` 时，输出名取输入文件的基名：`jhyy compile hello.jhyy` ⇒ `hello.exe`，
`jhyy build hello.jhyy` ⇒ `hello.s`。

`-o` 是**基名**，后缀自动补：`-o foo` ⇒ `foo.s` / `foo.exe`；`-o foo.s` ⇒ 仍是
`foo.s`（不会变成 `foo.s.s`），`-o foo.exe` ⇒ `foo.exe`（旁边的汇编是 `foo.exe.s`）。

---

## 2. 三个子命令的差别（重点）

`compile` / `build` / `run` 是同一条流水线的三个切点：

```text
.jhyy → lex → parse → sema → IL → 自研 amd64 后端 → .s → gcc + ld → .exe
                             └── build   = 到 .s 为止
                                        └── compile = 再走 gcc + ld
                                                     └── run = 再执行
```

| | `build` | `compile` | `run` |
|---|---|---|---|
| 解析 + 语义分析 | 是 | 是 | 是 |
| 生成 `.s` | 是 | 是 | 是 |
| 调 gcc / ld 链接 | 否 | 是 | 是 |
| 执行 | 否 | 否 | 是 |

### 两条等价路径

```bash
jhyy build   x.jhyy -o out            # ⇒ out.s
jhyy compile --no-link x.jhyy -o out  # ⇒ out.s
```

两条产出的 `.s` **逐字节相同** —— 包括 `#[link_section]` 生成的 `.section` 指令
（两条路径都套用同一段 section 处理）。仓库里有一条 artifact check
（`link_section_build`）钉住这个等价关系。

实测：对一个同时带 `#[link_section]` 和 `#[naked]` 的文件，两条路径的 `.s`
`cmp` 结果是完全一致。

### 一个和帮助文案不一致的地方

`jhyy --help` 里写的是 `compile ... (a lib without main is compiled only)`。
实测：拿一个**没有 `main_jhyy`** 的文件跑 `jhyy compile`，`.s` 确实产出了，但链接
步骤照样会跑并失败（`collect2.exe: error: ld returned 1 exit status`），退出码 1。
⇒ 想只拿汇编，用 `jhyy build` 或 `jhyy compile --no-link`。

---

## 3. 选项

| 选项 | 作用 |
|---|---|
| `--target=<triple>` | 选目标，默认 `amd64_win`。**位置任意**（子命令前后都行）；给多个时**最后一个生效** |
| `--no-link` | 只产出 `.s`，跳过链接。**位置任意**（子命令前后都行） |
| `--help` | 打印完整帮助并退出 0。**任意位置**都能触发 —— `jhyy --help` 和 `jhyy compile --help` 打的是同一份 |

不带任何参数跑 `jhyy` 打的也是**同一份**完整帮助。

### 四个目标

| 三元组 | 调用约定 | 运行时 | 这份构建能链接吗 |
|---|---|---|---|
| `amd64_win` | MS x64 | hosted（链 C 运行时） | 能（唯一能链的） |
| `amd64_sysv` | SysV AMD64 | hosted | 不能，必须 `--no-link` |
| `amd64_win_freestanding` | MS x64 | freestanding（UEFI） | 不能，必须 `--no-link` |
| `amd64_sysv_freestanding` | SysV AMD64 | freestanding | 不能，必须 `--no-link` |

freestanding 相关的三点：

1. **freestanding 只切「调用约定归属 + 入口钩子」，不切链接方式。** 链接行由源文件里有没有 `#[no_std]` 决定 —— 详见 [裸机与内核开发](/compiler/docs/osdev.html)。
2. **交叉目标故意拒绝链接**。不带 `--no-link` 直接报错、退出 1：

   ```text
   jhyy: refusing to link a cross target - this build's linker always emits a Windows .exe (via the bundled toolchain).
         Use --no-link, then link the .s with a toolchain that matches the target.
   ```

3. `--target` **不切换 PE / ELF 产出** —— 容器格式由宿主 `ld` 决定（ABI § 12.9）。

### 完整的交叉编译三步

```bash
# 1. 在 Windows 上出 .s（交叉目标必须带 --no-link）
jhyy compile --target=amd64_sysv_freestanding --no-link prog.jhyy -o prog
#    ⇒ prog.s

# 2. 在 Linux 上链成静态 ELF
gcc -nostdlib -static -T runtime/linux_elf/link.ld -o prog.elf \
    runtime/linux_elf/crt0.S prog.s

# 3. 跑
./prog.elf
```

---

## 4. 三个必须知道的怪癖

### 4.1 没有 `jhyy --version`

它从来就不存在。跑它会打：

```text
jhyy: unknown option --version
(try `jhyy --help`)
```

然后**退出 1**。版本横幅在 **`jhyy --help` 的第一行** —— 不带参数跑 `jhyy` 打的是
同一份帮助，banner 也在第一行。

### 4.2 命令行只接受一个输入文件

多余的 `.jhyy` 参数被**静默忽略** —— 不报错、不警告。实测
`jhyy compile --no-link main.jhyy lib.jhyy -o multi` 退出码 0，产出的 `multi.s`
里只有 `main_jhyy` 的符号，`lib.jhyy` 定义的 `lib_helper` 一个字都没有。

多文件请用 `import` 组合：在 `main.jhyy` 里写 `import lib;`，编译器沿 import 图
把 `lib.jhyy` 一起编进来。

### 4.3 不认识的选项会被拒绝

```text
$ jhyy compile --foo main.jhyy
compile: unknown option --foo
(try `jhyy --help`)
```

退出 1。它**不会**把这个 flag 当成文件名去打开。`build` 和 `run` 各有自己的前缀
（`build: unknown option --foo` / `run: unknown option --foo`）。

---

## 5. 退出码

| 情形 | 退出码 |
|---|---|
| `--help` / 无参数 | 0 |
| `build` / `compile` 成功 | 0 |
| `run` 成功 | **被运行程序的退出码** |
| 未知选项 / 未知命令 / 未知 target | 1 |
| 语法错误 / 语义错误 | 1（诊断打到 stderr，带 `file:line:col`） |
| 文件打不开 | 1 |
| 交叉目标拒绝链接 | 1 |
| 链接失败 | 1 |

`jhyy run` 会把被运行程序的退出码原样传出来：程序 `return 42` ⇒ `jhyy run` 退出 42。

诊断长这样：

```text
bad.jhyy:1:33: error: unexpected token ';' in expression
bad.jhyy:1:29: error: expected ;, got return
parse errors
```

另外两条错误路径的措辞：

```text
$ jhyy compile                        # 没给输入文件
usage: jhyy compile <file.jhyy> [-o output] [--no-link]

$ jhyy frobnicate x.jhyy             # 未知子命令
jhyy: unknown command 'frobnicate'
(commands: compile / build / run / dump - try `jhyy --help`)
```

> **关于「退出码和 clang 一致」**：README、README.zh-CN、CHANGELOG 和两份规范里
> **都没有**这条表述。实测出来的语义就是上面这张表 —— 成功 0、失败 1，`run` 额外
> 透传被运行程序的退出码。

> **在 MSYS2 bash 里取退出码要小心**：bash 会把退出码截成 8 位（`值 & 0xFF`）。
> 要精确的退出码，用 harness 或 Python `subprocess`，别读 `$?`。

---

## 6. 速查

```bash
# 编译并链接成 exe
jhyy compile hello.jhyy

# 只出汇编（交叉目标必须走这条）
jhyy build hello.jhyy -o hello
jhyy compile --no-link --target=amd64_sysv_freestanding hello.jhyy -o hello

# 编译 + 链接 + 跑
jhyy run hello.jhyy

# 只看语法树
jhyy dump hello.jhyy

# 看编译器自己的帮助（版本横幅在第一行）
jhyy --help
```

---

## 7. 相关页面

- [快速上手](/compiler/docs/getting-started.html) —— 装好之后的第一个程序。
- [裸机与内核开发](/compiler/docs/osdev.html) —— `--target=` 的四个取值、`#[no_std]` 与 freestanding。
- [目标与交叉编译](/compiler/download/targets.html) —— 四个目标的产物形态。
- [编译器实现](/compiler/docs/compiler.html) —— 命令行之后，编译器自己是怎么搭的。
- [语言规范 v4.0.0](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md) —— § 16 是命令行的权威定义。
