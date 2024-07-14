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
            data.forEach(todo => {
                console.log(todo); // デバッグ用
                const listItem = document.createElement('li');
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

                listItem.textContent = `${todo.task} - ${formattedDate} - 優先度: ${todo.priority !== undefined ? todo.priority : 'なし'} - 期限: ${todo.due_date ? new Date(todo.due_date).toLocaleDateString('ja-JP') : 'なし'} - タグ: ${todo.tags !== undefined ? todo.tags : 'なし'}`;

                const deleteLink = document.createElement('a');
                deleteLink.href = `#`;
                deleteLink.textContent = '削除';
                deleteLink.onclick = function(event) {
                    event.preventDefault();
                    deleteTask(todo.id);
                };
                listItem.appendChild(deleteLink);

                const editLink = document.createElement('a');
                editLink.href = `/todos/${todo.id}`;
                editLink.textContent = '編集';
                listItem.appendChild(editLink);

                todoListElement.appendChild(listItem);
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
            errorMessageElement.style.display = 'block';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    fetchTodos();
});
