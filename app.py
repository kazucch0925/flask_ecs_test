from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

todo_list = []
next_id = 1

@app.route('/')
def index():
    return render_template('index.html', todo_list=todo_list)

@app.route('/add', methods=['POST'])
def add():
    global next_id
    task = request.form['task']
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    todo_list.append({'id': next_id, 'task': task, 'created_at': created_at})
    next_id += 1
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    global todo_list
    todo = next((todo for todo in todo_list if todo['id'] == id), None)
    if todo:
        todo_list.remove(todo)
    else:
        return "Error: Task not found"
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    todo = next((todo for todo in todo_list if todo['id'] == id), None)
    if todo:
        if request.method == 'POST':
            task = request.form['task']
            todo['task'] = task
            return redirect(url_for('index'))
        else:
            return render_template('edit.html', todo=todo)
    else:
        return "Error: Task not found"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
