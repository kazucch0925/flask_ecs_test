from flask import Blueprint, render_template, redirect, url_for, session, current_app
from app.models import Todo
from app import db

main_bp = Blueprint('main', __name__, template_folder='../../templates')

@main_bp.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        user_id = session.get('user_id')
        if user_id is None:
            current_app.logger.error('Error: user_id not found in session. Session: %s', session)
            return redirect(url_for('auth.logout')) # user_idが見つからなかった場合はログアウト
        todo_list = Todo.query.filter_by(user_id=user_id).all()
        current_app.logger.info('Accessed index page. Session: %s', session)
        return render_template('index.html', todo_list=todo_list) # ログイン済みの場合、メインページにリダイレクト
    elif 'registered' in session and session['registered']:
        return redirect(url_for('auth.login')) # 登録済みの場合、ログインページにリダイレクト
    else:
        return redirect(url_for('auth.register')) # 未登録の場合、ユーザー登録ページにリダイレクト
