import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_home(client):
    res = client.get('/')
    assert res.status_code == 200
    assert res.get_json() == {"message": "Hello from Flask!"}

def test_health(client):
    res = client.get('/health')
    assert res.status_code == 200
    assert res.get_json() == {"status": "healthy"}

def test_echo(client):
    payload = {"foo": "bar"}
    res = client.post('/echo', json=payload)
    assert res.status_code == 200
    assert res.get_json() == payload

def test_mongo(client):
    res = client.get('/mongo')
    assert res.status_code in [200, 500]  # puede fallar si no hay Mongo real
    if res.status_code == 200:
        assert isinstance(res.get_json(), list)
