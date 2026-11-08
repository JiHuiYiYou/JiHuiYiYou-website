---
title: JiHuiYiYou-for-VEX
description: 让 JHYY 直接跑在 VEX V5 Brain 上——实测优先的嵌入式目标路线
layout: page
project: vex
zone: vex
---

给 JHYY（机会翼游）加一个**嵌入式目标**：VEX V5 Brain。当前进度是**第 0 步已完成** ——
把 VEX 侧的未知数全部变成实测值，写成一份事实基线。

## 目标硬件

VEX V5 Brain：ARM，**Xilinx Zynq**（Cortex-A9 + FPGA），有 VFPv3 + NEON。
DDR 基址 `0x03800000`（`lscript.ld` 里的 `ps7_ddr_0_S_AXI_BASEADDR`），
入口钉在 `0x03800020`。

## 路线 B 是「JHYY 直出 ARM 机器码」

不是「转译成 C++」。但边界要说清 —— **换掉的是 clang 的位置，`ld` 及以下原样不动**：

- **A 路**（第 0 步，黄金参考）：JHYY → C 源码 → clang → `.bin`
- **B 路**（目标）：JHYY → ARM 机器码（`.o`）→ 官方 SDK → `.bin`

B 路出的是 ARM `.o`，然后链官方 SDK 的 `lscript.ld` / `stdlib_0.lib` / `libv5rt.a`，
最后 objcopy 出 `.bin`。

这跟 pros-rs 当年的**同构**（Rust 出 `.o`、链 libpros）是一个路子，区别是**带着实测重走**，
不带它的沉没成本。

⇒ 推论也一致：**ABI 必须锁死**（softfp）、**入口必须锁死**（符号名 `main`）、
**绑定面必须锁死**（每个 `extern fn` 逐字对应一个 C 符号）—— 链哪份库就认哪份 ABI。
这三样锁不住，两路就没法对拍。

## Day 0 已完成：事实基线

[`docs/00-事实基线.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-for-VEX/blob/main/docs/00-%E4%BA%8B%E5%AE%9E%E5%9F%BA%E7%BA%BF.md)
是这个项目「会变的数字与平台事实」的**唯一真相源**。测量日期 **2026-11-08**，
机器 **Windows 10 + MSYS2**，测量方式全部是本机实测（编译 / 反汇编 / `readelf` / `nm`），
**零 JHYY 变量**。凡未实测的条目一律标「待测」，不写推测值。

规格书要覆盖八件事，缺一不可 —— **七件已有结论，一件待测**：

- 产物格式与签名布局 —— 已实测
- `vexStartup` 替你干了什么 —— 已实测（反汇编 + 重定位）
- 符号修饰规则 —— 已实测（C++ mangled 1404 个 vs 纯 C API）
- softfp / hard 的决定及依据 —— **已锁定 softfp**
- struct 传参的 C 对齐 —— 已实测（布局 + 寄存器约定 + 唯一那个按值 struct）
- 最小绑定面 —— 已核实确切函数名 + JHYY 侧逐字对应的清单
- 场控状态从哪读 —— `vexCompetitionStatus` / `vexCompetitionControl`
- 消息泵 tick 频率 —— **待测**（需实机）

几条实测结论：

- **产物格式不需要额外转换器** —— SDK 的 `objcopy` 直出最终格式。头 32 字节是 `XVX5` + 版本 1，
  入口紧跟其后在 `0x03800020`。
- **启动链完全闭合**：清 `.bss` → stdlib 版本校验 → newlib impure data → `__libc_init_array`
  → `vexMain` → `__libc_fini_array`。
- **用户的 `main` 是一个 task**，不是主线程 —— SDK 用 `vexTaskAdd(main, 2, "MAIN")` 把它注册进
  VEXos 调度器。所以 B 路**必须发射一个不带修饰的 `main` 符号**。
- **ABI 锁定 softfp** —— 我们的 ELF 与 `libv5rt.a` 都没有 `Tag_ABI_VFP_args` 标签，
  按 ARM ABI 缺省即 base standard variant。
- **指令集是 ARM 态、4 字节定长** ⇒ 后端不必做 Thumb-2 变长编码。
- **API 两层**：C++ `vex::`（1404 个 mangled 符号，**不碰**）和**纯 C `vex*()`**
  —— 后者 JHYY 的 `extern fn` 直接绑，**零胶水层**。
- **struct 布局实测**：packed 与非 packed 都有；C API 里**只有一个**按值传的 struct
  （`V5_DeviceVisionRgb`，≤4 B ⇒ 寄存器传参），其余一律指针传递。
- **内存预算**：堆 1 MB，栈 14 KB —— 递归深度是硬约束。
- **JHYY 侧的硬约束**（ABI v4.0.0）：不支持变参、不支持 struct 按值跨 FFI，
  且**指针宽度锁死 64 位** ⇒ ARM 目标必须先把指针宽度定成 4 字节，否则连 `extern fn` 都对不上。

## 三条坑（都在原文里被明确警告过）

1. **MSYS2 自带的 `objdump` 是 x86-only** —— 对 VEX 产物会报
   `can't disassemble for architecture UNKNOWN!` ⇒ **必须用 `arm-none-eabi-objdump`**
   （本次是额外装的，binutils 2.47）。`readelf` 两边都能读。
2. **SDK 的 clang 是 8.0.0**，flags 里写着 `-target thumbv7-none-eabi`（一个 **Thumb** 目标），
   但实测入口处是 **ARM 态**指令（`e59f00a0` 是 ARM 态 LDR literal，Thumb-2 会是 `f8df`）。
   「目标说 Thumb、实测产物是 ARM」这个组合依赖具体版本的 codegen 行为 ——
   **换 clang 版本必须重测**，不能把这条结论直接搬过去。
3. **实测环境是 Windows 10 + MSYS2** —— 工具链路径、shell、objcopy 的行为都跟这个环境绑定。

## 后续排期

- **Day 0** —— 已完成。手写 C 探针，零 JHYY 变量，纯手工走通 `源码 → ELF → 带签名 bin → program.bin`。
  探针里还顺手做了绑定面本身的一层：屏显 API 全是变参，而 JHYY 不支持变参调用，
  所以加了一个**非变参封装** `jhyy_vex_display_puts` —— 变参只发生在 C 内部。
- **Day 1–2** —— 未开始。emitter 发 **C**（不发 C++），最小子集 + 最小绑定面
  （先只绑 `vexDeviceGetByIndex` / `vexDeviceMotorVelocitySet` / `vexDelay` / `jhyy_vex_display_puts`）。
- **Day 3** —— 未开始。A 路产物跟现有 C++ 工程的行为对照，补齐 Day 0 遗留的待测项，规格书定稿。
- **B 阶段** —— 未开始。JHYY 的 ARM 后端。

Day 3 的对拍口径先说清：**「一致」指的是行为，不是字节**。A 路和 B 路是两个不同的代码生成器
（`.s` 必然不同，`.o` 段布局也可能不同），所以 `.s` / `.o` / ELF / `.map` / `.bin` 五层产物
是**各自的诊断证据**，不是逐字节比对对象 —— 逐层比对只是为了**定位**不一致发生在哪一层。

Day 0 还有一条**验收线**没过：**A 路产出的 `.bin` 必须真的在 Brain 上转过电机**。
这件事需要 microSD 卡和一台机器人 —— 屏显与电机的实机行为、消息泵 tick 频率、
`vexDisplayPrintf` 的坐标语义都还标着「待测」。

Day 0 的探针可以复现（产物本地留存，不进版本库）：

```bash
scripts/build-vex.sh spike/day0-c day0c
```

## 边界与纪律

- **不直接改 JHYY 主仓** —— 实验在本仓做，拿到实测再回主仓落地，单独评审。
- **第 0 步的产出是知识，不是代码** —— emitter 是探针，不许长成产品。
- **产物本地留存，不进版本库** —— `.bin` / ELF 含 `libv5rt.a` 的代码（VEX 专有），
  在「SDK 再分发」拍板前不进公开 repo；留存靠**本地 + 可复现脚本 + 哈希清单**。

仓库：<https://github.com/JiHuiYiYou/JiHuiYiYou-for-VEX>
