# 机会翼游 · JHYY 家族官网

[编译器](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) / [IDE](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE) / [OS](https://github.com/JiHuiYiYou/JiHuiYiYou-OS) / [for-VEX](https://github.com/JiHuiYiYou/JiHuiYiYou-for-VEX) 四个项目的官网枢纽。

静态站，挂在 GitHub Pages。**内容源是 Markdown，HTML 是生成产物。**

## 四个项目

| 项目 | 状态 | 说明 |
|---|---|---|
| [JHYY 编译器](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) | v4.1.4 · 稳定 | 自举的系统编程语言编译器。编译器唯一实现是 JHYY 自己，后端是自研 amd64 发射器 |
| [JHYY IDE](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE) | v0.2.1 | 拖块编程与文本编辑共享同一棵 AST 的桌面工作台 |
| [JiHuiYiYou-OS](https://github.com/JiHuiYiYou/JiHuiYiYou-OS) | 孵化中 | 用这门语言写的 microkernel；当前只有 UEFI x64 引导 spike |
| [JiHuiYiYou-for-VEX](https://github.com/JiHuiYiYou/JiHuiYiYou-for-VEX) | Day 0 完成 | 让 JHYY 直出 ARM 机器码，链官方 SDK 跑在 VEX V5 Brain 上 |

编译器仓里是权威事实源：规范 / ABI / 二进制格式 / 变更日志 / 问题台账 / 回归套件。

## 本站

- 在线：`https://ji-hui-yi-you.github.io/JiHuiYiYou-website/`
- 部署：GitHub Pages，`main` 分支根目录
- 本地预览：`python -m http.server 8000`

## 怎么改

```bash
# 改内容 → content/ 下编辑 Markdown，然后重新生成
python tools/build.py

# 检查站内链接与锚点
python tools/build.py --check

# 把文档里的 .jhyy 代码块交给真编译器验一遍
python tools/check_examples.py
```

生成的 HTML 直接提交进仓库（GH Pages 从仓库根直出）。改完跑一次
`build` + `check`，两条都绿再提交。

**版本号只有一处**：`tools/siteconfig.py` 里的 `SITE_VERSION`。改那里，全站跟着改。

内容写作规约见 [`tools/CONTENT_GUIDE.md`](tools/CONTENT_GUIDE.md)；
设计与架构见 [`DESIGN.md`](DESIGN.md)。

## 目录

```
content/          内容源（Markdown + 少量 HTML 片段）
tools/            生成器、Markdown 渲染器、站点配置、写作规约
assets/css/       main.css（门脸层）/ docs.css（文档层）
assets/js/        main.js（门脸层动效）/ docs.js（文档层搜索）
downloads/        v4.1.4 发行件镜像 + SHA256SUMS.txt
```

## License

MIT
