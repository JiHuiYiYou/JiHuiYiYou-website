---
title: 裸机与内核开发
description: freestanding 目标、no_std、内联汇编与最小内核启动路径
layout: docs
project: compiler
zone: docs
---

「能不能用它写内核」这个问题在 JHYY 上要拆成三层看：**语言层**、**运行时层**、
**ABI 层**。三层各管各的，混成一句「无标准库」就会得出错误结论。这页把三层
分开说清楚，再逐条核实「最小内核启动路径」上哪些真的能用、哪些目前还是空的。

一句话预告：**语言层的零件基本齐了，运行时层和链接层还没接上。**

---

## 1. 三层要分开

| 层 | 开关 | 管什么 | 明确不管什么 |
|---|---|---|---|
| **语言层** | 源文件里的 `#[no_std]` 属性 | 声明「这个模块不要 C 运行时」，并把入口符号换成 `main` | 不决定调用约定，不决定链接器 |
| **运行时层** | 目标名里的 `_freestanding` 后缀 | 「没有操作系统运行时」这个目标形态 | **不切链接方式** |
| **ABI 层** | `--target=<triple>` | 选哪套 calling convention（MS x64 / SysV AMD64） | 不切 PE / ELF 产出（那由宿主 `ld` 决定） |

ABI § 1 的原话：**两个 freestanding 目标只切换「调用约定归属 + 入口钩子」，不切换
链接方式。** 换句话说，`--target=amd64_win_freestanding` 跟 `amd64_win` 的寄存器
约定**逐字节相同**，差别在别处（见第 2 节）。

---

## 2. 链接行由 `#[no_std]` 决定，不由 `--target` 决定

| 源文件里有 `#[no_std]` 吗 | 链接行 |
|---|---|
| 没有 | 链 `runtime.o` + `helpers.o`，再无条件追加 `-lm -lkernel32 -luser32 -lshell32 -ladvapi32` |
| 有 | `-nostartfiles -nodefaultlibs -Wl,--entry=main -lgcc`，**不**链 runtime / helpers |

第二行的 `--entry=main` 是因为 codegen 按函数名**原样**发符号 —— 用户的
`fn main` 就是 `main`。`#[no_std]` 模块必须定义 `fn main`，否则 sema 报
`error: #[no_std] module must define 'fn main()'`。

注意第二行**末尾仍然无条件追加** `-lm -lkernel32 -luser32 -lshell32 -ladvapi32`。
⇒ 真正的 UEFI / 裸机镜像**不能**用这个链接行，得自己用 lld-link
（`/SUBSYSTEM:EFI_APPLICATION /ENTRY:efi_main`）或自定义链接行完成。

### 一个实测出来的坑

`#[no_std]` 的链接行分支是靠一个 side-file 标志传过去的
（`compiler/build/obj/_no_std.flag.<pid>`），而**这个路径是相对当前工作目录的**。

- 在编译器仓库根目录跑 `jhyy compile ns.jhyy` ⇒ 走 no_std 链接行 ⇒ 链接成功，程序返回 42，进程退出码 42。
- 在任何一个没有 `compiler/build/obj/` 子目录的地方跑同一条命令 ⇒ 标志文件写不出来 ⇒ **回落到托管链接行** ⇒ 链接失败（`collect2.exe: error: ld returned 5 exit status`），退出码 1。

这不是设计意图，是路径相对于 CWD 的副作用。写文档的时候把它记下来，是因为它
很容易被误读成「`#[no_std]` 编不过」。

---

## 3. 已知缺口（诚实披露）

| 缺口 | 状态 |
|---|---|
| **UEFI EFIAPI wrapper 未实装**（ABI § 12.8） | `emit_entry_point` / `no_crt_init` 两个钩子**都是空实现** ⇒ 编译器不生成 wrapper，也不自动抑制 CRT / runtime 链接。entry 符号由用户自行提供 |
| **真正的裸机链接行** | 做不到 —— 见第 2 节（Windows 系统库无条件追加） |
| **交叉目标链接** | **故意拒绝**：非 `amd64_win` 的目标不带 `--no-link` 直接报错、退出 1 |
| **panic handler** | 语言里**没有 panic 概念**。`compiler/runtime/no_std_core/panic_handler.jhyy` 是一个 M0 stub（死循环），而且**没有接进构建** —— 链接行里没有它 |
| **串口输出** | 仓里没有 UART / COM1 / `0x3f8` 的任何代码。`std/io.jhyy` 的注释写明「OS kernel M11 launch 后再换 syscall 实现」 |
| **`#[naked]` 的符号落位** | 见第 5 节：函数体在 `.s` 里**没有标签** |
| **`.bss` 清零 / 起始栈** | 没有 CRT 启动代码 ⇒ 两样都没有（见第 6 节） |

这些不是「暂时没写」，是**明确登记在案**的边界。ABI § 12 的偏离表是权威清单。

---

## 4. 可用的裸机语言面

| 特性 | 状态 | 限制 |
|---|---|---|
| `#[no_std]` | 可用 | 模块级属性；必须定义 `fn main` |
| `#[link_section("...")]` | 可用 | 只改符号落入的 section，**不改调用约定**。section 名必须是可打印 ASCII |
| `volatile T` | 可用 | 只修饰**基础类型**（修饰 struct / 指针 / 数组是编译错误）；布局与 `T` 完全一致；保证单线程内每次访问命中内存、不重排。跨线程要配 `fence_*` |
| `asm!("...")` | 可用但受限 | 单个字符串字面量；**没有操作数约束、没有 clobber 声明**；AT&T 语法；x86-64 only。返回值语义未定义 ⇒ 惯例写在语句位置 |
| `fence_seq_cst()` / `fence_acquire()` / `fence_release()` | 可用 | 分别发射 `mfence` / `lfence` / `sfence`；只覆盖 x86-64 |
| `#[naked]` | 能编，但有缺口 | 见第 5 节 |
| `defer` | 可用 | 只覆盖**显式 `return`** 路径；函数体末表达式的**隐式返回不触发** defer |

实测产物（`volatile` + `asm!` + `fence` 一起用）：

```asm
	movl %eax, (%r8)      # volatile store —— 真的写内存，不进寄存器缓存
nop                    # asm!("nop") —— 内联在当前位置
mfence                 # fence_seq_cst() —— 内联在调用点
	movl (%r8), %eax      # volatile load
```

`asm!` 和 `fence_*` 都是**内联在函数体当前位置**（ABI § 8）。这不是便利问题 ——
早期实现把它们 append 到 `.s` 末尾，落在所有函数之外成为死字节，**内存屏障从未
执行过**。现在这条已经修好。

---

## 5. `#[naked]`：能编，但符号落位目前不对

`#[naked]` 的契约：无 prologue / epilogue，完全控制寄存器与栈；函数体**只能**含
`asm!(...)` 语句（局部变量 / 控制流 / `return` 是编译错误）。

实测 `jhyy build` 出来的 `.s`：

```asm
pushq %r15
iret
.text
.balign 16
.globl main_jhyy
main_jhyy:
	...
```

`irq_entry:` 这个标签**没有出现** —— 函数体以**文件作用域**的形式落在 `.text`
之前。链接后的 exe 里 `<irq_entry>` 指向的是一段对齐填充（`nop`），不是函数体。

⇒ 结论：`#[naked]` 目前能编译，但**裸中断入口还不能真正被调用**。
回归用例 `compiler/tests/examples/naked_interrupt_entry.jhyy` 只断言进程退出码 0
—— harness 看不到符号落位，所以这一条没被门挡住。

---

## 6. 最小内核启动路径：逐条核实

| 环节 | 状态 | 依据 |
|---|---|---|
| 入口符号 | **用户自己提供**。UEFI 场景 `efi_main`，裸机 / Linux ELF 场景 `_start` | 语言规范 § 17.6 |
| `#[no_std]` 下的入口 | `main`（链接行 `-Wl,--entry=main`）；sema 强制要求 `fn main` | ABI § 7 |
| 栈设置 | **待补充**。没有 CRT 启动代码 ⇒ 没有起始栈。`fn main` 自己会生成标准前导（`pushq %rbp` / `movq %rsp, %rbp` / `subq $N, %rsp`），但**起始栈**要 firmware 或用户代码提供 | 链接行 `-nostartfiles` |
| panic handler | **未实装**。见第 3 节 | `no_std_core/panic_handler.jhyy` 未接进构建 |
| 串口输出 | **未实装**。见第 3 节 | 仓里没有 UART 代码 |
| `.bss` 清零 | **待补充**。同样因为没有 CRT 启动代码 | — |
| 中断 / IDT / 页面表 | **待补充**。语言层面没有相关设施 | — |

---

## 7. 实证参考：UEFI x64 引导 spike

`JiHuiYiYou-OS/spike/boot.s` 是一个**手写的 GNU 汇编**文件
（`.intel_syntax noprefix`），**不是** JHYY 代码。它的价值在于钉死了 UEFI x64
入口的真实寄存器约定：

```asm
efi_main:
    # RCX = EFI_HANDLE ImageHandle
    # RDX = EFI_SYSTEM_TABLE *SystemTable
    mov     r12, rdx                   # r12 = ST
    mov     rax, [r12 + 64]            # ConOut (NOT StdErr at 80)
    ...
    call    [r13 + 8]                  # OutputString
```

- **入口约定**：RCX = ImageHandle，RDX = SystemTable —— 跟 `amd64_win_freestanding` 的 MS x64 约定对得上。
- **构建行**：`x86_64-w64-mingw32-gcc -nostdlib -Wl,--subsystem,10 -Wl,-e,efi_main -Wl,--image-base=0x10000 -o BOOTX64.EFI boot.s`。
- **退出码**：`out 0xf4, al`（isa-debug-exit）把状态传给 QEMU。
- **栈**：spike 自己 `push rbp / mov rbp, rsp` 建帧，**没人替它建起始栈**。

对照 JHYY 侧：编译器**没有**生成 EFIAPI wrapper 的代码（ABI § 12.8），所以从
`.s` 到 `.efi` 这一段目前要手写。

---

## 8. OS / 嵌入式能力现状表

| 能力 | 现状 |
|---|---|
| `#[no_std]` 模块编译 + 链接 | **可用**（实测：链接成功，退出码 42） |
| 自定义入口符号（`efi_main` / `_start`） | **可用** —— 用户自己写，编译器不生成 |
| `#[link_section]` 放启动代码 | **可用**（实测：`.section .text.boot` 出现在 `.s` 里） |
| `volatile` 访问 MMIO | **可用**（实测：真的走内存读写） |
| 内联 `asm!` | **可用**，受限于单字符串字面量 |
| 内存屏障 | **可用**（`mfence` / `lfence` / `sfence` 内联在调用点） |
| `#[naked]` 中断入口 | **不可用**（符号落位不对） |
| panic / 断言 / 栈回溯 | **未实装** |
| 串口 / UART 输出 | **未实装** |
| 中断控制器 / IDT / 页面表 | **未实装** |
| 多核 / SMP | **未实装** |
| aarch64 / riscv64 裸机 | **未实装**（只有 x86-64） |
| UEFI 镜像自动产出 | **未实装**（入口路径未完工，ABI § 12.8） |

---

## 9. 相关页面

- [CLI 参考](/compiler/docs/cli.html) —— `--target=` 的四个取值与交叉目标的 `--no-link` 用法。
- [ABI v4.0.0](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v4.0.0.md) —— § 7 是入口与链接，§ 8 是底层扩展，§ 12 是偏离表。
- [语言规范 v4.0.0](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md) —— § 17 是 `volatile` / `asm!` / `#[naked]` / `#[link_section]` / `#[no_std]` / 内存屏障 / freestanding entry。
- [目标与交叉编译](/compiler/download/targets.html) —— 四个目标的产物形态。
