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

// タスクが一つもない場合はチェックボックスを非活性
function updateCheckboxes() {
    const tasks = document.querySelectorAll('#todoList tr');
    const selectAllCheckbox = document.getElementById('selectAll');
    if (tasks.length === 0) {
        selectAllCheckbox.disabled = true;
    } else {
        selectAllCheckbox.disabled = false;
    }
}

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

            // 全選択機能の設定
            const selectAllCheckbox = document.getElementById('selectAll');
            selectAllCheckbox.checked = false; // 初期状態で未選択
            selectAllCheckbox.addEventListener('change', function() {
                const checkboxes = document.querySelectorAll('.task-select-checkbox');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = selectAllCheckbox.checked;
                });
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
	updateCheckboxes();
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
    updateCheckboxes();
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
    updateCheckboxes();
    .catch(error => {
        console.error('Error deleting task:', error);
        const errorMessageElement = document.querySelector('.error-message');
        if (errorMessageElement) {
            errorMessageElement.textContent = `削除に失敗しました: ${error.message}`;
            errorMessageElement.style.display = 'block';
        }
    });
}

// 選択したタスクを削除する関数
function deleteSelectedTasks() {
    const selectedTasks = document.querySelectorAll('.task-select-checkbox:checked');
    const idsToDelete = Array.from(selectedTasks).map(checkbox => checkbox.getAttribute('data-task-id'));

    if (idsToDelete.length > 0) {
        const confirmation = confirm(`選択した${idsToDelete.length}件のタスクを削除してよろしいですか？`);
        if (confirmation) {
            idsToDelete.forEach(id => {
                deleteTask(id);
            });
        }
    } else {
        alert('削除するタスクが選択されていません。');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    fetchTodos();

    // 削除ボタンのイベントリスナーを追加
    const deleteButton = document.getElementById('deleteSelectedTasks');
    deleteButton.onclick = deleteSelectedTasks;
});
