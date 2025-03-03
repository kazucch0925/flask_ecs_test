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

// トースト通知を表示する関数
function showToast(message, type) {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        // コンテナがなければ作成
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        document.body.appendChild(toastContainer);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type || 'info'}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    
    // アニメーションのためにタイミングをずらす
    setTimeout(() => toast.classList.add('show'), 10);

    // 5秒後にトーストを削除
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toastContainer.contains(toast)) {
                toastContainer.removeChild(toast);
            }
        }, 500);
    }, 5000);
}

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

// 画像プレビュー機能
document.getElementById('image').addEventListener('change', function(event) {
    const imagePreview = document.getElementById('imagePreview');
    imagePreview.innerHTML = '';
    
    if (this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'preview-image';
            imagePreview.appendChild(img);
        };
        reader.readAsDataURL(this.files[0]);
    }
});

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
                
                // 画像表示用のHTML
                let imageHtml = 'なし';
                if (todo.image_path) {
                    imageHtml = `<img src="${todo.image_path}" alt="タスク画像" class="task-image" onclick="showFullImage('${todo.image_path}')">`;
                }

                row.innerHTML = `
                    <td><input type="checkbox" class="task-select-checkbox" data-task-id="${todo.id}"></td>
                    <td>${todo.task}</td>
                    <td>${formattedDate}</td>
                    <td>${priorityText}</td>
                    <td>${todo.due_date ? new Date(todo.due_date).toLocaleDateString('ja-JP') : 'なし'}</td>
                    <td>${todo.tags !== undefined ? todo.tags : 'なし'}</td>
                    <td class="image-cell">${imageHtml}</td>
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
        })
        .finally(() => {
            updateCheckboxes();
        });
}

// 画像を拡大表示する関数
function showFullImage(imagePath) {
    // モーダルを作成
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    
    // 画像要素を作成
    const img = document.createElement('img');
    img.src = imagePath;
    img.className = 'full-image';
    
    // 閉じるボタンを作成
    const closeBtn = document.createElement('span');
    closeBtn.className = 'close-image-modal';
    closeBtn.innerHTML = '&times;';
    closeBtn.onclick = function() {
        document.body.removeChild(modal);
    };
    
    // モーダルに要素を追加
    modal.appendChild(closeBtn);
    modal.appendChild(img);
    
    // モーダルをクリックしたら閉じる
    modal.onclick = function(event) {
        if (event.target === modal) {
            document.body.removeChild(modal);
        }
    };
    
    // モーダルをbodyに追加
    document.body.appendChild(modal);
}

function addTask() {
    const task = document.getElementById('task').value;
    const priority = document.getElementById('priority').value;
    const due_date = document.getElementById('due_date').value;
    const tags = document.getElementById('tags').value;
    const imageFile = document.getElementById('image').files[0];
    
    // 画像ファイルがある場合はFormDataを使用
    if (imageFile) {
        const formData = new FormData();
        formData.append('task', task);
        formData.append('priority', priority);
        if (due_date) formData.append('due_date', due_date);
        if (tags) formData.append('tags', tags);
        formData.append('image', imageFile);
        
        fetch('/todos', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                document.getElementById('addTaskModal').style.display = 'none';
                document.getElementById('addTaskForm').reset();
                document.getElementById('imagePreview').innerHTML = '';
                fetchTodos();
                showToast('タスクが正常に追加されました。', 'success');
            } else {
                return response.text().then(text => {
                    console.log('Response text:', text);
                    throw new Error('Failed to add task');
                });
            }
        })
        .catch(error => {
            console.error('Error adding task:', error);
            showToast(`追加に失敗しました: ${error.message}`, 'error');
        })
        .finally(() => {
            updateCheckboxes();
        });
    } else {
        // 画像がない場合は従来のJSON形式で送信
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
                document.getElementById('addTaskForm').reset();
                fetchTodos();
                showToast('タスクが正常に追加されました。', 'success');
            } else {
                return response.text().then(text => {
                    console.log('Response text:', text);
                    throw new Error('Failed to add task');
                });
            }
        })
        .catch(error => {
            console.error('Error adding task:', error);
            showToast(`追加に失敗しました: ${error.message}`, 'error');
            const errorMessageElement = document.querySelector('.error-message');
            if (errorMessageElement) {
                errorMessageElement.textContent = `追加に失敗しました: ${error.message}`;
                errorMessageElement.style.display = 'block';
            }
        })
        .finally(() => {
            updateCheckboxes();
        });
    }
}

function deleteTask(id) {
    fetch(`/todos/${id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            fetchTodos();
	    showToast('タスクが正常に削除されました。', 'success');
        } else {
            return response.text().then(text => {
                console.log('Response text:', text);
                throw new Error('Failed to delete task');
            });
        }
    })
    .catch(error => {
        console.error('Error deleting task:', error);
	showToast(`削除に失敗しました: ${error.message}`, 'error');
        const errorMessageElement = document.querySelector('.error-message');
        if (errorMessageElement) {
            errorMessageElement.textContent = `削除に失敗しました: ${error.message}`;
            errorMessageElement.style.display = 'block';
        }
    })
    .finally(() => {
        updateCheckboxes();
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
        showToast('削除するタスクが選択されていません。', 'warning');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    fetchTodos();

    // 削除ボタンのイベントリスナーを追加
    const deleteButton = document.getElementById('deleteSelectedTasks');
    deleteButton.onclick = deleteSelectedTasks;
    
    // 検索機能のイベントリスナーを追加
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('searchInput');
    
    searchButton.addEventListener('click', function() {
        const searchQuery = searchInput.value.trim();
        fetchTodos(searchQuery);
    });
    
    // Enterキーでも検索できるようにする
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const searchQuery = searchInput.value.trim();
            fetchTodos(searchQuery);
        }
    });
});
