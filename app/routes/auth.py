from flask import Blueprint, request, redirect, url_for, jsonify, session, current_app, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__, template_folder='../../templates')

# ユーザー登録ルート
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # ユーザーIDの重複チェック
    existing_user_username = User.query.filter_by(username=username).first()
    if existing_user_username:
        current_app.logger.warning('Registration failed for username: %s. Username already exists.', username)
        return jsonify({"message": "このユーザー名は既に使用されています"}), 400

    # メールアドレスの重複チェック
    existing_user_email = User.query.filter_by(email=email).first()
    if existing_user_email:
        current_app.logger.warning('Registration failed for email: %s. Email already exists.', email)
        return jsonify({"message": "このメールアドレスは既に使用されています"}), 400

    # パスワードのハッシュ化
    hashed_password = generate_password_hash(password)

    # ユーザーオブジェクトの作成とデータベースへの保存
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    session['registered'] = True # ユーザーが登録済みであることを示すフラグをセット
    session['user_id'] = new_user.id # ユーザーIDをセッションに保存
    session['logged_in'] = True # 登録後は即メインページの方が良い気がするのでログイン判定にする

    current_app.logger.info('User registered: %s. Session: %s', username, session)
    return jsonify({"message": "User registered successfully"}), 201

# ログインルート
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json()
    identifier = data.get('identifier')
    password = data.get('password')

    # メールアドレスまたはユーザー名を検索
    user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()

    # ユーザーの存在とパスワードの検証
    if user is None:
        current_app.logger.warning('Login failed for identifier: %s. User not found. Session: %s', identifier, session)
        return jsonify({"message": "このメールアドレスまたはユーザー名は登録されていません"}), 400
    elif not check_password_hash(user.password, password):
        current_app.logger.warning('Login failed for identifier: %s. Incorrect password. Session: %s', identifier, session)
        return jsonify({"message": "パスワードが正しくありません"}), 400

    session['logged_in'] = True # ログイン済みであることを示すフラグをセット
    session['user_id'] = user.id # ユーザーIDをセッションに保存
    current_app.logger.info('User logged in: %s. Session: %s', identifier, session)
    return jsonify({"message": "User logged in successfully"}), 200

# ログアウトルート
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear() # セッションをクリア
    current_app.logger.info('User logged out. Session: %s', session)
    return jsonify({"message": "User logged out successfully", "redirect": '/login'}), 200
