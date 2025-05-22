## 1. はじめに
### 1.1 目的
本ドキュメントは、ローカル SQLite にユーザーテーブルを持つ認証機能付き Web アプリケーションの要件を定義し、
システム開発チームおよびステークホルダー間の共通理解を確立することを目的とします。

### 1.2 範囲
- **In-Scope**: ユーザー登録、ログイン認証、成功ページ、ログアウト
- **Out-Of-Scope**: パスワードリセット、多要素認証（MFA）、管理者機能、外部サービス連携

## 2. 用語集
| 用語           | 定義                                   |
|----------------|----------------------------------------|
| SRS            | Software Requirements Specification    |
| MVP            | Minimum Viable Product                 |
| WAL            | Write-Ahead Logging                    |

## 3. 機能要件 (Functional Requirements) 
### 3.1 ユーザー登録
- **入力項目**: ユーザー名（必須, <=50 文字）、メールアドレス（必須, フォーマット検証）、パスワード（必須, 強度チェック）
- **バリデーション**: 入力エラー時にフィールド毎のメッセージを表示
- **保存**: パスワードはハッシュ化（bcrypt 推奨）して保存

### 3.2 ログイン
- **入力項目**: メールアドレス, パスワード
- **認証**: ハッシュ比較による認証処理
- **遷移**: 認証成功 → 成功ページ、失敗 → エラーメッセージ表示

### 3.3 成功ページ (Dashboard)
- **表示内容**: ようこそメッセージ（ユーザー名表示）
- **操作**: ログアウトボタン（セッション破棄後、ログインページへ遷移）

## 4. 非機能要件 (Non-functional Requirements) 
### 4.1 セキュリティ
- **パスワード管理**: bcrypt ハッシュ保存
- **セッション管理**: HTTP-Only Cookie、CSRF トークン、15 分のセッションタイムアウト
- **パスワード強度メーター**: ユーザビリティ向上のため実装

### 4.2 パフォーマンス
- SQLite の **WAL モード**を有効化し、同時書き込み性能を向上
- 適宜 **インデックス**を設計（メールアドレスにユニークインデックス）

### 4.3 可用性・信頼性
- ローカル DB ファイルの**バックアップ／リストア手順**をドキュメント化
- **ログ出力レベル**（INFO/ERROR）を統一

### 4.4 保守性・拡張性
- **モジュール設計**: MVC パターン採用
- **テスト**: ユニットテスト、統合テストのカバレッジ確保

### 4.5 ユーザビリティ・アクセシビリティ
- WCAG 2.1 レベル AA 準拠
- レスポンシブデザイン対応

## 5. データ要件 (Data Requirements) 
```sql
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL CHECK(length(username) <= 50),
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
PRAGMA journal_mode = WAL;
````

## 6. 受け入れ基準 (Acceptance Criteria) 

* **登録成功**: Given 正しい情報, When 「登録」クリック, Then 「ログインページへリダイレクト」
* **パスワード強度不足**: Given 弱いパスワード, When 入力完了, Then エラー「パスワードが弱すぎます」

## 7. 制約事項

* **プラットフォーム**: ローカル環境限定（SQLite 利用）
* **言語／フレームワーク**: Python 3.9+, Flask 2.x

## 8. 将来拡張 (Future Scope)

* パスワードリセット／MFA
* プロファイル編集機能
* 多言語対応

## 9. MVP 要件 

* ユーザー登録（ハッシュ化保存）
* ログイン／セッション管理
* 成功ページ表示
* 基本的なエラーメッセージ

## 10. 依存関係・技術選定

* Python 3.9+, Flask, SQLite, bcrypt ライブラリ
* フロントエンド: HTML/CSS/JavaScript (Vanilla or Bootstrap)

## 11. セットアップ

```bash
pip install -e .[dev]
init-db
```

上記コマンドで依存関係のインストールとデータベース初期化が行えます。
