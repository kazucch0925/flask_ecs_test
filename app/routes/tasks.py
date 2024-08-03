from flask import Blueprint, request, jsonify, session, current_app, render_template
from datetime import datetime, date
import pytz
from app.models import Todo
from app import db

tasks_bp = Blueprint('tasks', __name__, template_folder='../../templates')

def get_user_id_from_session():
    if 'logged_in' in session and session['logged_in']:
        return session.get('user_id')
    return None

def get_todo_response(todo):
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    created_at_tokyo = todo.created_at.astimezone(tokyo_tz)
    response = {
        "id": todo.id,
        "task": todo.task,
        "created_at": created_at_tokyo.isoformat(),
        "priority": todo.priority,
        "due_date": todo.due_date.isoformat() if todo.due_date else None,
        "tags": todo.tags
    }
    current_app.logger.debug(f'Todo priority: {todo.priority}')
    current_app.logger.debug(f'Todo due_date: {todo.due_date}')
    current_app.logger.debug(f'Todo tags: {todo.tags}')
    current_app.logger.debug(f'Generated response: {response}')
    return response

# タスクの追加ルート
@tasks_bp.route('/todos', methods=['POST'])
def add_todo():
    current_app.logger.info('Task add route called.')
    user_id = get_user_id_from_session()
    current_app.logger.debug(f'User ID from session: {user_id}')
    if user_id is None:
        current_app.logger.error('Error: user_id not found in session. Session: %s', session)
        return jsonify({"message": "user_id not found in session"}), 401

    try:
        data = request.get_json() or {}
        current_app.logger.debug(f'Received data: {data}')
    except Exception as e:
        current_app.logger.error('Failed to parse JSON. Error: %s', str(e))
        return jsonify({"message": "Invalid JSON format"}), 400

    task = data.get('task')
    priority = data.get('priority', 1)
    due_date = data.get('due_date')
    tags = data.get('tags')

    current_app.logger.debug(f'Task: {task}, Priority: {priority}, Due date: {due_date}, Tags: {tags}')

    if not task:
        current_app.logger.warning('Failed to add task. Task was empty. Session: %s', session)
        return jsonify({"message": "タスクを入力してください"}), 400

    tokyo_tz = pytz.timezone('Asia/Tokyo')
    now = datetime.now(tokyo_tz)

    try:
        if due_date:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        new_todo = Todo(task=task, created_at=now, user_id=user_id, priority=priority, due_date=due_date, tags=tags)
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
@tasks_bp.route('/todos/<int:id>', methods=['PUT'])
def edit_todo(id):
    user_id = get_user_id_from_session()
    if user_id is None:
        current_app.logger.error('Error: user_id not found in session. Session: %s', session)
        return jsonify({"message": "user_id not found in session"}), 401

    todo = db.session.get(Todo, id)
    if todo and todo.user_id == user_id:
        try:
            data = request.get_json() or {}
            task = data.get('task')
            priority = data.get('priority', todo.priority)
            due_date = data.get('due_date', todo.due_date)
            tags = data.get('tags', todo.tags)

            current_app.logger.debug(f"Received data: {data}")
            current_app.logger.debug(f"Task: {task}, Priority: {priority}, Due date: {due_date}, Tags: {tags}")

            if not task:
                current_app.logger.warning('Failed to edit task. Task was empty. Session: %s', session)
                return jsonify({"message": "タスクを入力してください"}), 400

            todo.task = task
            todo.priority = priority
            
            if due_date:
                try:
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

# タスクの完了状態を更新するルート
@tasks_bp.route('/todos/<int:id>/status', methods=['PATCH'])
def update_task_status(id):
    user_id = get_user_id_from_session()
    if user_id is None:
        current_app.logger.error('Error: user_id not found in session. Session: %s', session)
        return jsonify({"message": "user_id not found in session"}), 401

    task = Todo.query.filter_by(id=id, user_id=user_id).first()
    if not task:
        return jsonify({"message": "Task not found or unauthorized access"}), 404

    try:
        data = request.get_json()
        is_complete = data.get('isComplete')
        if is_complete is not None:
            task.is_complete = is_complete
            db.session.commit()
            return jsonify({"message": "Task status updated successfully"}), 200
        else:
            return jsonify({"message": "Invalid data provided"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update task status"}), 500
