import logging
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db' # SQLite3データベースの設定
    app.secret_key = 'your_secret_key_here' # セッション用の秘密鍵を設定

    # ログの設定
    logging.basicConfig(filename='app.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    
    # コンソールにもログを出力する設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(console_handler)

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

    # エラーハンドリング
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f'Server Error: {error}, route: {request.url}')
        return jsonify({"message": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error(f'Unhandled Exception: {e}, route: {request.url}')
        return jsonify({"message": "Unhandled exception occurred"}), 500

    return app
