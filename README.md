# JHYY — the family website

**[Chinese version →](README.zh-CN.md)** ｜ A static site for four projects: the
[compiler](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler),
[IDE](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE),
[OS](https://github.com/JiHuiYiYou/JiHuiYiYou-OS) and
[for-VEX](https://github.com/JiHuiYiYou/JiHuiYiYou-for-VEX).

**The content sources are Markdown; the HTML is a generated artifact.**

## The four projects

| Project | Status | What it is |
|---|---|---|
| [JHYY compiler](https://github.com/JiHuiYiYou/JiHuiYiYou-compiler) | v4.1.5 · stable | A self-hosted systems language compiler. The only implementation of the compiler is JHYY itself, and the backend is a self-written amd64 emitter |
| [JHYY IDE](https://github.com/JiHuiYiYou/JiHuiYiYou-IDE) | v0.2.1 | A desktop workbench where block programming and text editing share one AST |
| [JiHuiYiYou-OS](https://github.com/JiHuiYiYou/JiHuiYiYou-OS) | incubating | A microkernel written in that language; today it is only a UEFI x64 boot spike |
| [JiHuiYiYou-for-VEX](https://github.com/JiHuiYiYou/JiHuiYiYou-for-VEX) | step 0 done | Compiling JHYY straight to ARM machine code, linked against the official SDK, running on a VEX V5 Brain |

The compiler repository is the authoritative source of facts: the language spec, the ABI, the binary format, the changelog, the workaround ledger, the regression suite.

## This site

- Live: `https://jihuiyiyou.github.io/JiHuiYiYou-website/`
- Deployed by GitHub Pages from the root of `main`
- Local preview: `python -m http.server 8000`

## How to change something

```bash
# Edit the Markdown under content/ (the English sources live in content/en/), then regenerate
python tools/build.py

# Check the site's internal links and anchors
python tools/build.py --check

# Facts gate: the site's siteconfig.FACTS ↔ the compiler repo's docs/internal/FACTS.md
python tools/check_facts.py          # needs the compiler repo (../JiHuiYiYou by default; JHYY_REPO overrides)

# Twin-page gate: every page must have both a Chinese and an English version
python tools/check_twins.py

# i18n consistency: no hand-written facts in the prose, no Chinese on English pages, one term per concept
python tools/check_i18n.py

# Hand the .jhyy code blocks in the docs to the real compiler
python tools/check_examples.py
```

The generated HTML is committed straight into the repository — GitHub Pages serves the repository root. After a change, run `build` + `check` once, and only commit when both are green.

## Documentation

| Document | What it covers |
|---|---|
| [`DESIGN.md`](DESIGN.md) | Design decisions: the north star, the general rules, the two layers, the anti-patterns, the decision log |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Site structure and current state: routes, content skeleton, build pipeline, gates, components, what exists today |
| [`Task.md`](Task.md) | What is not done yet: what, who owns it, how it is judged done |
| [`tools/CONTENT_GUIDE.md`](tools/CONTENT_GUIDE.md) | The rules for writing `content/**`: front matter, Markdown dialect, voice, where facts come from |
| [`assets/fonts/README.md`](assets/fonts/README.md) | Font assets and their licenses |

**A rule that spans files is written in exactly one place** — the mechanisms (version numbers, fact placeholders, the bilingual tree, the glossary) are documented in `ARCHITECTURE.md` §4 and `DESIGN.md` §6; this README does not restate them, because a restatement is a second copy and the second copy drifts.

> These five documents are written in Chinese, following the family's rule that in-repo documentation stays in Chinese while outward-facing documents (README / CONTRIBUTING / CHANGELOG) are English.

## Layout

```
content/          content sources (Markdown + a few hand-written HTML pages)
tools/            generator, Markdown renderer, site configuration, writing guide
assets/css/       main.css (landing pages) / docs.css (documentation pages)
assets/js/        main.js (landing page motion) / docs.js (documentation search)
downloads/        v4.1.5 release artifacts mirror + SHA256SUMS.txt
```

## License

MIT
