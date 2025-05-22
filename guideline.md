# GitHub 運用ガイドライン

本ガイドラインは、本プロジェクトを効率的かつ品質高く運用するための
コーディング規約とブランチ戦略を定義します。

---

## 1. コーディング規約

### 1.1 スタイルガイド
- **Python**: PEP8 準拠、インデントはスペース4、行長 88 文字まで（Black 標準値）  
- **Docstring**: PEP257 準拠。モジュール／クラス／関数に必須。

### 1.2 フォーマット & リンティング
- **Black**: 自動フォーマット  
- **isort**: インポート整序  
- **Flake8**: コード品質チェック  
- **設定統合**: `pyproject.toml` で Black/isort、`.flake8` で Flake8 共有

### 1.3 テスト
- **pytest**: ユニット・統合テスト  
- **命名規則**: `tests/unit/`、`tests/integration/` 下に配置  
- **カバレッジ**: 80%以上を目標  
- **CI 自動実行**: GitHub Actions でプッシュ／PR 時に実行

### 1.4 コミット & PR
- **コミットメッセージ**: Conventional Commits  
- **コミットチェック**: `commitlint` の pre-commit フック  
- **Pull Request**  
  - 1 PR = 1 機能 or 1 修正  
  - CI 通過必須
  - PR テンプレートを利用し、目的・変更点・テスト結果を記入

---

## 2. ブランチ戦略

### 2.1 基本フロー（GitHub Flow 推奨）
1. `main` ブランチは常にデプロイ可能  
2. 新機能・バグ修正は全て `main` から派生する短命ブランチで実装  
```

git checkout main
git pull
git checkout -b feature/xxx-説明

```
3. 作業完了後は PR を切り、レビュー→CI→マージ→デプロイ

### 2.2 命名規則
- feature: `feature/説明`  
- bugfix: `bugfix/説明`  
- hotfix（緊急修正）: `hotfix/説明`  

### 2.3 リリース & タグ
- **Semantic Versioning** に準拠  
- `main` マージ後、`vMAJOR.MINOR.PATCH` タグを自動生成  
- リリースノートは GitHub Release 機能を利用
