from app import db, app
import pytest


class TestApp:
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        app.secret_key = '12345'
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.session.remove()

    def test_home_route(self, client):
        # Testing the home route
        response = client.get('/home')
        assert response.status_code == 200
        assert b"Asset Management System" in response.data

    def test_register_route(self, client):
        # Testing the register route
        response = client.get('/register')
        assert response.status_code == 200
        assert b"Register" in response.data
        assert b"Already have an account? " in response.data

    def test_login_route(self, client):
        # Testing the login route
        response = client.get('/login')
        assert response.status_code == 200
        assert b"Login" in response.data
        assert b"Don't have an account? " in response.data

    def test_logout_redirect(self, client):
        response = client.get('logout', follow_redirects=True)
        # check that the logout path takes users back to login
        assert response.status_code == 200
        assert b"Login" in response.data
        assert b"Don't have an account? " in response.data
