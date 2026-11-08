---
title: JiHuiYiYou-OS
description: 用 JHYY 写的操作系统——从 UEFI 引导 spike 开始的实测路线
layout: page
project: os
zone: os
---

用 JHYY（机会翼游）写的操作系统。**它现在处在极早期** —— 仓库里只有一个 UEFI x64 引导 spike，
设计基线正在重整。这一页写的是**现状**，不是蓝图。

## 仓库里现在有什么

仓库当前只有一个目录 `spike/`（外加一份 MIT 协议的 `LICENSE`）：

- `spike/boot.s` —— UEFI x64 引导程序，Intel 语法。
- `spike/BOOTX64.EFI` —— 上面那个源文件的编译产物。
- `spike/esp_root/EFI/BOOT/BOOTX64.EFI` —— EFI 分区镜像里的引导文件。
- `spike/wrap_gpt.py` —— 把一份裸 FAT 镜像包进带**一个 EFI System Partition** 的 GPT 磁盘镜像（自己写保护 MBR、主/备 GPT 头和 CRC32，还会把 FAT 的 BPB 隐藏扇区数改成分区起始 LBA）。

最近一次提交（2026-10-30）就是 **「清空原有设计文档 —— 重整设计基线」**：一次性删掉了
`docs/` 下 17 份 v0.0.x 设计文档、`deep_research/` 下 9 份外部调研存档，外加 `README.md`
和 `CLAUDE.md`。那批文档写于编译器 v1.8.3 时代（C 宿主 + QBE + ABI v1.0.0），
里面大量结论已被推翻或过时。

内容没丢，**全在 git 历史里**：`24589bd` 是删除前的最后状态，`git show 24589bd:docs/<file>` 可以考古。
跨项目的设计基线现在单点落在编译器仓的 `docs/coordination/`。

## spike 已经实测到的四件事

`spike/boot.s` 的头注释里列的就是这个 spike 要验证的四件事：

1. **UEFI x64 直接以 long mode 交接**，不需要模式切换汇编。
2. **EFI 调用约定是 MS x64**：入口处 `RCX` = 第一个参数（ImageHandle），`RDX` = SystemTable。
3. **ConOut 函数指针按 `[protocol + offset]` 访问可用** —— 但偏移是 **+64，不是 +80**。
   +80 是 **StdErr**；OVMF 的 ConSplitter 没给图形控制台注册 StdErr，写进去只到串口，
   在 GOP framebuffer 上**看不见**。这个 +64 / +80 是实测踩出来的，代码注释里专门标了 CRITICAL。
4. **`isa-debug-exit` 端口 `0xf4` 能把退出码传给 QEMU**。

> 诚实补充：当前提交的 `boot.s` 最后是一个 `hlt` 死循环 —— 屏幕上打出 `HELLO` / `OK` 给人看，
> 注释里写明「自动化验证时把它换成 `out 0xf4, al`」。也就是说第四条在代码里**留了位置**，
> 但这份提交走的是给人看的那条路。

spike 里做的事其实只有三步，全是对着 ConOut 协议打函数指针：**ClearScreen**（偏移 48，
先擦掉 TianoCore 的启动画面）、**SetAttribute**（偏移 40，白字亮红底 `0xCF`）、
**OutputString**（偏移 8，打 `HELLO` 和 `OK`）。头注释把这个 spike 标成 **P0-1** ——
它是 OS 线的第一个待验证点，不是产品的一小块。

## 构建

`boot.s` 注释里给的就是这条（可粘贴）：

```bash
x86_64-w64-mingw32-gcc -nostdlib -Wl,--subsystem,10 \
  -Wl,-e,efi_main -Wl,--image-base=0x10000 -o BOOTX64.EFI boot.s
```

`--subsystem,10` 是 EFI application，`-e,efi_main` 指定入口。

打出来的 `BOOTX64.EFI` 放进 `esp_root/EFI/BOOT/`，再由 `wrap_gpt.py` 把分区内容包成
一张可启动的 GPT 磁盘镜像。

## 方向（尚未成文为 OS 仓自己的设计文档）

下面这些是**方向**，不是已冻结的实现方案：

- **能力微内核 + `Cap<T>` capability** —— 编译器仓的[《JHYY OS 侧设计终版》](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/coordination/JHYY_OS%E4%BE%A7%E8%AE%BE%E8%AE%A1%E7%BB%88%E7%89%88.md)把内核身份锁定成
  「能力微内核（长期）+ 特权分层（首版）」，理由是三份规范（语言规范 v4.0.0 / ABI v4.0.0 /
  二进制格式 v1.0.0）已经提供对象分类 `type_tag`、cap 授权 `rights`/`depth`、IPC 原地 cap 传输
  这套完整授权链条 —— 走传统混合内核，这套二进制格式会退化成装饰。
- **lang-debug ABI** —— [语言规范 § 19](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v4.0.0.md)的「Debug ABI」是跨项目契约：尺寸定案、`jhyy` 侧的
  类型表达、编译器不生成 DWARF debug info、FFI 边界提醒。
- **GUI** —— 对象骨架（`compositor` / `surface` / `seat` / `buffer`）足以搭一条双缓冲显示管线，
  但**完整的桌面还没被规范定义**。

那份设计文档同时把该由首次架构冻结回答的问题**列了出来**（线程与地址空间是否分离、内核对象是否统一
header、revoke 是否同步、中断是不是 capability、page fault 归内核还是用户 pager……）——
它们现在还没有答案。`.jhyynb` 这个 capability 启动格式本身也还是**设计稿、未实装**。

排期上，整条 OS 线（编译器 [`docs/internal/FACTS.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/FACTS.md) § 4.3 里的 **OS-1 … OS-16** 十六个版本槽）
排在编译器的 v4.6 → v4.15，**一个都还没开始**。

想看旧的那批设计稿（v0.0.x 时代写的，C 宿主 + QBE + ABI v1.0.0 背景，多数结论已被推翻），
考古命令：

```bash
git show 24589bd:docs/README.md
```

## 语言面

写内核需要的语言特性，JHYY 这一侧已经在了：`#[no_std]`、freestanding 目标、`#[naked]`、
`#[link_section]`、`volatile`、内联 `asm!`、内存屏障。
怎么用它们写裸机代码，见[裸机与内核开发](/compiler/docs/osdev.html)。

## 现状小结

- 仓库里**只有** `spike/` 一个目录 —— 一个能打出 `HELLO` 的 UEFI 引导程序。
- 设计文档已被清空重整，路线图待重写。
- 没有可安装、可运行的东西，也没有任何发布渠道。

仓库：<https://github.com/JiHuiYiYou/JiHuiYiYou-OS>
