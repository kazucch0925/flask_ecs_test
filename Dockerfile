FROM python:3.9

WORKDIR /app
ADD . /app

# タイムゾーンを日本時間に設定
RUN apt-get update && apt-get install -y tzdata
ENV TZ=Asia/Tokyo

# DNSの設定
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf

# パッケージをインストール
RUN pip install --upgrade pip && pip install -r requirements.txt

# データベースの初期化
RUN python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

EXPOSE 80

# アプリケーションを実行
CMD ["python", "run.py"]
