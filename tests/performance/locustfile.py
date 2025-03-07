from locust import HttpUser, task, between
import json
import random

class TodoUser(HttpUser):
    """
    Todoアプリケーションのパフォーマンステスト用ユーザークラス
    様々なユーザー行動をシミュレートします
    """
    # テスト対象のホスト
    host = "https://todolist-sample.com"
    # リクエスト間の待機時間（1〜3秒）
    wait_time = between(1, 3)
    
    def on_start(self):
        """ユーザーセッション開始時の処理（ログイン）"""
        # ランダムなユーザー名を生成（負荷テスト時に複数ユーザーをシミュレート）
        self.username = f"loadtest_user_{random.randint(1, 1000)}"
        self.email = f"{self.username}@example.com"
        self.password = "password123"
        
        # 新規ユーザー登録
        self.register()
        # ログイン
        self.login()
        # テスト用のタスクをいくつか作成
        self.create_initial_tasks()
    
    def register(self):
        """ユーザー登録"""
        response = self.client.post("/register", json={
            "username": self.username,
            "email": self.email,
            "password": self.password
        })
        if response.status_code != 201:
            print(f"Registration failed: {response.text}")
    
    def login(self):
        """ログイン"""
        response = self.client.post("/login", json={
            "identifier": self.email,
            "password": self.password
        })
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
    
    def create_initial_tasks(self):
        """初期タスクの作成"""
        self.tasks_created = []
        
        # 5つのタスクを作成
        for i in range(5):
            priority = random.randint(1, 3)
            tags = random.choice(["work", "personal", "urgent", "later"])
            
            response = self.client.post("/todos", json={
                "task": f"Performance Test Task {i}",
                "priority": priority,
                "tags": tags
            })
            
            if response.status_code == 201:
                task_data = response.json()
                self.tasks_created.append(task_data["id"])
    
    @task(3)
    def view_todos(self):
        """タスク一覧の表示（高頻度）"""
        self.client.get("/todos")
    
    @task(2)
    def search_todos(self):
        """タスクの検索（中頻度）"""
        search_terms = ["Test", "Task", "Performance", "1", "2"]
        term = random.choice(search_terms)
        self.client.get(f"/todos?search={term}")
    
    @task(1)
    def add_todo(self):
        """タスクの追加（低頻度）"""
        priority = random.randint(1, 3)
        tags = random.choice(["work", "personal", "urgent", "later"])
        
        response = self.client.post("/todos", json={
            "task": f"New Performance Task {random.randint(1000, 9999)}",
            "priority": priority,
            "tags": tags,
            "due_date": "2025-12-31" if random.choice([True, False]) else None
        })
        
        if response.status_code == 201:
            task_data = response.json()
            self.tasks_created.append(task_data["id"])
    
    @task(1)
    def edit_todo(self):
        """タスクの編集（低頻度）"""
        if not self.tasks_created:
            return
            
        task_id = random.choice(self.tasks_created)
        self.client.put(f"/todos/{task_id}", json={
            "task": f"Updated Task {random.randint(1000, 9999)}",
            "priority": random.randint(1, 3)
        })
    
    @task(1)
    def delete_todo(self):
        """タスクの削除（低頻度）"""
        if not self.tasks_created:
            return
            
        task_id = random.choice(self.tasks_created)
        response = self.client.delete(f"/todos/{task_id}")
        
        if response.status_code == 204:
            self.tasks_created.remove(task_id)

class AdminUser(HttpUser):
    """
    管理者ユーザーをシミュレート
    より多くのデータを扱う操作を実行
    """
    host = "http://localhost:80"
    wait_time = between(2, 5)
    
    def on_start(self):
        """管理者ユーザーのセッション開始"""
        self.username = "admin_user"
        self.email = "admin@example.com"
        self.password = "admin123"
        
        # 管理者ユーザー登録
        self.register()
        # ログイン
        self.login()
        # 多数のタスクを作成
        self.create_bulk_tasks()
    
    def register(self):
        """管理者ユーザー登録"""
        response = self.client.post("/register", json={
            "username": self.username,
            "email": self.email,
            "password": self.password
        })
    
    def login(self):
        """ログイン"""
        response = self.client.post("/login", json={
            "identifier": self.email,
            "password": self.password
        })
    
    def create_bulk_tasks(self):
        """大量のタスクを作成"""
        self.tasks_created = []
        
        # 20個のタスクを作成
        for i in range(20):
            response = self.client.post("/todos", json={
                "task": f"Admin Task {i}",
                "priority": random.randint(1, 3),
                "tags": f"tag{i},admin,bulk"
            })
            
            if response.status_code == 201:
                task_data = response.json()
                self.tasks_created.append(task_data["id"])
    
    @task(5)
    def get_all_todos(self):
        """全タスク取得（高負荷操作）"""
        self.client.get("/todos")
    
    @task(2)
    def complex_search(self):
        """複雑な検索クエリ"""
        search_terms = ["Admin", "Task", "bulk", "tag"]
        term = random.choice(search_terms)
        self.client.get(f"/todos?search={term}")
    
    @task(1)
    def bulk_operations(self):
        """一括操作（編集）"""
        if not self.tasks_created or len(self.tasks_created) < 5:
            return
            
        # ランダムに5つのタスクを選んで編集
        for _ in range(5):
            task_id = random.choice(self.tasks_created)
            self.client.put(f"/todos/{task_id}", json={
                "task": f"Updated Admin Task {random.randint(1000, 9999)}",
                "priority": random.randint(1, 3),
                "tags": f"updated,admin,{random.randint(1, 100)}"
            })
