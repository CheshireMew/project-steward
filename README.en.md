<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Project Steward learns from project outcomes, prevents rework, and closes root causes">
</p>

<!-- readme-header:start -->

<p align="center">
  <a href="./README.md">中文</a> · <strong>English</strong> · <a href="./README.ja.md">日本語</a> | <a href="./SKILL.md">文档</a> | <a href="./CONTRIBUTING.md">贡献</a> | <a href="https://github.com/CheshireMew/project-steward/issues">反馈</a>
</p>

<p align="center">
  <a href="https://x.com/0xCheshire" title="X"><img src="https://img.shields.io/badge/X-%400xCheshire-000000?logo=x&amp;logoColor=white" alt="X：@0xCheshire"></a>
  <a href="https://t.me/CheshireBTC" title="Telegram"><img src="https://img.shields.io/badge/Telegram-CheshireBTC-26A5E4?logo=telegram&amp;logoColor=white" alt="Telegram：CheshireBTC"></a>
  <a href="https://blog.blacknico.com/" title="Blog"><img src="https://img.shields.io/badge/Blog-blog.blacknico.com-2E7D32?logo=rss&amp;logoColor=white" alt="博客：blog.blacknico.com"></a>
  <a href="https://blacknico.com/" title="Homepage"><img src="https://img.shields.io/badge/Home-blacknico.com-1F6FEB?logo=googlechrome&amp;logoColor=white" alt="个人主页：blacknico.com"></a>
</p>

<p align="center">
  <a href="https://github.com/CheshireMew/project-steward/stargazers"><img src="https://img.shields.io/github/stars/CheshireMew/project-steward?style=flat" alt="GitHub Stars"></a>
  <a href="https://github.com/CheshireMew/project-steward/forks"><img src="https://img.shields.io/github/forks/CheshireMew/project-steward?style=flat" alt="GitHub Forks"></a>
  <a href="https://github.com/CheshireMew/project-steward/blob/main/LICENSE"><img src="https://img.shields.io/github/license/CheshireMew/project-steward?style=flat" alt="Repository License"></a>
</p>

<!-- readme-header:end -->

# Project Steward

**Turn the successes, rework, and corrections from one project into better action on the next.**

Project Steward is a project-governance Skill. It learns reusable methods from complete project work, checks likely rework boundaries before changes, and closes defects by migrating producers, boundaries, and consumers together.

Use it for repository-level outcomes: understanding a codebase, preventing unsafe changes, governing cross-layer failures, organizing a repository, improving a README, licensing, and publication. Ordinary feature work and single-function questions remain regular development tasks.

> Inspection, audit, diagnosis, and review are read-only by default. Project Steward changes state only when the request explicitly asks for implementation, self-evolution, or publication.

## What it helps you accomplish

### Learn from real project work

Project Steward groups requests, decisions, commands, waits, failures, corrections, and final evidence by user outcome. It identifies proven methods, the earliest point of divergence, and the future action that should change.

It does not append every internal lesson to the README. Internal behavior belongs to SKILL.md, references, and tests; the README keeps only stable identity, usable entry points, and reader-facing boundaries.

### Prevent rework before implementation

- Freeze target behavior, the source of truth, impact scope, and stopping point.
- Migrate every formal call site and retire the old path.
- Add focused checks for durable operations, external CLIs, model calls, desktop lifecycles, and cross-repository contracts.
- Design verification from the formal producer to the observable user result.

### Close defects at the root cause

- Separate the symptom, direct cause, valid guard, earliest controllable cause, workaround, and residue.
- Preserve failing evidence before changing the final boundary.
- Verify production, transport or storage, consumption, user-visible results, and old-path retirement.
- Turn cohesion, coupling, duplication, and god-module findings into an implementable project result.

### Govern a project's public surface

Project Steward can also study unfamiliar repositories, inventory directories, maintain project templates, govern product experience and logs, record the user's execution environment, and complete README, licensing, Star History, and repository publication work.

## Say it directly

### Evolve from a conversation

~~~text
Use $project-steward to read this conversation's complete process.
Group proven mechanisms, capability gaps, and root causes by user outcome.
Show the future behavior and affected files first, then evolve Project Steward after confirmation.
~~~

### Check a change before implementation

~~~text
Use $project-steward to review this change.
Identify the source of truth, every consumer, old-path retirement, and real verification,
then implement it through fresh evidence.
~~~

### Repair a cross-layer defect

~~~text
Use $project-steward to diagnose and fix this cross-layer failure.
Do not add symptom-specific exceptions. Migrate producers, boundaries, and consumers together,
and prove the old architecture is gone.
~~~

### Understand or govern a repository

~~~text
Use $project-steward to explain this project.
Show what it solves, how it runs, where its core boundaries are,
what is worth adopting, and what must not be copied directly.
~~~

### Improve a README

~~~text
Use $project-steward to improve this README.
Check Git and repository state, content and visuals, languages, licensing,
Star History, links, and publication, then deliver the complete result.
~~~

## What a complete README improvement includes

A complete README task checks whether the repository is initialized, whether a README exists, and whether project identity and reader flow are accurate before choosing to write, rewrite, restructure, or compress.

- Content: remove internal-method mirrors and repetition; retain identity, outcomes, real entry points, first success, and maintainer navigation.
- Visuals: qualify the hero, images, and evidence, then inspect desktop, narrow viewport, and GitHub light and dark themes.
- Header: generate 中文, English, 日本語, documentation, contribution, feedback, personal links, Stars, Forks, and license from active facts.
- License: preserve an accurate existing license; when absent, verify rights and adoption goals before applying the confirmed choice.
- Star History: run the real workflow for a public GitHub repository and verify both SVGs and the README consumer.
- Publication: for an approved existing remote, commit precisely, push, and verify remote HEAD without silently creating remotes, changing visibility, force-pushing, or deleting files.

See the [complete README delivery method](./references/readme-delivery.md).

## How it works

~~~text
User outcome
  → project facts and authority
  → prevention / diagnosis / implementation
  → formal producer and real boundary
  → final consumer and user result
  → old-path retirement and regression
~~~

The main Skill file owns routing only. Full methods live in [references](./references/), deterministic tools live in [scripts](./scripts/), and each project's durable facts remain in that project's existing rules, code, configuration, and tests.

## Installation

~~~bash
npx skills add CheshireMew/project-steward
~~~

After installation, invoke it directly:

~~~text
Use $project-steward to review this project comprehensively and order the governance work by risk.
~~~

Writing, running, installing, committing, and publishing remain separately authorized by the request. Project Steward self-evolution uses two-stage confirmation: it shows future behavior and impact first, then modifies itself after approval.

## Repository map

| Path | Responsibility |
| --- | --- |
| [SKILL.md](./SKILL.md) | Role, primary routes, authority, and stopping points |
| [references](./references/) | Unique owners for each governance method |
| [scripts](./scripts/) | README, license, template, directory, environment, and Star History tools |
| [assets](./assets/) | License catalog, templates, README profile, and visual resources |
| [tests](./tests/) | Active routes, method ownership, tools, and consumer contracts |

## Verification

Run all active tests:

~~~powershell
python -m unittest discover -s tests -v
~~~

Audit all three README languages:

~~~powershell
python scripts/audit_readme.py README.md --header-profile assets/readme-profile/profile.json --repository CheshireMew/project-steward --language zh-CN --branch main --navigation-target docs=SKILL.md
python scripts/audit_readme.py README.en.md --header-profile assets/readme-profile/profile.json --repository CheshireMew/project-steward --language en --branch main --navigation-target docs=SKILL.md
python scripts/audit_readme.py README.ja.md --header-profile assets/readme-profile/profile.json --repository CheshireMew/project-steward --language ja --branch main --navigation-target docs=SKILL.md
~~~

## Star History

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/CheshireMew/project-steward/star-history/star-history-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/CheshireMew/project-steward/star-history/star-history.svg">
  <img alt="Project Steward GitHub Star History" src="https://raw.githubusercontent.com/CheshireMew/project-steward/star-history/star-history.svg">
</picture>

The repository's GitHub Actions workflow uses the short-lived github.token and publishes the chart to the dedicated star-history branch. See [Star History governance](./references/github-star-history.md) for the full production chain.

## License and third-party sources

Project Steward's primary code and documentation are licensed under the [Mozilla Public License 2.0](./LICENSE).

Parts of the README content and visual methods are adapted from [oil-oil/beautify-github-readme](https://github.com/oil-oil/beautify-github-readme) under its MIT License. Exact scope and notices are in [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) and [NOTICE](./NOTICE).

Report problems and improvement ideas through [GitHub Issues](https://github.com/CheshireMew/project-steward/issues).
