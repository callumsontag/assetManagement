import os
import pytest
from app import app


@pytest.fixture()
def client():
    app.config['TESTING'] = True
    app.secret_key = '12345'
    with app.test_client() as client:
        return client


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_request_example(client):
    response = client.get("/home")
    assert b"<title>Home</title>" in response.data


def test_home_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    # Set the Testing configuration prior to creating the Flask application

    # Create a test client using the Flask application configured for testing

    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the" in response.data
    assert b"Flask User Management Example!" in response.data
    assert b"Need an account?" in response.data
    assert b"Existing user?" in response.data
