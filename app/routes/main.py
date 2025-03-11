from flask import Blueprint, render_template, jsonify, session, current_app, redirect, url_for
from app.models import Todo
from datetime import datetime
import pytz

main_bp = Blueprint('main', __name__, template_folder='../../templates')

def get_todo_response(todo):
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    created_at_tokyo = todo.created_at.astimezone(tokyo_tz)
    return {
        "id": todo.id,
        "task": todo.task,
        "created_at": created_at_tokyo.isoformat(),
        "priority": todo.priority,
        "due_date": todo.due_date.isoformat() if todo.due_date else None,
        "tags": todo.tags,
        "image_path": todo.image_path
    }

@main_bp.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        user_id = session.get('user_id')
        if user_id is None:
            current_app.logger.error('Error: user_id not found in session. Session: %s', session)
            return redirect(url_for('auth.logout'))
        current_app.logger.info('Accessed index page. Session: %s', session)
        return render_template('index.html')
    elif 'registered' in session and session['registered']:
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('auth.register'))

# /todosのGETルートはapp/routes/tasks.pyに移動しました
