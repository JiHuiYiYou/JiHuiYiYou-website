# 自托管字体

站点的四款拉丁字体放在这里，**不走 CDN** —— `fonts.googleapis.com` 在中国大陆
取不到，取不到就整站字体退到系统默认（标题掉回 Times New Roman，品牌识别度归零）。

> 这个决定（为什么自托管、为什么中文走系统栈）记在 `DESIGN.md` §6；
> 本文件只管**资产清单与许可**，不复述设计理由。

| 字体 | 用途 | 许可 |
|---|---|---|
| Instrument Serif | 门脸层大标题 | SIL OFL 1.1（`OFL-instrumentserif.txt`） |
| Space Grotesk | 门脸层正文 | SIL OFL 1.1（`OFL-spacegrotesk.txt`） |
| JetBrains Mono | 代码 | SIL OFL 1.1（`OFL-jetbrainsmono.txt`） |
| Inter | 文档层正文 | SIL OFL 1.1（`OFL-inter.txt`） |

**只有 latin / latin-ext 子集** —— 这四款都**没有汉字字形**。中文由
`assets/css/main.css` 的 `--f-serif` / `--f-sans` 里的系统 CJK 栈兜
（思源宋体 / 思源黑体 / 苹方 / 微软雅黑 / 宋体）。

子集文件按 `家族-字重-字形-子集.woff2` 命名，`@font-face` 规则在
`assets/css/fonts.css`。

字体文件由 `tools/` 之外的脚本从 Google Fonts 下载一次后提交进仓；
**不要**在构建时联网取字体 —— 那会让构建依赖网络。
