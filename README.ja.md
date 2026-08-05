<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Project Steward はプロジェクトの結果から学び、手戻りを防ぎ、根本原因まで収束させます">
</p>

<!-- readme-header:start -->

<p align="center">
  <a href="./README.md">中文</a> · <a href="./README.en.md">English</a> · <strong>日本語</strong> | <a href="./SKILL.md">文档</a> | <a href="./CONTRIBUTING.md">贡献</a> | <a href="https://github.com/CheshireMew/project-steward/issues">反馈</a>
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

**一度のプロジェクトで得た成功、手戻り、修正を、次のより確かな行動へ変えます。**

Project Steward はプロジェクトガバナンス用の Skill です。プロジェクトの全過程から再利用できる方法を学び、変更前に手戻りの原因となる境界を確認し、不具合発生後は生産者・境界・消費者をまとめて移行して根本原因まで収束させます。

リポジトリ全体の成果に向いています。コードベースの理解、安全な変更、複数層にまたがる不具合、ディレクトリ整理、README 改善、ライセンス、公開を扱います。通常の機能実装や単一関数の質問は、通常の開発タスクとして扱います。

> 検査、監査、診断、レビューは既定で読み取り専用です。明示的に実装、自己進化、公開を依頼された場合だけ、対応する状態を変更します。

## できること

### 実際のプロジェクト作業から学ぶ

Project Steward は、要求、判断、コマンド、待機、失敗、修正、最終証拠をユーザー成果ごとに整理します。すでに有効だった方法、最初にずれた地点、次回変えるべき行動を見つけます。

内部で学んだ規則を README に追加し続けることはありません。内部動作は SKILL.md、references、tests が保持し、README には安定した役割、利用入口、読者に必要な境界だけを残します。

### 実装前に手戻りを防ぐ

- 目標動作、唯一の事実源、影響範囲、停止位置を固定します。
- 正式な呼び出し元を一度に移行し、旧経路を終了させます。
- 永続操作、外部 CLI、モデル呼び出し、デスクトップのライフサイクル、複数リポジトリ契約に必要な専用確認を重ねます。
- 正式な生産者からユーザーが確認できる結果までを通した検証を設計します。

### 根本原因から不具合を収束させる

- 現象、直接原因、正当な保護、最初の制御可能な原因、回避策、残留を分けます。
- 失敗証拠を保持してから最終境界を移行します。
- 生成、転送または保存、消費、ユーザー結果、旧経路の終了を確認します。
- 凝集度、結合、重複、巨大モジュールの指摘を実施可能なプロジェクト成果へ変えます。

### プロジェクトの公開面を整える

未知のリポジトリの調査、ディレクトリの棚卸し、プロジェクトテンプレート、製品体験、ログ、実行環境に加え、README、ライセンス、Star History、リポジトリ公開まで一貫して扱えます。

## そのまま依頼できます

### 会話から自己進化する

~~~text
この会話の全過程を $project-steward で読んでください。
ユーザー成果ごとに成功した仕組み、能力の不足、根本原因を整理し、
将来の動作と影響ファイルを先に提示して、確認後に自己進化してください。
~~~

### 変更前に確認する

~~~text
この変更を $project-steward で確認してください。
唯一の事実源、すべての消費者、旧経路の終了、実際の検証を決めてから、
新しい証拠が十分になるまで実装してください。
~~~

### 複数層の不具合を修正する

~~~text
この複数層の不具合を $project-steward で診断して修正してください。
症状ごとの例外は追加せず、生産者、境界、消費者を一度に移行し、
旧アーキテクチャが終了したことを証明してください。
~~~

### リポジトリを理解・統治する

~~~text
このプロジェクトを $project-steward で説明してください。
何を解決し、どのように動き、主要な境界がどこにあり、
何を取り入れられ、何を直接コピーすべきでないかを示してください。
~~~

### README を改善する

~~~text
この README を $project-steward で改善してください。
Git とリポジトリ状態、文章と視覚、多言語、ライセンス、
Star History、リンク、公開を確認し、完成した結果まで届けてください。
~~~

## README の完全な改善内容

完全な README 改善では、リポジトリが初期化済みか、README が存在するか、プロジェクトの役割と読者経路が正しいかを確認してから、新規作成、全面改稿、再構成、圧縮を選びます。

- 文章：内部方法の写しと重複を除き、役割、成果、実際の入口、最初の成功、保守ナビゲーションを残します。
- 視覚：hero、画像、証拠の適格性を確認し、デスクトップ、狭い画面、GitHub の明暗テーマで検査します。
- ヘッダー：中文、English、日本語、文書、貢献、フィードバック、個人リンク、Stars、Forks、ライセンスを実際の事実から生成します。
- ライセンス：正しい既存ライセンスは維持し、存在しない場合は権利と採用目的を確認してから、承認済みの選択を適用します。
- Star History：公開 GitHub リポジトリで実際のワークフローを実行し、両方の SVG と README の消費を確認します。
- 公開：承認済みの既存リモートには正確にコミットして push し、リモート HEAD を確認します。リモート作成、公開範囲変更、強制 push、ファイル削除は自動では行いません。

詳しい手順は [README 完全配信方法](./references/readme-delivery.md) を参照してください。

## 処理の流れ

~~~text
ユーザー成果
  → プロジェクトの事実と権限
  → 予防 / 診断 / 実装
  → 正式な生産者と実際の境界
  → 最終消費者とユーザー結果
  → 旧経路の終了と回帰確認
~~~

Skill のメインファイルはルーティングだけを担当します。完全な方法は [references](./references/)、決定的なツールは [scripts](./scripts/) にあり、各プロジェクト固有の長期事実は、そのプロジェクトの既存ルール、コード、設定、テストに残ります。

## インストール

project-steward ディレクトリ全体を、Agent Skills 対応ツールが使用する Skills ディレクトリへ配置してください。SKILL.md、agents、references、scripts、assets をまとめて保持します。

その後、依頼の中で直接呼び出します。

~~~text
このプロジェクトを $project-steward で包括的に確認し、リスク順に改善案を示してください。
~~~

書き込み、実行、インストール、コミット、公開は依頼内容に応じて個別に許可されます。Project Steward の自己進化は二段階確認を使用し、将来の動作と影響範囲を先に提示し、承認後に自身を変更します。

## リポジトリ構成

| パス | 役割 |
| --- | --- |
| [SKILL.md](./SKILL.md) | 役割、主要ルート、権限、停止位置 |
| [references](./references/) | 各ガバナンス方法の唯一の所有者 |
| [scripts](./scripts/) | README、ライセンス、テンプレート、ディレクトリ、環境、Star History のツール |
| [assets](./assets/) | ライセンスカタログ、テンプレート、README profile、視覚素材 |
| [tests](./tests/) | アクティブなルート、方法の所有権、ツール、消費者契約 |

## 検証

すべてのアクティブテストを実行します。

~~~powershell
python -m unittest discover -s tests -v
~~~

3 言語の README を監査します。

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

このリポジトリの GitHub Actions は短期 github.token を使用し、専用の star-history ブランチへグラフを公開します。完全な生成経路は [Star History ガバナンス](./references/github-star-history.md) を参照してください。

## ライセンスと第三者ソース

Project Steward の主要なコードと文書は [Mozilla Public License 2.0](./LICENSE) で提供されます。

README の内容・視覚方法の一部は [oil-oil/beautify-github-readme](https://github.com/oil-oil/beautify-github-readme) を MIT License に従って改変したものです。正確な範囲と完全な通知は [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) と [NOTICE](./NOTICE) にあります。

問題や改善案は [GitHub Issues](https://github.com/CheshireMew/project-steward/issues) から送信できます。
