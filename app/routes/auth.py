from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__, template_folder='../../templates')

# ユーザー登録ルート
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # メールアドレスの重複チェック
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            current_app.logger.warning('Registration failed for email: %s. Email already exists.', email)
            return render_template('register.html', message="このメールアドレスは既に使用されています")

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
        return redirect(url_for('main.index'))

    return render_template('register.html')

# ログインルート
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        # メールアドレスまたはユーザー名を検索
        user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()

        # ユーザーの存在とパスワードの検証
        if user is None:
            current_app.logger.warning('Login failed for identifier: %s. User not found. Session: %s', identifier, session)
            return render_template('login.html', message="このメールアドレスまたはユーザー名は登録されていません")
        elif not check_password_hash(user.password, password):
            current_app.logger.warning('Login failed for identifier: %s. Incorrect password. Session: %s', identifier, session)
            return render_template('login.html', message="パスワードが正しくありません")
        session['logged_in'] = True # ログイン済みであることを示すフラグをセット
        session['user_id'] = user.id # ユーザーIDをセッションに保存
        current_app.logger.info('User logged in: %s. Session: %s', identifier, session)
        return redirect(url_for('main.index'))

    return render_template('login.html')

# ログアウトルート
@auth_bp.route('/logout')
def logout():
    session.clear() # セッションをクリア
    session['registered'] = True # ログインページに飛ばすために登録済みフラグを立てる
    current_app.logger.info('User logged out. Session: %s', session)
    return redirect(url_for('main.index'))
