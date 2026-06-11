# StudyLog

学習記録・日記・成長記録など、**時間軸の変化を追いたいあらゆる事象**を体系的に記録・管理するWebアプリです。

PCのフォルダ構造のように階層を作り、時間の流れに沿って記録を積み上げていくことができます。

---

## 📌 コンセプト

「時間軸の変化を追える事象には、体系的な階層構造が有用である」

学習記録はもちろん、日記・子供の成長記録・読書記録など、継続的に記録したいことであれば何にでも活用できます。

---

## 🖥️ 画面構成

```
カテゴリ選択（画面1）
  └── サブカテゴリ＋ログ一覧（画面2）
        └── 詳細ログ（画面3）
```

**画面1 - カテゴリ選択**
トップページ。記録の大分類をサイドバーで管理します。

**画面2 - サブカテゴリ＋ログ一覧**
カテゴリの中分類と、日付・タイトルのログ一覧を表示します。

**画面3 - 詳細ログ**
ログの詳細（タイトル・メモ・不明点）を表示します。

---

## ⚙️ 技術スタック

| カテゴリ | 技術 |
|---|---|
| フロントエンド | HTML / CSS / JavaScript |
| バックエンド | FastAPI |
| データベース | PostgreSQL |
| ORM | SQLAlchemy |
| バリデーション | Pydantic |
| ホスティング | Render |

---

## 🚀 主な機能

- カテゴリ・サブカテゴリ・詳細ログの3階層管理
- 各階層の追加・編集・削除（CRUD操作）
- 詳細ログへのメモ・不明点の記録
- カテゴリ一覧のスライドサイドバー

---

## 🗂️ ディレクトリ構成

```
StudyLog/
├── frontend/
│   ├── index.html       # カテゴリ選択画面
│   ├── category.html    # サブカテゴリ＋ログ一覧画面
│   └── log.html         # 詳細ログ画面
├── backend/
│   ├── main.py          # APIエンドポイント定義
│   ├── database.py      # DB接続設定
│   └── models.py        # テーブル定義
└── .gitignore
```

---

## 🔧 ローカル環境での起動方法

### 前提条件
- Python 3.11以上
- PostgreSQL

### セットアップ

```bash
# 依存ライブラリのインストール
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv

# 環境変数の設定
# backend/.env を作成して以下を記述
DATABASE_URL=postgresql://localhost/studylog

# サーバー起動
cd backend
uvicorn main:app --reload
```

フロントエンドは`frontend/index.html`をブラウザで直接開いてください。

---

## 📋 API一覧

| 対象 | メソッド | エンドポイント |
|---|---|---|
| カテゴリ | GET | /categories |
| カテゴリ | POST | /categories |
| カテゴリ | PUT | /categories/{id} |
| カテゴリ | DELETE | /categories/{id} |
| サブカテゴリ | GET | /subcategories/{category_id} |
| サブカテゴリ | POST | /subcategories |
| サブカテゴリ | PUT | /subcategories/{id} |
| サブカテゴリ | DELETE | /subcategories/{id} |
| ログ | GET | /logs/{subcategory_id} |
| ログ | GET | /logs/detail/{id} |
| ログ | POST | /logs |
| ログ | PUT | /logs/{id} |
| ログ | DELETE | /logs/{id} |

---

## 🔮 今後の予定（Ver2.0以降）

- 可変階層の実装（ユーザーが自由に深さを決められる）
- 認証機能の追加
- AI理解度テスト機能（学習内容から自動で問題を生成）
