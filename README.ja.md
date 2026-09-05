<!-- readme-header:start -->

<p align="center">
  <img src="./assets/readme/hero.svg" width="160" alt="Project Steward">
</p>

<h1 align="center">Project Steward</h1>

<p align="center">
  <strong>プロジェクトの調査・監査、手戻りの予防、根本原因の修正、UI デザインと使いやすさの改善を支援する Agent Skill。</strong>
</p>

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

Project Steward は、対応する Agent が利用するプロジェクトガバナンス用の Skill です。リポジトリ、実装計画、UI の問題、タスクの全履歴を渡すことで、調査、完成度の確認、UI 設計・改善、手戻りの予防、複数層の不具合修正、開発・公開に必要な整理を依頼できます。

> 検査、監査、診断、振り返りは既定で読み取り専用です。実装を明示的に依頼した場合に、該当範囲を変更します。通常の機能実装や単一関数の質問は通常の開発タスクとして扱います。

## できること

### UI の設計・見た目・使いやすさを改善する

ゼロからの UI 設計、視覚的な方向性の変更、既存製品のレイアウト、書体、配色、情報階層、コンポーネント、操作、アニメーションの調整に対応します。参考 UI の再構築、複数ページのデザインシステム統一、デスクトップウィンドウ、レスポンシブ表示、ローカルファイルを扱う画面の改善も対象です。

関連ページ、ウィンドウ、主要状態を確認し、見た目、理解、操作を妨げる問題を調べます。実装が承認された後は、実際の入口から最終画面と連続操作を確認し、コード変更済み、画面検証済み、使用感確認済みを区別します。[製品体験と UI の方法](./references/product-experience-governance.md)を参照してください。

### プロジェクトを理解し、計画と完成度を照合する

未知のリポジトリの目的、動かし方、主要モジュールの関係を説明します。参考プロジェクトでは、学べる方法と実際に再利用できる内容を区別します。実装計画と照合して完了、漏れ、未検証を明らかにし、総合監査ではプロジェクトに適用される範囲を調べ、証拠に基づいて優先順位を付けます。

### 実装前に手戻りを防ぐ

機能追加、リファクタリング、移行の前に、目標、依存関係、影響する呼び出し元、変更順序、確認方法を整理します。変更に応じて性能、進捗表示、長時間処理、モデルが関与する処理、プロジェクト間のインターフェースを確認します。

### 根本原因から不具合を収束させる

症状から修正すべき原因をたどり、関連モジュール、データ、呼び出し元を変更して、古い実装の終了も確認します。結合、重複実装、責務が多すぎるモジュールを調べ、同じ問題への修正の繰り返しを防ぎます。

### プロジェクト・実行環境・公開を整える

| 作業 | 得られる結果 | 方法 |
| --- | --- | --- |
| ディレクトリ整理 | 使用中のファイル、ローカル状態、履歴を分け、除外・移動・保管案を提示 | [ディレクトリ](./references/repository-directory-governance.md) |
| 外部互換性 | ツール連携、公式形式、エクスポート経路の不整合を特定・修正 | [互換性](./references/external-tool-compatibility.md) |
| テンプレート | 基準の作成・採用・更新と、繰り返し適用できる方法の反映 | [テンプレート](./references/project-template-system.md) · [進化](./references/template-evolution.md) |
| ログと環境 | 実操作の追跡と、ツール、SDK、キャッシュ、長時間処理の条件確認 | [ログ](./references/log-audit-standard.md) · [環境](./references/user-environment-governance.md) |
| 実行時ストレージ | モデル、ダウンロード、メディア、キャッシュ、テスト出力の配置・増加・残留を管理 | [ストレージ](./references/production-storage-governance.md) |
| README と公開 | 紹介文、視覚素材、多言語、ライセンス、GitHub 情報の整理 | [README](./references/readme-delivery.md) · [ライセンス](./references/license-governance.md) · [公開](./references/repository-publication.md) |

### 実際のプロジェクト作業から学ぶ

タスクの全過程から有効な方法、失敗原因、ユーザーの修正を読み取り、次回の行動を提案します。確認後に再利用できる方法を Project Steward に反映し、プロジェクト固有の判断は、そのプロジェクトの文書、コード、設定に残します。

## そのまま依頼できます

対応する Agent で `$project-steward` を指定し、対象プロジェクトや資料を渡してください。確認、提案、実装のどこまで依頼するかを言葉で指定できます。

| 目的 | 依頼例 |
| --- | --- |
| UI 改善 | $project-steward でこのプロジェクトのレイアウト、情報階層、コンポーネント、操作を改善し、実際の画面と主要操作を確認してください。 |
| 新規設計 | $project-steward でこの製品の UI を設計し、まず構造と視覚的な方向性を選べるように提示してください。 |
| 参考 UI の再構築 | $project-steward でこの参考 UI を再構築し、実行結果との差を確認してください。 |
| リポジトリの理解 | $project-steward でこのリポジトリの目的、構造、動かし方を説明し、再利用に値する能力も別途評価してください。 |
| 計画の確認 | $project-steward で実装計画と照合し、完了、漏れ、未検証の項目を示してください。 |
| 総合監査 | $project-steward でプロジェクト全体を確認し、利用者への影響とリスク順に改善案を示してください。 |
| 変更前の確認 | $project-steward でこの変更の影響範囲、依存関係、確認方法を調べ、まず実装案を提示してください。 |
| 根本原因の修正 | $project-steward でこの問題を診断・修正し、関連する呼び出し元と実際の結果を確認してください。 |
| ファイル整理 | $project-steward で使用中のファイルとアップロード不要なファイルを調べ、まず整理案を示してください。 |
| 互換性の確認 | $project-steward でこの外部ツールや公式形式との互換性を調べ、失敗する箇所を示してください。 |
| テンプレート採用・更新 | $project-steward でプロジェクトの基準を確認し、テンプレートの採用・更新案を示してください。 |
| テンプレートの進化 | $project-steward でこれらの方法を安定した既定値にできるか判断し、該当テンプレートを更新してください。 |
| ログ改善 | $project-steward で一度の操作の入力、経過、失敗、結果を追えるようにログを改善してください。 |
| 環境確認 | $project-steward で必要なツール、SDK、キャッシュの場所を確認し、現在の不足を示してください。 |
| ストレージ管理 | $project-steward でモデル、メディア、キャッシュ、テスト出力の増加と残留を調べ、まず改善案を示してください。 |
| README 改善 | $project-steward でこの README の文章、多言語、ホームページ情報、関連する公開作業を改善してください。 |
| ライセンス確認 | $project-steward でライセンスと第三者ソースを確認し、適用範囲と調整案を示してください。 |
| 変更の公開 | $project-steward でアップロード内容を確認し、承認済みの変更を既存リモートへコミット・push してください。 |
| 会話から学ぶ | $project-steward でこのタスクの全履歴を読み、将来の行動と影響ファイルを提示してから、確認後に自己進化してください。 |

## README の完全な改善内容

プロジェクトの事実に基づいて主要用途と利用入口を整理し、文章、視覚素材、多言語、ナビゲーション、ライセンスを扱います。公開 GitHub リポジトリでは Star History、Topics、About Description も対象です。Website は条件を満たす正式な入口だけを使います。

- 視覚検査は素材ソースの構造と参照を対象とし、見た目の品質を検証したとは扱いません。
- Star History の実装はワークフロー起動後に停止します。グラフ生成とリモート表示は、別途検証を依頼されるまで未検証です。
- コミットと push は確認済みの範囲で行い、push 後の新しいリモート検査は待ちません。

詳しい範囲と実行条件は [README 完全配信方法](./references/readme-delivery.md) を参照してください。

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

~~~bash
npx skills add CheshireMew/project-steward
~~~

インストール後、依頼の中で直接呼び出します。

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

この README を確認します。他の言語は各ページに記載されたコマンドを使います。

~~~powershell
python scripts/audit_readme.py README.ja.md --header-profile assets/readme-profile/profile.json --repository CheshireMew/project-steward --language ja --project-name "Project Steward" --tagline "プロジェクトの調査・監査、手戻りの予防、根本原因の修正、UI デザインと使いやすさの改善を支援する Agent Skill。" --identity-image assets/readme/hero.svg --identity-image-width 160 --branch main --navigation-target docs=SKILL.md
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
