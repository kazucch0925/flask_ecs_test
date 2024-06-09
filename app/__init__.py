import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db' # SQLite3データベースの設定
    app.secret_key = 'your_secret_key_here' # セッション用の秘密鍵を設定

    # ログの設定
    logging.basicConfig(filename='app.log', level=logging.DEBUG)

    # データベースの初期化
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # ブループリントの登録
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    return app
