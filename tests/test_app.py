import unittest
from app import create_app, db
from app.models import User, Todo
from werkzeug.security import generate_password_hash

class BasicTests(unittest.TestCase):

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
            password_hash = generate_password_hash('password')
            user = User(username='testuser', email='test@example.com', password=password_hash)
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        response = self.client.post('/login', json={
            'identifier': 'test@example.com',
            'password': 'password'
        })
        print("Login Response Data:", response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)

    def test_index_page(self):
        self.login()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)  # ログインが成功したことを確認

    def test_register(self):
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@example.com')

    def test_add_todo(self):
        self.login()
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            todo = Todo(task='Test Task', user_id=user.id)
            db.session.add(todo)
            db.session.commit()

            todo = Todo.query.filter_by(task='Test Task').first()
            self.assertIsNotNone(todo)
            self.assertEqual(todo.task, 'Test Task')

    def test_edit_todo(self):
        self.login()
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            todo = Todo(task='Old Task', user_id=user.id)
            db.session.add(todo)
            db.session.commit()

            response = self.client.put(f'/todos/{todo.id}', json={'task': 'Updated Task'})
            self.assertEqual(response.status_code, 200)

            updated_todo = db.session.get(Todo, todo.id)
            self.assertEqual(updated_todo.task, 'Updated Task')

    def test_delete_todo(self):
        self.login()
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            todo = Todo(task='Task to be deleted', user_id=user.id)
            db.session.add(todo)
            db.session.commit()

            response = self.client.delete(f'/todos/{todo.id}')
            self.assertEqual(response.status_code, 204)

            deleted_todo = db.session.get(Todo, todo.id)
            self.assertIsNone(deleted_todo)

    def test_login(self):
        self.login()
        response = self.client.post('/login', json={
            'identifier': 'test@example.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('User logged in successfully', response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()
