# JiHuiYiYou 官网

[机会翼游](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) 的官网(landing page)静态实现,部署在 GitHub Pages。

[![GH Pages status](https://img.shields.io/badge/GH%20Pages-jihuiyiyou.github.io-blue)](https://jihuiyiyou.github.io/JiHuiYiYou-website/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 当前状态

- **v1.8.3 同步** (2026-08-29): `v1.x FINAL`,Stage 2 N=4 byte-equal closure sha `03a1cdd4...`
- **静态实现**: 单 `index.html` + `assets/{css,js,img}/`,无构建步骤
- **GH Pages 部署**: 根目录 `/`,branch `main`,default domain `*.github.io`

## 文件结构

```
JiHuiYiYou-website/
├── index.html                # 主页面(11 section + footer)
├── assets/
│   ├── css/main.css          # 设计系统(深黑 + 琥珀 + Ecosystem grid + :active 全站)
│   ├── js/main.js            # 滚动揭示 / tab / copy / 磁吸 / IntersectionObserver
│   └── img/jhyy-icon.png
├── downloads/                # ← GitHub Pages 直接 host,带 ?v=1.8.3 cache-bust
│   ├── jhyy-installer-1.8.3.exe   (~28.5 MB,WiX 7.0.0 + .NET 8 chain)
│   ├── jhyy-compiler-1.8.3.msi   (~1.1 MB,silent,SCCM 友好)
│   ├── jhyy-lang-1.8.3.vsix      (~13 KB,VS Code 扩展)
│   └── SHA256SUMS.txt
├── .nojekyll                 # 禁 Jekyll 化
├── .gitignore                # 排除散落 PNG / .playwright-cli / 根目录 exe·msi 散落
├── DESIGN.md                 # 设计文档(Next.js 路线图已 deprecated,见 §11 banner)
└── README.md                 # 本文件
```

## 11 个 section

| # | Section | 内容 |
|---|---------|------|
| 1 | Hero | 标题 + Stage 2 N=4 + 3 CTA |
| 2 | Why JHYY (Bento) | 4 张卡:类型 / 控制流 / 自举 / 规范锁定 |
| 3 | Install | MSI 一键 / 源码 / 企业 MSI 3 卡 |
| 4 | Code Showcase | 4 个 tab:hello / shapes / fib / enum |
| 5 | Toolchain | Compiler / VS Code ext / MCP / Windows Installer |
| 6 | Roadmap | v0.x done / v1.x done v1.8.3 FINAL / v2.x next / v3.x parallel |
| 7 | Performance | 4 真指标(closure sha / 102-102 / W=0 / ~120ms) |
| 8 | About | 中文 bio + QQ 群 429807125 |
| 9 | Docs Preview | 4 卡:spec v1.3.0 / ABI v1.0.0 / workarounds / examples |
| 10 | Ecosystem | GCC / MSYS2 / mingw-w64 / .NET 8 / WiX 7 / QBE 6 张 |
| 11 | Final CTA | 3 按钮:Installer / Silent MSI / Build from source |

> Hero 顶部的 eyebrow 小窗(原 `v1.8.3 · Stage 2 ...` 那一行)在最近一次迭代删除 — 信息在 Hero sub + Why JHYY 03 / Performance 都已覆盖。

## 本地预览

```bash
# Python(任意静态 server 都行)
python -m http.server 8000

# Node
npx serve .

# MSYS2
python -m http.server 8000 --bind 127.0.0.1
```

浏览器打开 `http://localhost:8000`。

## 部署到 GitHub Pages

**首次**(本地无 .git):

```bash
git init
git checkout -b main
git remote add origin git@github.com:JiHuiYiYou/JiHuiYiYou-website.git
git config user.name "JHYY"
git config user.email "15901598712@163.com"
git add .
git commit -m "feat: JHYY 官网 v1.8.3 同步 + GitHub Pages 部署"
git push -u origin main
```

**SSH agent 注意**(Windows + MSYS2 / Git Bash): Bash 工具每次开新 subshell,ssh-agent 不持久。
`git push` 前**必须**在同一次调用里:`eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519 && git push`。

**启用 Pages**: repo Settings → Pages → Source `Deploy from a branch` → Branch `main` / `/ (root)` → Save。
1-2 分钟后 `https://jihuiyiyou.github.io/JiHuiYiYou-website/` 生效。

## 后续内容更新

**主仓 ship 后**(同步 `index.html` 内容):

```bash
# vX.Y.Z 状态 / 数字 / 链接全部改完后:
git add .
git commit -m "sync: 主仓 vX.Y.Z ship 后跟进"
git push
```

**installer artifacts 更新**(从主仓拷):

```bash
cp <main-repo>/installer/build-artifacts/jhyy-installer-X.Y.Z.exe downloads/
cp <main-repo>/installer/build-artifacts/jhyy-compiler-X.Y.Z.msi downloads/
cp <main-repo>/installer/build-artifacts/jhyy-lang-X.Y.Z.vsix downloads/
cd downloads && sha256sum * > SHA256SUMS.txt && cd ..

# 同步更新 index.html 所有 download href 里的 ?v=X.Y.Z cache-bust
# (避免 Edge 缓存命中老版 URL)

git add downloads/ index.html
git commit -m "chore(downloads): bump installer to X.Y.Z"
git push
```

## 链接到主仓

| 网站段 | 跳转到 |
|--------|--------|
| Hero CTA "Read the spec" | [`docs/abis/jhyy-lang-spec-v1.3.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-lang-spec-v1.3.0.md) |
| Docs Preview · Spec | 同上 |
| Docs Preview · ABI | [`docs/abis/jhyy-abi-v1.0.0.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/abis/jhyy-abi-v1.0.0.md) |
| Docs Preview · Workarounds | [`docs/internal/workarounds.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/docs/internal/workarounds.md) |
| Docs Preview · Examples | [`compiler/tests/examples/`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/tree/main/compiler/tests/examples) |
| Ecosystem · GCC / MSYS2 / .NET / WiX / QBE | 各官方网站,见段内 `target="_blank"` |
| Footer · Build | [`JiHuiYiYou-compiler`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) |
| Footer · Issues | [`github.com/.../issues`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/issues) |
| Footer · Contributing | [`github.com/.../blob/main/CONTRIBUTING.md`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler/blob/main/CONTRIBUTING.md) |
| Footer · Community · QQ 群 | 群号 `429807125`(一键复制,QQ 客户端搜索加入) |

## 内容更新规则

- **主仓 ship 后**: 同步 `index.html` 里 vX.Y.Z 状态、Status bar、Roadmap、Performance 数字、toolchain 组件
- **installer artifacts 更新**: 从主仓 `installer/build-artifacts/` 拷最新 → 重 sha256sum → push,**所有 download href 同步加 `?v=X.Y.Z` cache-bust**
- **不引入构建**: 不加 Tailwind / Next.js / Vercel;保持纯静态
- **保持主仓为权威**: 网站是入口,文档 / changelog / workarounds 永远以主仓 GitHub 为准

## License

MIT — 跟 [JiHuiYiYou-compiler](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) 一致。
