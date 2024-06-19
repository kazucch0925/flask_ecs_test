from flask import Blueprint, request, redirect, url_for, jsonify, session, current_app, render_template
from datetime import datetime
import pytz
from app.models import Todo
from app import db

tasks_bp = Blueprint('tasks', __name__, template_folder='../../templates')

# タスクの追加ルート
@tasks_bp.route('/todos', methods=['POST'])
def add_todo():
    current_app.logger.info('Task add route called.')
    if 'logged_in' in session and session['logged_in']:
        user_id = session.get('user_id')
        if user_id is None:
            current_app.logger.error('Error: user_id not found in session. Session: %s', session)
            return jsonify({"message": "user_id not found in session"}), 401
        data = request.get_json() or {}
        task = data.get('task')
        if not task: # タスクが未入力の場合のバリデーション
            todo_list = Todo.query.filter_by(user_id=user_id).all()
            current_app.logger.warning('Failed to add task. Task was empty. Session: %s', session)
            return jsonify({"message": "タスクを入力してください"}), 400

        # 日本時間に変換
        tokyo_tz = pytz.timezone('Asia/Tokyo')
        now = datetime.now(tokyo_tz)

        new_todo = Todo(task=task, created_at=now, user_id=user_id)
        db.session.add(new_todo)
        db.session.commit()
        current_app.logger.info('Task added at Tokyo time: %s. Session: %s', now.isoformat(), session)
        return jsonify({"id": new_todo.id, "task": new_todo.task, "created_at": new_todo.created_at.isoformat()}), 201
    return jsonify({"message": "Unauthorized"}), 401

# タスクの削除ルート
@tasks_bp.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    if 'logged_in' in session and session['logged_in']:
        user_id = session.get('user_id') # セッションからuser_idを取得
        if user_id is None:
            current_app.logger.error('Error: user_id not found in session. Session: %s', session)
            return redirect(url_for('auth.logout')) # user_idが見つからなかった場合はログアウト
        todo = db.session.get(Todo, id)
        if todo and todo.user_id == user_id:
            db.session.delete(todo)
            db.session.commit()
            current_app.logger.info('Task deleted: %s. Session: %s', todo.task, session)
            return '', 204
        else:
            current_app.logger.error('Error: Task not found or unauthorized access. Session: %s', session)
            return jsonify({"message": "Task not found or unauthorized access"}), 404
    return jsonify({"message": "Unauthorized"}), 401

# タスクの編集ルート (PUT: タスクの更新)
@tasks_bp.route('/todos/<int:id>', methods=['PUT'])
def edit_todo(id):
    if 'logged_in' in session and session['logged_in']:
        user_id = session.get('user_id') # セッションからuser_idを取得
        if user_id is None:
            current_app.logger.error('Error: user_id not found in session. Session: %s', session)
            return redirect(url_for('auth.logout')) # user_idが見つからなかった場合はログアウト
        todo = db.session.get(Todo, id)
        if todo and todo.user_id == user_id:
            data = request.get_json() or {}
            task = data.get('task')
            if not task: # タスクが未入力の場合のバリデーション
                current_app.logger.warning('Failed to edit task. Task was empty. Session: %s', session)
                return jsonify({"message": "タスクを入力してください"}), 400
            todo.task = task
            db.session.commit()
            current_app.logger.info('Task edited: %s. Session: %s', task, session)
            return jsonify({"id": todo.id, "task": todo.task, "created_at": todo.created_at}), 200
        else:
            current_app.logger.error('Error: Task not found or unauthorized access. Session: %s', session)
            return jsonify({"message": "Task not found or unauthorized access"}), 404
    return jsonify({"message": "Unauthorized"}), 401

# タスクの編集フォーム表示ルート (GET: 編集フォームの表示)
@tasks_bp.route('/todos/<int:id>', methods=['GET'])
def get_todo_by_id(id):
    if 'logged_in' in session and session['logged_in']:
        user_id = session.get('user_id')
        if user_id is None:
            current_app.logger.error('Error: user_id not found in session. Session: %s', session)
            return redirect(url_for('auth.logout'))
        todo = db.session.get(Todo, id)
        if todo and todo.user_id == user_id:
            return render_template('edit.html', todo=todo)
        else:
            current_app.logger.error('Error: Task not found or unauthorized access. Session: %s', session)
            return jsonify({"message": "Task not found or unauthorized access"}), 404
    return jsonify({"message": "Unauthorized"}), 401
