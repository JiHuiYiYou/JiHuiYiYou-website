# JiHuiYiYou 官网

[JHYY 编译器](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler)(机会翼游 — 自研静态类型语言 + 自举编译器)的官网,静态静态实现,挂在 GitHub Pages。

## 主仓库

[github.com/JiHuiYiYou/JiHuiYiYou-compiler](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) — 编译器源码、规范 / ABI / changelog / 路线图 / workarounds 都在主仓。
当前状态 `v1.8.3`(`v1.x FINAL`),Stage 2 N=4 byte-equal closure 闭环。

## 本站

- 在线:`https://jihuiyiyou.github.io/JiHuiYiYou-website/`
- 部署:GitHub Pages from `main` branch,根目录 `/`
- 本地预览:`python -m http.server 8000`
- 静态:`index.html` + `assets/{css,js,img}` + `downloads/`,无构建步骤
- License:MIT