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
├── index.html                # 主页面(10 section + footer)
├── assets/
│   ├── css/main.css          # 设计系统(深黑 + 琥珀)
│   ├── js/main.js            # 滚动揭示 / tab / copy / 计数 / 磁吸
│   └── img/jhyy-icon.png
├── downloads/                # ← GitHub Pages 直接 host
│   ├── jhyy-installer-1.8.3.exe   (~28.5 MB,WiX 7.0.0 + .NET 8 chain)
│   ├── jhyy-compiler-1.8.3.msi   (~1.1 MB,silent,SCCM 友好)
│   ├── jhyy-lang-1.8.3.vsix      (~13 KB,VS Code 扩展)
│   └── SHA256SUMS.txt
├── .nojekyll                 # 禁 Jekyll 化
├── .gitignore                # 排除散落 PNG / .playwright-cli / tmp
├── DESIGN.md                 # 设计文档(Next.js 路线图已 deprecated,见 §11 banner)
└── README.md                 # 本文件
```

## 10 个 section

| # | Section | 内容 |
|---|---------|------|
| 1 | Hero | `v1.8.3 = v1.x FINAL` + Stage 2 N=4 + 3 CTA |
| 2 | Why JHYY (Bento) | 4 张卡:类型 / 控制流 / 自举 / 规范锁定 |
| 3 | Install (新) | MSI 一键 / 源码 / 企业 MSI 3 卡 |
| 4 | Code Showcase | 4 个 tab:hello / shapes / fib / enum |
| 5 | Toolchain | Compiler / VS Code ext / MCP / Windows Installer |
| 6 | Roadmap | v0.x done / v1.x done v1.8.3 FINAL / v2.x next / v3.x parallel |
| 7 | Performance | 4 真指标(编译时间 / 二进制 / 测试基线 / closure sha) |
| 8 | About | 中文 bio + QQ 群 429807125 |
| 9 | Docs Preview | 4 卡:spec v1.3.0 / ABI v1.0.0 / workarounds / examples |
| 10 | Final CTA | 3 按钮:Installer / Silent MSI / Build from source |

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

```bash
# 1. 本仓 init + push
git init
git checkout -b main
git remote add origin https://github.com/JiHuiYiYou/JiHuiYiYou-website.git
git add .
git commit -m "feat: JHYY 官网 v1.8.3 同步 + GitHub Pages 部署"
git push -u origin main

# 2. repo Settings → Pages:
#    Source: Deploy from a branch
#    Branch: main / / (root)
#    Save → 1-2 分钟后 https://<user>.github.io/JiHuiYiYou-website/ 可访问

# 3. 后续 installer artifacts 更新
cp <main-repo>/installer/build-artifacts/jhyy-installer-X.Y.Z.exe downloads/
cp <main-repo>/installer/build-artifacts/jhyy-compiler-X.Y.Z.msi downloads/
cd downloads && sha256sum * > SHA256SUMS.txt && cd ..
git add downloads/
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
| Footer · Build | [`JiHuiYiYou-compiler`](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) |
| Footer · Community · QQ 群 | 群号 `429807125`(一键复制,QQ 客户端搜索加入) |

## 内容更新规则

- **主仓 ship 后**: 同步 `index.html` 里 vX.Y.Z 状态、Status bar、Roadmap、Performance 数字、toolchain 组件
- **installer artifacts 更新**: 从主仓 `installer/build-artifacts/` 拷最新 → 重 sha256sum → push
- **不引入构建**: 不加 Tailwind / Next.js / Vercel;保持纯静态

## License

MIT — 跟 [JiHuiYiYou-compiler](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) 一致。
# JiHuiYiYou-website
