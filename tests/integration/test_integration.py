import unittest
from app import create_app, db
from app.models import User, Todo
from werkzeug.security import generate_password_hash
import json

class IntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        with self.app.app_context():
            db.create_all()
            # テストユーザーの作成
            password_hash = generate_password_hash('password')
            user = User(username='testuser', email='test@example.com', password=password_hash)
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_todo_workflow(self):
        """タスクの追加から削除までの一連の流れをテスト"""
        # ログイン
        login_response = self.client.post('/login', json={
            'identifier': 'test@example.com',
            'password': 'password'
        })
        self.assertEqual(login_response.status_code, 200)
        
        # タスク追加
        add_response = self.client.post('/todos', json={
            'task': 'Integration Test Task',
            'priority': 2,
            'due_date': '2025-12-31',
            'tags': 'integration,test'
        })
        self.assertEqual(add_response.status_code, 201)
        task_data = json.loads(add_response.data)
        task_id = task_data['id']
        
        # タスク取得
        get_response = self.client.get('/todos')
        self.assertEqual(get_response.status_code, 200)
        tasks = json.loads(get_response.data)
        self.assertTrue(any(task['id'] == task_id for task in tasks))
        
        # タスク編集
        edit_response = self.client.put(f'/todos/{task_id}', json={
            'task': 'Updated Integration Task',
            'priority': 3
        })
        self.assertEqual(edit_response.status_code, 200)
        updated_task = json.loads(edit_response.data)
        self.assertEqual(updated_task['task'], 'Updated Integration Task')
        self.assertEqual(updated_task['priority'], 3)
        
        # タスク削除
        delete_response = self.client.delete(f'/todos/{task_id}')
        self.assertEqual(delete_response.status_code, 204)
        
        # 削除確認
        get_after_delete = self.client.get('/todos')
        tasks_after_delete = json.loads(get_after_delete.data)
        self.assertFalse(any(task['id'] == task_id for task in tasks_after_delete))

    def test_authentication_flow(self):
        """認証フローのテスト（登録→ログイン→ログアウト）"""
        # 新規ユーザー登録
        register_response = self.client.post('/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword'
        })
        self.assertEqual(register_response.status_code, 201)
        
        # ログアウト
        logout_response = self.client.post('/logout')
        self.assertEqual(logout_response.status_code, 200)
        
        # 再ログイン
        login_response = self.client.post('/login', json={
            'identifier': 'new@example.com',
            'password': 'newpassword'
        })
        self.assertEqual(login_response.status_code, 200)
        
        # ログイン後のタスク作成
        add_response = self.client.post('/todos', json={
            'task': 'Task after re-login'
        })
        self.assertEqual(add_response.status_code, 201)

    def test_error_handling(self):
        """エラー処理のテスト"""
        # ログイン
        self.client.post('/login', json={
            'identifier': 'test@example.com',
            'password': 'password'
        })
        
        # 空のタスク（エラーになるはず）
        empty_task_response = self.client.post('/todos', json={
            'task': ''
        })
        self.assertEqual(empty_task_response.status_code, 400)
        
        # 無効な日付形式
        invalid_date_response = self.client.post('/todos', json={
            'task': 'Task with invalid date',
            'due_date': 'not-a-date'
        })
        self.assertEqual(invalid_date_response.status_code, 400)
        
        # 存在しないタスクへのアクセス
        invalid_id_response = self.client.get('/todos/9999')
        self.assertEqual(invalid_id_response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
