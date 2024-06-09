FROM python:3.9

WORKDIR /app
ADD . /app

# パッケージをインストール
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# データベースの初期化
RUN python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

EXPOSE 80

# アプリケーションを実行
CMD ["python", "run.py"]
