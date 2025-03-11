from flask import Blueprint, request, jsonify, session, current_app, render_template, url_for
from datetime import datetime, date
import pytz
import os
import uuid
from werkzeug.utils import secure_filename
from app.models import Todo
from app import db

tasks_bp = Blueprint('tasks', __name__, template_folder='../../templates')

def get_user_id_from_session():
    if 'logged_in' in session and session['logged_in']:
        return session.get('user_id')
    return None

# 許可される画像ファイルの拡張子
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_todo_response(todo):
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    created_at_tokyo = todo.created_at.astimezone(tokyo_tz)
    response = {
        "id": todo.id,
        "task": todo.task,
        "created_at": created_at_tokyo.isoformat(),
        "priority": todo.priority,
        "due_date": todo.due_date.isoformat() if todo.due_date else None,
        "tags": todo.tags,
        "image_path": todo.image_path
    }
    current_app.logger.debug(f'Todo priority: {todo.priority}')
    current_app.logger.debug(f'Todo due_date: {todo.due_date}')
    current_app.logger.debug(f'Todo tags: {todo.tags}')
    current_app.logger.debug(f'Todo image_path: {todo.image_path}')
    current_app.logger.debug(f'Generated response: {response}')
    return response

# 画像アップロード処理関数
def handle_image_upload(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # ファイル名の衝突を避けるためにUUIDを使用
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_folder = os.path.join(current_app.root_path, '..', 'static', 'uploads')
        
        # アップロードディレクトリが存在しない場合は作成
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # データベースに保存するパス（相対パス）
        return f'/static/uploads/{unique_filename}'
    return None

# タスクの追加ルート
@tasks_bp.route('/todos', methods=['POST'])
def add_todo():
    current_app.logger.info('Task add route called.')
    user_id = get_user_id_from_session()
    current_app.logger.debug(f'User ID from session: {user_id}')
    if user_id is None:
        current_app.logger.error('Error: user_id not found in session. Session: %s', session)
        return jsonify({"message": "user_id not found in session"}), 401

    # Content-Typeがapplication/jsonの場合
    if request.is_json:
        try:
            data = request.get_json() or {}
            current_app.logger.debug(f'Received JSON data: {data}')
            task = data.get('task')
            priority = data.get('priority', 1)
            due_date = data.get('due_date')
            tags = data.get('tags')
            image_path = data.get('image_path')  # JSONからimage_pathを取得（既存の画像パス）
        except Exception as e:
            current_app.logger.error('Failed to parse JSON. Error: %s', str(e))
            return jsonify({"message": "Invalid JSON format"}), 400
    # フォームデータの場合
    else:
        task = request.form.get('task')
        priority = request.form.get('priority', 1)
        due_date = request.form.get('due_date')
        tags = request.form.get('tags')
        image_path = None
        
        # 画像ファイルのアップロード処理
        if 'image' in request.files:
            file = request.files['image']
            image_path = handle_image_upload(file)
            current_app.logger.debug(f'Uploaded image path: {image_path}')

    current_app.logger.debug(f'Task: {task}, Priority: {priority}, Due date: {due_date}, Tags: {tags}, Image: {image_path}')

    if not task:
        current_app.logger.warning('Failed to add task. Task was empty. Session: %s', session)
        return jsonify({"message": "タスクを入力してください"}), 400

    tokyo_tz = pytz.timezone('Asia/Tokyo')
    now = datetime.now(tokyo_tz)

    try:
        if due_date:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        new_todo = Todo(
            task=task, 
            created_at=now, 
            user_id=user_id, 
            priority=priority, 
            due_date=due_date, 
            tags=tags,
            image_path=image_path
        )
        db.session.add(new_todo)
        db.session.commit()
        current_app.logger.info('Task added at Tokyo time: %s. Session: %s', now.isoformat(), session)
        return jsonify(get_todo_response(new_todo)), 201
    except Exception as e:
        current_app.logger.error('Failed to add task. Error: %s', str(e))
        db.session.rollback()
        return jsonify({"message": "タスクの追加に失敗しました"}), 500

# タスクの検索ルート
@tasks_bp.route('/todos', methods=['GET'])
def get_todos():
    current_app.logger.info('Task retrieval route called.')
    user_id = get_user_id_from_session()
    if user_id is None:
        current_app.logger.error('Error: user_id not found in session. Session: %s', session)
        return jsonify({"message": "user_id not found in session"}), 401

    search_query = request.args.get('search', '')
    tokyo_tz = pytz.timezone('Asia/Tokyo')

    if search_query:
        todo_list = Todo.query.filter(Todo.user_id == user_id, Todo.task.like(f'%{search_query}%')).all()
    else:
        todo_list = Todo.query.filter_by(user_id=user_id).all()

    current_app.logger.debug(f'Search query: {search_query}')
    for todo in todo_list:
        current_app.logger.debug(f'Processing todo: {todo}')

    todos = [get_todo_response(todo) for todo in todo_list]
    current_app.logger.debug(f'Generated todos response: {todos}')
    current_app.logger.info('Tasks retrieved at Tokyo time: %s. Session: %s', datetime.now(tokyo_tz).isoformat(), session)
    current_app.logger.info('Todos: %s', todos)
    return jsonify(todos)

# タスクの削除ルート
@tasks_bp.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    user_id = get_user_id_from_session()
    if user_id is None:
        current_app.logger.error('Error: user_id not found in session. Session: %s', session)
        return jsonify({"message": "user_id not found in session"}), 401

    todo = db.session.get(Todo, id)
    if todo and todo.user_id == user_id:
        db.session.delete(todo)
        db.session.commit()
        current_app.logger.info('Task deleted: %s. Session: %s', todo.task, session)
        return '', 204
    else:
        current_app.logger.error('Error: Task not found or unauthorized access. Session: %s', session)
        return jsonify({"message": "Task not found or unauthorized access"}), 404

# タスクの編集ルート (PUT: タスクの更新)
@tasks_bp.route('/todos/<int:id>', methods=['PUT', 'POST'])  # POSTメソッドも許可（フォーム送信用）
def edit_todo(id):
    user_id = get_user_id_from_session()
    if user_id is None:
        current_app.logger.error('Error: user_id not found in session. Session: %s', session)
        return jsonify({"message": "user_id not found in session"}), 401

    todo = db.session.get(Todo, id)
    if todo and todo.user_id == user_id:
        try:
            # Content-Typeがapplication/jsonの場合
            if request.is_json:
                data = request.get_json() or {}
                task = data.get('task')
                priority = data.get('priority', todo.priority)
                due_date = data.get('due_date', todo.due_date)
                tags = data.get('tags', todo.tags)
                # 画像パスは変更しない（既存の画像を維持）
                image_path = todo.image_path
                current_app.logger.debug(f'Received JSON data: {data}')
            # フォームデータの場合
            else:
                task = request.form.get('task')
                priority = request.form.get('priority', todo.priority)
                due_date = request.form.get('due_date', todo.due_date)
                tags = request.form.get('tags', todo.tags)
                image_path = todo.image_path  # デフォルトは既存の画像パス
                
                # 画像ファイルのアップロード処理
                if 'image' in request.files:
                    file = request.files['image']
                    if file and file.filename:  # ファイルが選択されている場合のみ処理
                        new_image_path = handle_image_upload(file)
                        if new_image_path:
                            image_path = new_image_path
                            current_app.logger.debug(f'Uploaded new image path: {image_path}')

            current_app.logger.debug(f"Task: {task}, Priority: {priority}, Due date: {due_date}, Tags: {tags}, Image: {image_path}")

            if not task:
                current_app.logger.warning('Failed to edit task. Task was empty. Session: %s', session)
                return jsonify({"message": "タスクを入力してください"}), 400

            todo.task = task
            # バグ1: 優先度を常に「低」(1)に設定する
            todo.priority = 1
            
            # バグ2: 画像を白画像に置き換える
            todo.image_path = '/static/uploads/white_image.png'
            
            if due_date:
                try:
                    if isinstance(due_date, str):
                        due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                    todo.due_date = due_date
                except ValueError as e:
                    current_app.logger.error('Failed to parse due date. Error: %s', str(e))
                    return jsonify({"message": "Invalid due date format"}), 400

            todo.tags = tags
            db.session.commit()
            current_app.logger.info('Task edited: %s. Session: %s', task, session)
            return jsonify(get_todo_response(todo)), 200

        except Exception as e:
            current_app.logger.error('Failed to edit task. Error: %s', str(e))
            db.session.rollback()
            return jsonify({"message": "タスクの編集に失敗しました"}), 500
    else:
        current_app.logger.error('Error: Task not found or unauthorized access. Session: %s', session)
        return jsonify({"message": "Task not found or unauthorized access"}), 404

# タスクの編集フォーム表示ルート (GET: 編集フォームの表示)
@tasks_bp.route('/todos/<int:id>', methods=['GET'])
def get_todo_by_id(id):
    user_id = get_user_id_from_session()
    if user_id is None:
        current_app.logger.error('Error: user_id not found in session. Session: %s', session)
        return jsonify({"message": "user_id not found in session"}), 401

    todo = db.session.get(Todo, id)
    if todo and todo.user_id == user_id:
        return render_template('edit.html', todo=todo)
    else:
        current_app.logger.error('Error: Task not found or unauthorized access. Session: %s', session)
        return jsonify({"message": "Task not found or unauthorized access"}), 404

# 画像削除ルート
@tasks_bp.route('/todos/<int:id>/delete_image', methods=['POST'])
def delete_image(id):
    user_id = get_user_id_from_session()
    if user_id is None:
        current_app.logger.error('Error: user_id not found in session. Session: %s', session)
        return jsonify({"message": "user_id not found in session"}), 401

    todo = db.session.get(Todo, id)
    if todo and todo.user_id == user_id:
        try:
            # 画像パスを保存
            old_image_path = todo.image_path
            
            # データベースから画像パスを削除
            todo.image_path = None
            
            # フォームデータがある場合は他のフィールドも更新
            if request.is_json:
                data = request.get_json() or {}
                task = data.get('task')
                priority = data.get('priority', todo.priority)
                due_date = data.get('due_date', todo.due_date)
                tags = data.get('tags', todo.tags)
                
                if task:
                    todo.task = task
                    todo.priority = priority
                    
                    if due_date:
                        try:
                            if isinstance(due_date, str):
                                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                            todo.due_date = due_date
                        except ValueError as e:
                            current_app.logger.error('Failed to parse due date. Error: %s', str(e))
                            return jsonify({"message": "Invalid due date format"}), 400
                    
                    todo.tags = tags
            
            db.session.commit()
            
            # 物理ファイルの削除（オプション）
            if old_image_path:
                try:
                    file_path = os.path.join(current_app.root_path, '..', old_image_path.lstrip('/'))
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        current_app.logger.info('Image file deleted: %s', file_path)
                except Exception as e:
                    current_app.logger.error('Failed to delete image file: %s. Error: %s', file_path, str(e))
            
            current_app.logger.info('Image deleted for task: %s. Session: %s', todo.task, session)
            return jsonify({"message": "Image deleted successfully"}), 200
        except Exception as e:
            current_app.logger.error('Failed to delete image. Error: %s', str(e))
            db.session.rollback()
            return jsonify({"message": "画像の削除に失敗しました"}), 500
    else:
        current_app.logger.error('Error: Task not found or unauthorized access. Session: %s', session)
        return jsonify({"message": "Task not found or unauthorized access"}), 404
