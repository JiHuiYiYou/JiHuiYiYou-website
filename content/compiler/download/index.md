---
title: 下载
description: 最新稳定版的产物矩阵、校验方式与包管理器入口
layout: docs
project: compiler
zone: download
---

# 下载

这一页是当前稳定版的产物矩阵：三个可下载的文件、两条分发渠道，以及一条每个用户
都会先撞上的签名说明。版本号以本页为准；历史版本见 [archive](#archive)。

> [!WARNING]
> 安装器和 MSI **都没有代码签名**。Windows SmartScreen 首次运行会弹
> 「Windows 已保护你的电脑」，点「更多信息 → 仍要运行」。
> 未签名二进制也更容易被第三方杀软拦。企业分发策略可能直接拒收未签名 MSI。

下载完先核对哈希——方法见[校验与签名](/compiler/download/verify.html)。

---

## 当前稳定版 {#current}

**当前稳定版 v{{site_version}}**，{{site_version_date}} 发布。

| 产物 | 体积 | 是什么 |
|---|---|---|
| `jhyy-installer-{{site_version}}.exe` | ~55 MB | GUI 安装器：编译器 + `.jhyy` 文件关联 + VS Code 扩展 + PATH + 内置 ucrt64 工具链 |
| `jhyy-compiler-{{site_version}}.msi` | ~28 MB | MSI（企业分发）：同样的载荷，无 GUI 向导 |
| `jhyy-lang-{{site_version}}.vsix` | ~11 KB | VS Code 扩展 |

体积是实测值（打包后量 `installer/build-artifacts/` 里的产物），不是估的。

每个 release 都附带一个 `SHA256.txt` 资产，内容是 `sha256sum` 格式的清单。
**先校验再运行**——完整命令见[校验与签名](/compiler/download/verify.html)。

### 下载

| 文件 | GitHub Releases | 本地镜像 |
|---|---|---|
| 安装器 | [jhyy-installer-{{site_version}}.exe](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/download/v{{site_version}}/jhyy-installer-{{site_version}}.exe) | [/downloads/jhyy-installer-{{site_version}}.exe](/downloads/jhyy-installer-{{site_version}}.exe) |
| MSI | [jhyy-compiler-{{site_version}}.msi](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/download/v{{site_version}}/jhyy-compiler-{{site_version}}.msi) | [/downloads/jhyy-compiler-{{site_version}}.msi](/downloads/jhyy-compiler-{{site_version}}.msi) |
| VS Code 扩展 | [jhyy-lang-{{site_version}}.vsix](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/download/v{{site_version}}/jhyy-lang-{{site_version}}.vsix) | [/downloads/jhyy-lang-{{site_version}}.vsix](/downloads/jhyy-lang-{{site_version}}.vsix) |
| 校验和清单 | [SHA256.txt](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases/download/v{{site_version}}/SHA256.txt) | [SHA256SUMS.txt](/downloads/SHA256SUMS.txt) |

> [!NOTE]
> 编译器本体 `jhyy.exe` **不是** release 资产——它由安装器装到
> `C:\Program Files\JHYY\bin\`，在仓库里则是 `compiler/build/bin/jhyy.exe`。

---

## 安装器（GUI） {#installer}

`jhyy-installer-{{site_version}}.exe`（~55 MB）是给个人用户的那一个：**WiX 4 的 Burn bundle**，
双击走图形向导。

装上这些东西：

- **编译器** `jhyy.exe`；
- **`.jhyy` 文件关联**——双击 `.jhyy` 文件直接用编译器处理；
- **VS Code 扩展**——装进用户的 VS Code；
- **PATH**——写进系统环境变量，装完在任意终端里 `jhyy` 就能用；
- **内置的最小原生 ucrt64 工具链**（gcc + binutils + CRT + 头文件），装在
  `<安装目录>\toolchain\` 下。

最后一条是 v4.1.0 起的变化：**装完不需要 MSYS2**。工具链清单记录的是
gcc 15.2.0 / `x86_64-w64-mingw32`，379 个文件；编译器默认就用这份内置的，
不读用户 PATH 上的 `gcc`（查找顺序见仓库的构建文档）。

安装器还带桌面与开始菜单快捷方式、文档链接，以及一个 `jhyy-bash.cmd`——
它自己找 bash 并把 `JHYY\bin` 塞进 PATH 后启动。

静默安装（脚本或批量部署用）：

```powershell
jhyy-installer-{{site_version}}.exe /quiet
```

`/passive` 是「有进度条但无交互」，两者都是 Burn 的标准开关。

> [!WARNING]
> 安装器**没有代码签名**。首次运行 SmartScreen 会拦一道，需要点
> 「更多信息 → 仍要运行」；发布者一栏显示未知发布者。第三方杀软误报的概率
> 也比签名过的二进制高。

---

## MSI（企业分发） {#msi}

`jhyy-compiler-{{site_version}}.msi`（~28 MB）装的东西和安装器**完全一样**——
同一个 WiX MSI 里打的是同一份载荷。区别只有两点：**没有 GUI 向导**，以及
**面向自动化分发**。

它存在的理由是软件分发策略：SCCM、Intune、组策略下发 MSI 时不需要有人点
「下一步」。

```powershell
msiexec /i jhyy-compiler-{{site_version}}.msi /qn
```

`/qn` 是 msiexec 的静默安装开关。MSI 是**每台机器安装**（per-machine）：
写 `C:\Program Files\JHYY` 与 HKLM 的 PATH。

> [!IMPORTANT]
> MSI **也没有代码签名**。有些组织的软件分发策略直接拒收未签名 MSI——
> 这不是打不开，是策略层面拉黑。遇到这种环境，请走
> [pkgmgr](#pkgmgr) 或自建镜像，并提前跟 IT 打招呼。

> [!NOTE]
> 安装器比 MSI 大，是因为它额外带了一份 .NET 8 Desktop Runtime（Burn 引导与
> `jhyy-setuc.exe` 要用）。两者的编译器载荷与内置工具链是一样的。
> 体积是打包后量出来的，数字随版本变——以本页表格为准。

---

## VS Code 扩展 {#vsix}

`jhyy-lang-{{site_version}}.vsix`（~11 KB）是 VS Code 扩展。装了它之后：

- `.jhyy` 文件有语法高亮（TextMate grammar，scope `source.jhyy`）；
- 编辑器标题栏出现 **Run JHYY File**（快捷键 `Ctrl+F5`）与 **Compile JHYY File (no run)**；
- 四个配置项控制它调哪个可执行文件、跑在哪个集成终端、运行前是否自动保存。

**不含**调试器、LSP server、IntelliSense、hover 文档。

装安装器或 MSI 时会一并装上扩展。单独装：

```powershell
code --install-extension jhyy-lang-{{site_version}}.vsix
```

也可以在 VS Code 里走「扩展 → 右上角 ⋯ → 从 VSIX 安装」。

扩展的版本号在打包时对齐编译器版本（仓库里的 `installer/vscode-ext/package.ps1`
改 `package.json` 的 `version` 字段），文件名也带同一个版本号。

---

## 包管理器 {#pkgmgr}

从 v4.1.4 起提供两条包管理器渠道。**两者装的是同一个 Burn bundle**，
并且**都在运行前核对 SHA-256**。

### winget

包标识 **`JiHuiYiYou.JHYY`**：

```powershell
winget install JiHuiYiYou.JHYY
```

> [!WARNING]
> **上游还没合并。** manifest 已于 2026-11-07 提交到 `microsoft/winget-pkgs`
> （PR 在 `JiHuiYiYou/winget-pkgs` 的 `jh-{{site_version}}` 分支上），但上游的自动校验
> 与 CLA 签署流程还没走完——截至写这页，`manifests/j/JiHuiYiYou/JHYY` 在上游
> 仓库里**还不存在**。所以 `winget install` 现在大概率报「找不到包」。
> 合并之后这条命令才会生效。

仓内的 manifest 在 `installer/distribution/winget/manifests/j/JiHuiYiYou/JHYY/<版本>/`
（三件套：版本 / 安装器 / locale）。

### scoop

用的是**个人 bucket**（进 Main bucket 是另一个决定，尚未做）：

```bash
scoop bucket add jhyy https://github.com/JiHuiYiYou/scoop-bucket
scoop install jhyy --global
```

`--global` 是必须的：安装器是每台机器安装（写 `C:\Program Files\JHYY` 和
HKLM 的 PATH），而 scoop 默认装到用户目录。从提权的 shell 里跑，或者接受安装
过程中的 UAC 提示。

manifest 在仓内的 `installer/distribution/scoop/jhyy.json`。

---

## 历史版本归档 {#archive}

历史版本全部留在 GitHub Releases 上：

- [JiHuiYiYou-compiler · Releases](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/releases)

每个 release 都带自己那版的 `SHA256.txt`。**校验和是跟着版本走的**——
拿旧版本的校验和去对新版本的产物，必然对不上。

> [!NOTE]
> 归档里 v1.5.5 / v1.5.6 那两次发布的资产已 404：它们是历史占位
> （manifest 里那几个版本号从来没有真正发布过）。其余版本可用。

---

## 接下来 {#next}

- [目标与交叉编译](/compiler/download/targets.html)——{{targets_count}} 个 target 各自的产物，
  以及 freestanding 到底改了什么。
- [源码构建与自举](/compiler/download/bootstrap.html)——从源码编编译器，
  以及自举闭环证明的是什么、不证明什么。
- [校验与签名](/compiler/download/verify.html)——SHA256 怎么核对，
  以及「没有签名」这件事对用户意味着什么。
