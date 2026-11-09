---
title: 校验与签名
description: SHA256 怎么核对、签名现状、以及发布产物如何验证来源
layout: docs
project: compiler
zone: download
---

# 校验与签名

这一页回答三个问题：**下载下来的字节是不是完整的**、**发布者是不是预期的那个
发布者**、以及**你手上的编译器是不是这一版**。

第二个问题的答案不太好看，先说在前面。

---

## 签名现状：没有签名

> [!WARNING]
> 安装器和 MSI **都没有代码签名**。Windows SmartScreen 首次运行会弹
> 「Windows 已保护你的电脑」，点「更多信息 → 仍要运行」。
> 未签名二进制也更容易被第三方杀软拦。企业分发策略可能直接拒收未签名 MSI。

具体会碰到什么：

| 场景 | 现象 |
|---|---|
| 个人用户首次运行 | SmartScreen 的蓝底提示框拦一道，需手动「更多信息 → 仍要运行」；「发布者」一栏显示未知发布者 |
| 第三方杀软 | 未签名二进制的启发式误报率明显更高，可能被隔离或要求加白名单 |
| 企业分发 | 很多组织的软件分发策略直接拒收未签名 MSI——不是装不上，是策略层面拉黑 |
| 强制签名环境 | 装不上，除非 IT 侧单独放行 |

**没有** minisign、sigstore、cosign、GPG 签名的 detached signature；
**没有** SLSA provenance、SBOM、attestation。发布流程产出的校验相关资产只有一个：
`SHA256.txt`。

所以本页不会给你一个签名验证流程——因为没有。这是有意的：**用一个不存在的
流程把「没签名」这件事说圆，比直接说没签名更糟。**

### SHA256 能证明什么、不能证明什么

`SHA256.txt` 和它校验的产物是**同一个发布者**提供的。这决定了它的能力边界：

- **能**证明文件在传输中没有损坏、没有截断、不是你下错了版本；
- **不能**证明发布者本人可信——如果有人能改你的下载源，他也能同时改
  `SHA256.txt`。

换句话说，这是**完整性**检查，不是**来源认证**。真要认证来源，得有签名或
transparency log——项目目前两者都没有。

---

## SHA256 怎么核对

每个 release 都带一个 `SHA256.txt` 资产，里面是 `sha256sum` 格式的清单：

```text
<64 位十六进制>  <文件名>
```

两个空格分隔，UTF-8 无 BOM，**LF 换行**（Windows 上生成的，但刻意写成 LF——
CRLF 会让 Linux 上的 `sha256sum -c` 把 `\r` 当成文件名的一部分）。

### bash

把三个产物和 `SHA256.txt` 放在同一个目录，然后：

```bash
sha256sum -c SHA256.txt
```

输出是逐行 `文件名: OK`；任何一行是 `FAILED` 就是对不上。

只核对其中一个文件：

```bash
sha256sum jhyy-installer-{{site_version}}.exe
```

把输出的哈希和 `SHA256.txt` 里那一行比对即可（文件里的哈希是小写）。

> [!NOTE]
> 权威清单是 release 上的那份 `SHA256.txt`。本站 `/downloads/` 下的本地镜像把
> 同一份清单存成 `SHA256SUMS.txt`——文件名不同，内容格式一样。

### PowerShell

一次核对清单里的全部文件：

```powershell
Get-Content .\SHA256.txt | ForEach-Object {
    $p = $_ -split '\s+', 2
    $actual = (Get-FileHash -Algorithm SHA256 -Path $p[1]).Hash.ToLower()
    if ($actual -eq $p[0].ToLower()) { "OK   $($p[1])" } else { "FAIL $($p[1])" }
}
```

单个文件：

```powershell
Get-FileHash -Algorithm SHA256 .\jhyy-installer-{{site_version}}.exe
```

`Get-FileHash` 输出的是**大写**十六进制，`SHA256.txt` 里是**小写**——比对时
统一转小写（上面的命令已经做了）。

---

## 核对失败通常是什么原因

按出现频率排：

1. **下载被截断。** 网络中断、代理缓存、浏览器中断续传都会留下半个文件。
   重新完整下载，不要用续传出来的半截文件。
2. **换行被改了。** `SHA256.txt` 必须是 LF。如果用编辑器打开后保存过（或在
   Windows 上被某些工具转成 CRLF），`sha256sum -c` 会报
   `No such file or directory`——因为它把行尾的 `\r` 当成了文件名的一部分。
   **不要编辑这个文件**，直接对原文件跑校验。
3. **拿到的不是原文件。** 从 GitHub release 的 **HTML 下载页**另存下来的东西
   不保证是发布物本身。用 tag 直链：
   `https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/download/v<版本>/<文件名>`
4. **版本号弄错。** `SHA256.txt` 是**跟着版本走的**——拿旧版本的校验和去对新
   版本的产物，必然对不上。另外归档里 v1.5.5 / v1.5.6 那两次是历史占位，
   资产已 404，清单里的哈希对不上任何现存的下载。
5. **对错了文件。** `SHA256.txt` 列的是三个发布产物：安装器、MSI、VSIX。
   编译器本体 `jhyy.exe` **不是** release 资产——它在安装器里，也在仓库的
   `compiler/build/bin/` 下。

---

## 怎样确认你拿到的确实是这个版本

### 版本横幅

`jhyy --help` 的**第一行**就是版本横幅：

```text
jhyy compiler v{{site_version}} (self-hosted)
```

不带参数直接跑 `jhyy` 打的是同一份帮助文本。

> [!NOTE]
> **没有 `jhyy --version`**——这个子命令不存在。版本横幅只在 `--help` 首行，
> 别去找一个不存在的命令。

### 编译产物里嵌的版本

版本号是编译器源码里的**字符串字面量**（`compiler/src0/main.jhyy` 里
`printf` 出来的那一行），编译时进二进制，所以可以直接在二进制里搜：

```bash
strings jhyy.exe | grep "jhyy compiler v"
```

需要 binutils 的 `strings`（MSYS2 与 Git Bash 里都有）。

### 装完之后

```powershell
where jhyy
jhyy --help
```

`where jhyy` 期望指向 `C:\Program Files\JHYY\bin\jhyy.exe`；`--help` 首行的
版本应当与本页写的当前稳定版一致。

VS Code 扩展那一份看文件名与版本号：产物叫 `jhyy-lang-<版本>.vsix`，扩展内部
的 `version` 字段在打包时对齐同一个版本号（仓库里的
`installer/vscode-ext/package.ps1` 负责改）。

---

## 接下来

- [下载](/compiler/download/index.html)——产物矩阵与下载链接。
- [源码构建与自举](/compiler/download/bootstrap.html)——为什么「编译出来的东西
  自己再编一遍还是一样」是发布前必过的一道门。
