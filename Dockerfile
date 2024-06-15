FROM python:3.9

# 作業ディレクトリの設定
WORKDIR /app

# アプリケーションコードをコンテナにコピー
ADD . /app

# タイムゾーンを日本時間に設定
RUN apt-get update && apt-get install -y tzdata
ENV TZ=Asia/Tokyo

# パッケージをインストール
RUN pip install --upgrade pip && pip install -r requirements.txt

# データベースの初期化
RUN python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# コンテナがリッスンするポートを指定
EXPOSE 80

# アプリケーションを実行
CMD ["python", "run.py"]
