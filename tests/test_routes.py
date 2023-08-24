from flask import url_for, request
from app import db, app, User, Asset
from flask_login import login_user
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

    def test_assets_route(self, client):
        user = User(
            user_id=5, email='testtest@mettle.co.uk', password='test')
        asset = Asset(asset_id=1, name='testasset1',
                      description='test asset description', user_id=5)

        response = client.get("assets/5", follow_redirects=True)
        assert b"Assets" in response.data
        assert response.status_code == 200
        assert b"Assets" in response.data

    # def test_create_assets_route(self, client):

    # def test_edit_assets_route(self, client):

    # def test_delte_assets_route(self, client):
