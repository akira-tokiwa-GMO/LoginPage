# API 仕様

Flask アプリケーションが提供する主要エンドポイントの入出力をまとめます。

| メソッド | パス | 入力 | 成功レスポンス | ステータスコード |
|---------|------|------|----------------|----------------|
| GET | `/register` | なし | 登録フォーム HTML | 200 |
| POST | `/register` | `username`, `email`, `password`, `csrf_token` | `/login` へリダイレクト | 302 |
| GET | `/login` | なし | ログインフォーム HTML | 200 |
| POST | `/login` | `email`, `password`, `csrf_token` | `/dashboard` へリダイレクト | 302 |
| POST | `/logout` | `csrf_token` | `/login` へリダイレクト | 302 |
| GET | `/dashboard` | Cookie に保存された `user_id` | ダッシュボード HTML | 200 または 302 |

エラー時は各テンプレート上にエラーメッセージを表示し、HTTP ステータスは基本的に 200 を返します。未ログインで `/dashboard` へアクセスした場合は `/login` へ 302 リダイレクトされます。
