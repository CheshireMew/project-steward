<!-- readme-header:start -->

<p align="center">
  <img src="./assets/readme/hero.svg" width="160" alt="Project Steward">
</p>

<h1 align="center">Project Steward</h1>

<p align="center">
  <strong>An Agent Skill for project research and audits, preventing rework, fixing root causes, and improving UI design and usability.</strong>
</p>

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

Give a compatible Agent this Skill and a repository, plan, UI problem, or task history. Project Steward supports research, delivery audits, UI design, rework prevention, root-cause fixes, and project publication.

> Checks, audits, diagnoses, and reviews are read-only by default. Explicit implementation requests authorize changes to the corresponding scope. Ordinary feature work and single-function questions remain normal development tasks.

## What it helps you accomplish

### Design and improve interfaces and usability

Design or refine layout, typography, color, hierarchy, components, interaction, and motion. Rebuild reference interfaces, align design systems, and improve desktop windows, responsive layouts, and local file workspaces.

Review relevant pages, windows, and states. After approved implementation, check actual visuals and continuous use; report implementation, visual verification, and usability separately. See [product experience and interface governance](./references/product-experience-governance.md).

### Understand a project and audit delivery

Explain a repository’s purpose, operation, and architecture; distinguish methods worth learning from reusable content. Compare delivery with the plan to find completed, missing, and unverified work. Comprehensive audits prioritize applicable findings with evidence.

### Prevent rework before implementation

Plan the result, dependencies, affected callers, migration order, and checks before implementation. Review relevant performance, progress, long-running operations, model workflows, and cross-project interfaces.

### Close defects at the root cause

Trace symptoms to their source, repair affected modules and callers, and retire obsolete implementations. Review coupling, duplication, and overloaded modules to prevent recurring patches.

### Organize the project, environment, and publication

| Work | Result | Method |
| --- | --- | --- |
| Directories | Classify active files, local state, and history; propose ignore, move, or archive decisions | [Directories](./references/repository-directory-governance.md) |
| External compatibility | Inspect tool integration, official formats, and export chains; locate and repair incompatibilities | [Compatibility](./references/external-tool-compatibility.md) |
| Project templates | Establish, adopt, and upgrade baselines; capture consistently applicable practices | [Templates](./references/project-template-system.md) · [Evolution](./references/template-evolution.md) |
| Logs and environment | Trace real operations and check tools, SDKs, caches, and long-running tasks | [Logs](./references/log-audit-standard.md) · [Environment](./references/user-environment-governance.md) |
| Runtime storage | Govern placement, growth, and leftovers for models, downloads, media, caches, and test outputs | [Storage](./references/production-storage-governance.md) |
| README and publication | Prepare project introductions, homepage visuals, languages, licenses, and GitHub metadata | [README](./references/readme-delivery.md) · [Licensing](./references/license-governance.md) · [Publication](./references/repository-publication.md) |

### Learn from real project work

Learn from effective practices, failures, and corrections in a complete task. Propose future changes and incorporate approved methods into Project Steward. Project decisions stay in project documentation, code, and configuration.

## Say it directly

Start each request with **Use $project-steward**, then provide the project or material and an instruction below. Specify review, proposal, or implementation.

| Intent | Example request |
| --- | --- |
| Improve an interface | improve this project's UI and usability, including layout, hierarchy, components, and interactions; check the actual visuals and main operations. |
| Design from scratch | design this product's interface. Present structure and visual directions for me to choose first. |
| Rebuild a reference | rebuild this reference interface and compare it with the running result. |
| Understand or govern a repository | explain this repository's purpose, architecture, and operation, and separately assess which capabilities are worth adopting. |
| Audit a plan | compare this project with the implementation plan and list completed, missing, and unverified work. |
| Audit a project | review this project comprehensively and prioritize improvements by user impact and risk. |
| Check a change | check this change's impact, dependencies, and acceptance criteria. Give me an implementation proposal first. |
| Fix a root cause | diagnose and fix this failure, update affected callers, and verify the actual result. |
| Organize directories | identify files still in use and files that should not be uploaded. Propose an organization plan first. |
| Check compatibility | check compatibility with this external tool or official format and identify the failing boundary. |
| Adopt or upgrade templates | inspect this project's baseline and propose template adoption or upgrades. |
| Evolve templates | assess whether these practices qualify as stable defaults and update the relevant templates. |
| Improve logs | improve this project's logs so one operation's inputs, progress, failures, and result can be traced. |
| Check the environment | check required tools, SDKs, and cache locations and explain current environment gaps. |
| Govern storage | inspect growth and leftovers from models, media, caches, and test outputs. Propose storage changes first. |
| Improve a README | improve this README, including content, languages, homepage information, and related publication work. |
| Review licensing | inspect this repository's licenses and third-party sources and propose scope corrections. |
| Publish changes | inspect upload contents, then commit and push the confirmed changes to the existing remote. |
| Learn from a conversation | read this complete task history and propose future behavior and affected files before approved self-evolution. |

## What a complete README improvement includes

Use project facts to explain main uses and entry points, then address content, homepage visuals, languages, navigation, and licensing. Public GitHub repositories also include Star History, Topics, and About Description; Website uses only a qualified official destination.

- Visual checks cover source structure and references; they do not establish that the image looks good.
- Star History implementation stops after workflow dispatch. Generated charts and remote display remain unverified until a separate remote-acceptance request.
- Commit and push follow the confirmed scope; a push does not start a wait for new remote checks.

See the [complete README delivery method](./references/readme-delivery.md) for scope and execution conditions.

## How it works

~~~text
User outcome
  → project facts and authority
  → prevention / diagnosis / implementation
  → formal producer and real boundary
  → final consumer and user result
  → old-path retirement and regression
~~~

[SKILL.md](./SKILL.md) selects methods in [references](./references/) and tools in [scripts](./scripts/). Project facts stay in the project.

## Installation

~~~bash
npx skills add CheshireMew/project-steward
~~~

After installation, invoke it directly:

~~~text
Use $project-steward to review this project comprehensively and order the governance work by risk.
~~~

Authorize writing, execution, installation, commits, and publication through your request. Self-evolution presents behavior and impact for approval before changing the Skill.

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

Check this README (use the command on each translated page for that language):

~~~powershell
python scripts/audit_readme.py README.en.md --header-profile assets/readme-profile/profile.json --repository CheshireMew/project-steward --language en --project-name "Project Steward" --tagline "An Agent Skill for project research and audits, preventing rework, fixing root causes, and improving UI design and usability." --identity-image assets/readme/hero.svg --identity-image-width 160 --branch main --navigation-target docs=SKILL.md
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
