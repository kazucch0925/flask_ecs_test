document.getElementById('logoutButton').onclick = function() {
    fetch('/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "User logged out successfully") {
            window.location.href = data.redirect; // ログインページにリダイレクト
        } else {
            throw new Error(data.message);
        }
    })
    .catch(error => {
        console.error('Error logging out:', error);
        const errorMessageElement = document.querySelector('.error-message');
        if (errorMessageElement) {
            errorMessageElement.textContent = `ログアウトに失敗しました: ${error.message}`;
            errorMessageElement.style.display = 'block';
        }
    });
};

document.getElementById('openModalButton').onclick = function() {
    document.getElementById('addTaskModal').style.display = 'block';
};

document.getElementsByClassName('close')[0].onclick = function() {
    document.getElementById('addTaskModal').style.display = 'none';
};

window.onclick = function(event) {
    if (event.target == document.getElementById('addTaskModal')) {
        document.getElementById('addTaskModal').style.display = 'none';
    }
};

function fetchTodos(search = '') {
    let url = '/todos';
    if (search) {
        url += `?search=${search}`;
    }

    fetch(url)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.text().then(text => {
                    console.log('Response text:', text);
                    throw new Error('Failed to fetch todos');
                });
            }
        })
        .then(data => {
            console.log('Fetched todos:', data);
            const todoListElement = document.getElementById('todoList');
            todoListElement.innerHTML = '';
            const priorityLabels = {1: '低', 2: '中', 3: '高'};
            data.forEach(todo => {
                console.log(todo); // デバッグ用
                const row = document.createElement('tr');
                const date = new Date(todo.created_at);
                const formattedDate = new Intl.DateTimeFormat('ja-JP', {
                    year: 'numeric',
                    month: 'numeric',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: 'numeric',
                    second: 'numeric',
                    timeZone: 'Asia/Tokyo'
                }).format(date);
                const priorityText = priorityLabels[todo.priority] || 'なし';

                row.innerHTML = `
                    <td><input type="checkbox" class="task-select-checkbox" data-task-id="${todo.id}"></td>
                    <td>${todo.task}</td>
                    <td>${formattedDate}</td>
                    <td>${priorityText}</td>
                    <td>${todo.due_date ? new Date(todo.due_date).toLocaleDateString('ja-JP') : 'なし'}</td>
                    <td>${todo.tags !== undefined ? todo.tags : 'なし'}</td>
                    <td class="actions">
                        <a href="#" onclick="deleteTask(${todo.id})">削除</a>
                        <a href="/todos/${todo.id}">編集</a>
                    </td>
                `;
                todoListElement.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching todos:', error);
            const errorMessageElement = document.querySelector('.error-message');
            if (errorMessageElement) {
                errorMessageElement.textContent = `タスクの取得に失敗しました: ${error.message}`;
                errorMessageElement.style.display = 'block';
            }
        });
}

function addTask() {
    const task = document.getElementById('task').value;
    const priority = document.getElementById('priority').value;
    const due_date = document.getElementById('due_date').value;
    const tags = document.getElementById('tags').value;

    fetch('/todos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ task, priority, due_date, tags })
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('addTaskModal').style.display = 'none';
            fetchTodos();
        } else {
            return response.text().then(text => {
                console.log('Response text:', text);
                throw new Error('Failed to add task');
            });
        }
    })
    .catch(error => {
        console.error('Error adding task:', error);
        const errorMessageElement = document.querySelector('.error-message');
        if (errorMessageElement) {
            errorMessageElement.textContent = `追加に失敗しました: ${error.message}`;
            errorMessageElement.style.display = 'block';
        }
    });
}

function deleteTask(id) {
    fetch(`/todos/${id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            fetchTodos();
        } else {
            return response.text().then(text => {
                console.log('Response text:', text);
                throw new Error('Failed to delete task');
            });
        }
    })
    .catch(error => {
        console.error('Error deleting task:', error);
        const errorMessageElement = document.querySelector('.error-message');
        if (errorMessageElement) {
            errorMessageElement.textContent = `削除に失敗しました: ${error.message}`;
            errorMessageElement.style.display 'block';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    fetchTodos();
});

document.getElementById('selectAll').addEventListener('change', function(event) {
    let checkboxes = document.querySelectorAll('.task-select-checkbox');
    for (let checkbox of checkboxes) {
        checkbox.checked = event.target.checked;
    }
});

document.getElementById('deleteSelectedTasks').addEventListener('click', function() {
    let selectedTasks = document.querySelectorAll('.task-select-checkbox:checked');
    let idsToDelete = Array.from(selectedTasks).map(checkbox => checkbox.getAttribute('data-task-id'));
    if (idsToDelete.length > 0) {
        let confirmation = confirm(`選択した${idsToDelete.length}件のタスクを削除してよろしいですか？`);
        if (confirmation) {
            idsToDelete.forEach(id => {
                deleteTask(id);
            });
        }
    }
});

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('task-complete-checkbox')) {
        const taskId = event.target.getAttribute('data-task-id');
        const isComplete = event.target.checked;

        fetch(`/todos/${taskId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ isComplete: isComplete })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Task status updated', data);
            fetchTodos(); // リストを更新
        })
        .catch(error => console.error('Error updating task status:', error));
    }
});
