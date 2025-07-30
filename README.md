# Flask Todo アプリケーション - CI/CD環境デモ

## 📋 概要

この Flask Todo アプリケーションは、AWS での完全な CI/CD パイプラインの実装を示すデモンストレーションプロジェクトです。ユーザー登録・認証機能を持つTodo管理システムと、GitHub → CodeBuild → ECS への自動デプロイフローを実装しています。

### 🎯 プロジェクトの目的

- モダンなCI/CDパイプラインの実装例を提供
- AWS CloudFormation によるインフラストラクチャ・アズ・コード（IaC）の実践
- コンテナ化された Web アプリケーションの本番デプロイメント

## 🏗️ アーキテクチャ

### システム構成

```
GitHub → AWS CodePipeline → CodeBuild → Amazon ECR → Amazon ECS
```

### 使用技術スタック

**フロントエンド:**
- HTML5, CSS3, JavaScript（ES6）
- Responsive Design

**バックエンド:**
- Python 3.9+
- Flask (Webフレームワーク)
- Flask-SQLAlchemy (ORM)
- SQLite (開発環境データベース)

**インフラストラクチャ:**
- AWS CodePipeline (CI/CDパイプライン)
- AWS CodeBuild (ビルド・テスト)
- Amazon ECR (コンテナレジストリ)
- Amazon ECS (コンテナオーケストレーション)
- AWS CloudFormation (インフラ管理)
- Docker (コンテナ化)

**品質管理ツール:**
- Playwright (E2Eテスト - ※別リポジトリで管理)

## 📁 プロジェクト構成

```
flask_ecs_test/
├── app/                          # Flaskアプリケーション本体
│   ├── __init__.py              # アプリケーション初期化
│   ├── models.py                # データベースモデル
│   └── routes/                  # ルーティング定義
│       ├── auth.py              # 認証関連API
│       ├── main.py              # メインページ
│       └── tasks.py             # Todo管理API
├── templates/                    # HTMLテンプレート
│   ├── index.html               # メインページ
│   ├── login.html               # ログインページ
│   ├── register.html            # ユーザー登録ページ
│   └── edit.html                # タスク編集ページ
├── static/                      # 静的ファイル
│   ├── styles.css               # スタイルシート
│   ├── scripts.js               # JavaScript
│   ├── favicon.ico              # ファビコン
│   └── uploads/                 # アップロード画像
├── cloudformation/              # AWS CloudFormationテンプレート
│   └── template.yaml            # インフラ定義
├── 構成図/                      # アーキテクチャ図
├── Dockerfile                   # コンテナイメージ定義
├── buildspec.yml                # CodeBuildビルド仕様
├── openapi.yaml                 # API仕様書
├── requirements.txt             # Python依存関係
└── run.py                       # アプリケーションエントリーポイント
```

## 🚀 機能一覧

### 認証機能
- ユーザー登録（ユーザー名・メールアドレス・パスワード）
- ログイン・ログアウト
- セッション管理

### Todo管理機能
- タスクの作成・閲覧・編集・削除
- 優先度設定（高・中・低）
- 期限日設定
- タグ機能
- 画像添付機能
- タスク検索
- 一括選択・削除
- リアルタイム通知（Toast）

### API機能
- RESTful API設計
- OpenAPI 3.0仕様書
- JSON形式でのデータ交換

## 🛠️ セットアップ手順

### 前提条件

- AWS アカウント
- GitHub アカウント
- Docker Desktop（**推奨** - ローカル開発時）
- Python 3.9+（Dockerを使わない場合）

> 💡 **推奨**: ローカルでの動作確認には **Docker を使用する方法（セクション3）** をお勧めします。環境構築が簡単で、本番環境との差異を最小限に抑えられます。

### 1. リポジトリの準備

```bash
# リポジトリをフォークまたはクローン
git clone <your-forked-repo-url>
cd flask_ecs_test
```

### 2. Python環境でのローカル開発（Docker未使用の場合）

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt

# アプリケーションの起動
python run.py
```

ブラウザで `http://localhost:80` にアクセスしてアプリケーションを確認できます。

### 3. Dockerを使用したローカル環境のセットアップ（推奨）

Dockerを使用することで、環境構築を簡単に行うことができます。

```bash
# Dockerイメージのビルド
docker build -t todo_flask .

# Dockerコンテナを起動（container_nameは任意の名前に変更可能）
docker run --name todo_container -d -p 80:80 todo_flask

# ブラウザで http://localhost:80 にアクセス
```

**Dockerコンテナの管理:**

```bash
# コンテナの停止
docker stop todo_container

# コンテナの再起動
docker start todo_container

# コンテナの削除（停止後に実行）
docker rm todo_container

# イメージの削除
docker rmi todo_flask

# 実行中のコンテナを確認
docker ps

# 全てのコンテナを確認（停止中も含む）
docker ps -a
```

**開発時の便利なオプション:**

```bash
# ログをリアルタイムで確認
docker logs -f todo_container

# コンテナ内でbashを実行（デバッグ用）
docker exec -it todo_container bash

# ボリュームマウントで開発（ソースコード変更を即座に反映）
docker run --name todo_dev -d -p 80:80 -v $(pwd):/app todo_flask
```

### 4. AWS環境のセットアップ

#### 4.1 必要な設定の変更

**⚠️ 重要: 以下の設定を必ずあなたの環境に合わせて変更してください**

#### A. CloudFormationテンプレート（`cloudformation/template.yaml`）

以下のパラメータのデフォルト値を変更：

```yaml
Parameters:
  NotificationEmail:
    Default: 'your-email@example.com'  # ← あなたのメールアドレス
  
  SlackWebhookUrl:
    Default: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'  # ← あなたのSlack Webhook URL
  
  ConnectionArn:
    Default: 'arn:aws:codeconnections:REGION:ACCOUNT-ID:connection/YOUR-CONNECTION-ID'  # ← あなたのCodeStar Connection ARN
```

また、以下の箇所の GitHub ユーザー名を変更：

```yaml
# 582行目付近
Location: !Sub 'https://github.com/YOUR-USERNAME/${TestRepositoryName}.git'

# 651行目と665行目付近
FullRepositoryId: !Sub 'YOUR-USERNAME/${AppRepositoryName}'
FullRepositoryId: !Sub 'YOUR-USERNAME/${TestRepositoryName}'
```

#### B. アプリケーション設定（`app/__init__.py`）

```python
# セキュリティ上重要: 必ず変更してください
app.secret_key = 'your-unique-secret-key-here'  # ← ランダムな文字列に変更

# 本番環境では外部データベースを推奨
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'  # ← 必要に応じて変更
```

#### C. ビルド仕様（`buildspec.yml`）

AWS Secrets Manager にDocker Hub認証情報を保存し、シークレット名を変更：

```yaml
env:
  secrets-manager:
    DOCKERHUB_USER: arn:aws:secretsmanager:$AWS_DEFAULT_REGION:$AWS_ACCOUNT_ID:secret:YOUR-SECRET-NAME:username
    DOCKERHUB_PASS: arn:aws:secretsmanager:$AWS_DEFAULT_REGION:$AWS_ACCOUNT_ID:secret:YOUR-SECRET-NAME:password
```

#### 4.2 AWS リソースの作成

1. **CodeStar Connection の作成**
   ```bash
   aws codeconnections create-connection \
     --provider-type GitHub \
     --connection-name your-github-connection
   ```

2. **Secrets Manager でDocker Hub認証情報を保存**
   ```bash
   aws secretsmanager create-secret \
     --name your-secret-name \
     --description "Docker Hub credentials"
   ```

3. **CloudFormation スタックのデプロイ**
   ```bash
   aws cloudformation create-stack \
     --stack-name flask-ecs-cicd \
     --template-body file://cloudformation/template.yaml \
     --parameters ParameterKey=AccountID,ParameterValue=YOUR-AWS-ACCOUNT-ID \
                  ParameterKey=ConnectionArn,ParameterValue=YOUR-CONNECTION-ARN \
     --capabilities CAPABILITY_IAM
   ```

## 📊 監視・通知

### 通知設定

CI/CDパイプラインの実行状況は以下で通知されます：

- **メール通知**: CloudFormationで設定したメールアドレス
- **Slack通知**: 設定したSlack Webhook URL
- **AWS CloudWatch**: ビルドログとメトリクス

## 🔧 カスタマイズ

### データベース変更

本番環境では外部データベースの使用を推奨：

```python
# PostgreSQL例
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host:port/dbname'

# MySQL例
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@host:port/dbname'
```

### タイムゾーン変更

```dockerfile
# Dockerfile
ENV TZ=America/New_York  # お住まいの地域に変更
```

### 通知のカスタマイズ

Slack通知のメッセージフォーマットは `cloudformation/template.yaml` の Lambda関数内で変更可能です。

## 🚨 トラブルシューティング

### よくある問題

1. **CodePipeline が失敗する**
   - CodeStar Connection の承認が完了しているか確認
   - IAMロールの権限を確認

2. **ビルドが失敗する**
   - Secrets Manager の認証情報を確認
   - buildspec.yml のシークレット名を確認

3. **ECS デプロイが失敗する**
   - ECS クラスター・サービスが正しく作成されているか確認
   - タスク定義のリソース設定を確認

### ログの確認

```bash
# CloudWatch ログ
aws logs describe-log-groups
aws logs get-log-events --log-group-name /aws/codebuild/your-project

# ECS タスクログ
aws ecs describe-tasks --cluster your-cluster --tasks your-task-id
```

## 📄 ライセンス

このプロジェクトはオープンソースです。自由にカスタマイズ・利用してください。

## 🤝 コントリビューション

1. フォークする
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📞 サポート

質問や問題がある場合は、GitHubのIssuesを作成してください。

---

**⚠️ 注意事項:**
- 本番環境では適切なセキュリティ設定を行ってください
- AWSリソースの利用には料金が発生します
- 不要になったリソースは必ず削除してください

**🎉 Happy Coding!** 