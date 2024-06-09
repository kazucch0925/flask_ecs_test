from flask import Blueprint, request, redirect, url_for, render_template, session, current_app
from datetime import datetime
from app.models import Todo
from app import db

tasks_bp = Blueprint('tasks', __name__, template_folder='../../templates')

# タスクの追加ルート
@tasks_bp.route('/add', methods=['POST'])
def add():
    if 'logged_in' in session and session['logged_in']:
        user_id = session.get('user_id')
        if user_id is None:
            current_app.logger.error('Error: user_id not found in session. Session: %s', session)
            return redirect(url_for('auth.logout')) # user_idが見つからなかった場合はログアウト
        task = request.form['task']
        if not task: # タスクが未入力の場合のバリデーション
            todo_list = Todo.query.filter_by(user_id=user_id).all()
            current_app.logger.warning('Failed to add task. Task was empty. Session: %s', session)
            return render_template('index.html', todo_list=todo_list, message="タスクを入力してください")
        new_todo = Todo(task=task, created_at=datetime.utcnow(), user_id=user_id)
        db.session.add(new_todo)
        db.session.commit()
        current_app.logger.info('Task added: %s. Session: %s', task, session)
    return redirect(url_for('main.index'))

# タスクの削除ルート
@tasks_bp.route('/delete/<int:id>')
def delete(id):
    if 'logged_in' in session and session['logged_in']:
        user_id = session.get('user_id') # セッションからuser_idを取得
        if user_id is None:
            current_app.logger.error('Error: user_id not found in session. Session: %s', session)
            return redirect(url_for('auth.logout')) # user_idが見つからなかった場合はログアウト
        todo = Todo.query.get(id)
        if todo and todo.user_id == user_id:
            db.session.delete(todo)
            db.session.commit()
            current_app.logger.info('Task deleted: %s. Session: %s', todo.task, session)
        else:
            current_app.logger.error('Error: Task not found or unauthorized access. Session: %s', session)
            return "Error: Task not found or unauthorized access"
    return redirect(url_for('main.index'))

# タスクの編集ルート
@tasks_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'logged_in' in session and session['logged_in']:
        user_id = session.get('user_id') # セッションからuser_idを取得
        if user_id is None:
            current_app.logger.error('Error: user_id not found in session. Session: %s', session)
            return redirect(url_for('auth.logout')) # user_idが見つからなかった場合はログアウト
        todo = Todo.query.get(id)
        if todo and todo.user_id == user_id:
            if request.method == 'POST':
                task = request.form['task']
                if not task: # タスクが未入力の場合のバリデーション
                    current_app.logger.warning('Failed to edit task. Task was empty. Session: %s', session)
                    return render_template('edit.html', todo=todo, message="タスクを入力してください")
                todo.task = task
                db.session.commit()
                current_app.logger.info('Task edited: %s. Session: %s', task, session)
                return redirect(url_for('main.index'))
            else:
                return render_template('edit.html', todo=todo)
        else:
            current_app.logger.error('Error: Task not found or unauthorized access. Session: %s', session)
            return "Error: Task not found or unauthorized access"
    else:
        return redirect(url_for('auth.login'))
