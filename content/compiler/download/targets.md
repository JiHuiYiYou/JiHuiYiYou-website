---
title: 目标与交叉编译
description: {{targets_count}} 个 target 的取舍、freestanding 的含义与裸机工具链最小组合
layout: docs
project: compiler
zone: download
---

# 目标与交叉编译

这一页回答四个问题：**目标只有哪几个**、每个目标产出什么、**freestanding 到底
改了什么**、以及裸机构建最少需要哪些工具。

---

## 目标边界：只有 amd64

当前只有{{targets_count}} 个目标，全部是 x86-64。**没有 aarch64、没有 riscv64、没有 wasm。**

| 目标三元组 | ABI | 产物 | 状态 | 说明 |
|---|---|---|---|---|
| `amd64_win` | MS x64 | PE/COFF 可执行文件（`.exe`） | 稳定 | 宿主默认目标。编译器自身就跑在这个目标上 |
| `amd64_sysv` | SysV AMD64 | SysV 汇编（`.s`）→ 外部 ld 链成 ELF | 稳定 | 产物是汇编文本，链接由外部 linker 完成 |
| `amd64_win_freestanding` | MS x64 | UEFI 可执行映像（`.efi`） | 测试中 | 调用约定与 `amd64_win` 逐字节相同；UEFI 入口路径尚未完工（ABI § 12.8） |
| `amd64_sysv_freestanding` | SysV AMD64 | freestanding 汇编（`.s`） | 测试中 | 裸机内核的主要入口目标；同样存在 UEFI 入口缺口 |

{{targets_count}} 个目标**全部**走自研的 amd64 后端（`target_backend_mode` 一律返回
`BACKEND_SELF`），没有 QBE 回退路径——QBE 早已从构建链里移除。

> [!IMPORTANT]
> 这是**当前的边界**：编译器本体只有 amd64 后端。ARM 目标在另一个项目里推进——
> [for-VEX](/vex/index.html) 走的是 JHYY 直出 ARM 机器码（`.o`）再链官方 SDK
> 出 `.bin`，那条路线目前停在事实基线阶段，ARM 后端还没动手。
> 「多架构 ABI」在发行计划里是 v4.16 之后的未排期项。

ABI 侧对此有明确登记：§ 12.10「无 aarch64 / riscv64」，`.jhyynb` 原生二进制格式
至今仍是设计稿。

---

## freestanding 改了什么

这是最容易读错的一条。**freestanding 只切换「调用约定归属 + 入口钩子」，
不切换链接方式。**

链接行到底怎么走，判据是**源文件里有没有 `#[no_std]`**，跟 `--target` 无关
（ABI § 7）：

| 源文件 | 链接行 |
|---|---|
| 没有 `#[no_std]` | 链 `runtime.o` + `helpers.o`（C 运行时 bridge） |
| 有 `#[no_std]` | 不链上面两个，加 `-nostartfiles -nodefaultlibs -Wl,--entry=main -lgcc` |

两条分支都带同一串链接标志：

```text
-g0 -Wl,--build-id=none -Wl,--stack,67108864 … -lm -lkernel32 -luser32 -lshell32 -ladvapi32
```

**Windows 系统库与 `-lm` 是无条件加的**，`#[no_std]` 也不例外。所以真正的
freestanding 镜像得自己用 `lld-link` 或自定义链接行完成。

由此推出两条实操结论：

- **输出容器格式不由 `--target` 决定**，而由宿主机工具链的 `ld` 决定
  （`link_with_gcc` 没有 target 参数，ABI § 12.9）。表里的 PE / ELF 只是各目标的
  惯例产出。
- **非 `amd64_win` 的目标必须显式加 `--no-link`。** 不加的话编译器会直接拒绝：

  ```text
  jhyy: refusing to link a cross target - this build's linker always emits a Windows .exe (via the bundled toolchain).
        Use --no-link, then link the .s with a toolchain that matches the target.
  ```

  这道守卫是有来由的：拿 Windows 链接器去链 SysV 汇编，编出来的东西**编译期
  零告警、运行时段错误**。

---

## 交叉到 Linux

`amd64_sysv*` 目标产出 SysV 汇编，在 Linux 上链接并运行。一共三步：

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

Linux 运行时调的是 `main_jhyy`（不是 `main`），并以它的返回值退出，所以入口
约定与托管侧一致——但链接是 `-nostdlib`，所以 freestanding 程序不能调 libc。

CI 在 `ubuntu-latest` 上跑的就是这条链。

> [!NOTE]
> **编译器本身只在 Windows 上跑。** `jhyy.exe` 是 PE 可执行文件，自举闭环必须
> 执行它；C 端编译器已删除，不存在「用 Linux gcc 编出原生 ELF 版 jhyy」这条路。
> 不受此限的是**产物**。

---

## 裸机工具链最小组合

要真正编出一个裸机镜像，最少需要下面这些。逐条对照 JHYY 的现状：

| 环节 | 需要什么 | JHYY 现状 |
|---|---|---|
| 编译器本体 | `jhyy.exe` | 自举锚点，`compiler/build/bin/jhyy.exe`（仓库里就有一份） |
| 汇编器 | **自研 amd64 发射器** | 后端直接吐 GAS / AT&T 语法的 `.s`，没有独立的汇编器二进制 |
| 系统汇编器 | GNU `as`（经 `gcc -c` 调用） | 只有在把 `.s` 变成目标文件时才用得上 |
| 目标链接器 | 见下 | 外部 `ld`，由宿主工具链决定容器格式 |
| `objcopy` / `objdump` | binutils | 编译本身**不需要**：`objdump` 只在产物级门里用来反汇编核对，`objcopy` 出现在 for-VEX 的 ARM 路线（官方 SDK 自带） |
| QEMU | `qemu-system-x86_64` | 跑 UEFI 镜像用，**不是**编译环节 |
| UEFI 固件 | OVMF（`edk2-x86_64-code.fd` + `edk2-vars.fd`） | 仓库里的 `scripts/dev/install/install-freestanding-toolchain.sh` 从 MSYS2 的 QEMU share 里拷进来 |
| GRUB / limine | 无 | **仓库里没有**，主线走 OVMF + QEMU；OS 项目的 spike 用的是自己那份 `BOOTX64.EFI` |

**裸机构建仍然需要外部 ld。** ABI § 7 写得很直白：链接行是 gcc 的 as + ld，
`link_with_gcc` 没有 target 参数，输出容器由宿主机 `ld` 决定。JHYY 自己只负责
「把源码变成 `.s`」，从 `.s` 到可执行映像这一段全部是外部工具链的活。

三种目标各自需要哪个链接器：

| 目标 | 链接器 | 命令形态 |
|---|---|---|
| `amd64_win` | 宿主 gcc → ld（PE） | 编译器自己链，产出 `.exe` |
| `amd64_win_freestanding` | `lld-link` | `lld-link /SUBSYSTEM:EFI_APPLICATION /ENTRY:efi_main /MACHINE:X64` |
| `amd64_sysv*` | 外部 gcc / ld（ELF） | 在 Linux 上用 `-nostdlib -static` + 自己的 `link.ld` |

UEFI 那条路的完整四步，仓库里已经写成脚本：

```bash
# 1. jhyy compile → .s
scripts/dev/build/build-efi.sh compiler/tests/examples/hello-freestanding/efi.jhyy
# 2. gcc -c .s → .obj     3. gcc -c efi_helpers.s → .obj
# 4. lld-link → .efi
# 然后：
scripts/dev/test/run-ovmf.sh hello-freestanding.efi
```

`lld-link` 来自 MSYS2 的 `mingw-w64-x86_64-lld` 包；`run-ovmf.sh` 用 QEMU 起
EDK2，靠 debugcon 抓 ConOut。

---

## 已知缺口

freestanding 侧还没完工的部分，ABI § 12 都登记着：

- **§ 12.8 · UEFI EFIAPI wrapper 未实装**：freestanding 的两个钩子
  （`emit_entry_point` / `no_crt_init`）**都是空实现**——编译器不生成 EFIAPI
  wrapper，也不自动抑制 CRT / runtime 链接。entry 符号由用户自行提供
  （`efi_main` / `_start`）。
- **§ 12.9 · 无交叉编译容器后端**：`--target` 不切换 PE / ELF 产出。
- **§ 12.10 · 无 aarch64 / riscv64**。
- **§ 12.1 · struct / enum 返回值在所有目标无条件走 sret**，无大小阈值；
  跨语言互操作时与 SysV 标准不符。
- **§ 12.6 · 栈槽只保证 8 字节对齐**（当前没有 16 字节对齐的类型，未触发）。

---

## 接下来

- [ABI v{{abi_version}}](/compiler/docs/abi.html)——契约原文。
- [裸机与内核开发](/compiler/docs/osdev.html)——写裸机程序时的实际做法。
- [源码构建与自举](/compiler/download/bootstrap.html)——从源码编编译器。
