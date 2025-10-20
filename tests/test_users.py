import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Base

TEST_DB_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)

@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

def test_put_user(client):
    r = client.post("/api/users", json={
        "name": "John",
        "email": "john@example.com",
        "age": 25,
        "student_id": "S1234567"
    })
    u = r.json()
    r2 = client.put(f"/api/users/{u['id']}", json={
        "name": "Johnny",
        "email": "johnny@example.com",
        "age": 26,
        "student_id": "S1234567"
    })
    assert r2.status_code == 200
    assert r2.json()["name"] == "Johnny"

def test_patch_user(client):
    r = client.post("/api/users", json={
        "name": "Alice",
        "email": "alice@example.com",
        "age": 22,
        "student_id": "S7654321"
    })
    u = r.json()
    r2 = client.patch(f"/api/users/{u['id']}", json={"age": 30})
    assert r2.status_code == 200
    assert r2.json()["age"] == 30

def test_put_project(client):
    user = client.post("/api/users", json={
        "name": "Bob",
        "email": "bob@example.com",
        "age": 20,
        "student_id": "S1111111"
    }).json()
    p = client.post("/api/projects", json={
        "name": "Proj1",
        "description": "Desc1",
        "owner_id": user["id"]
    }).json()
    r = client.put(f"/api/projects/{p['id']}", json={
        "name": "Proj2",
        "description": "Updated",
        "owner_id": user["id"]
    })
    assert r.status_code == 200
    assert r.json()["name"] == "Proj2"

def test_patch_project(client):
    user = client.post("/api/users", json={
        "name": "Eve",
        "email": "eve@example.com",
        "age": 24,
        "student_id": "S2222222"
    }).json()
    p = client.post("/api/projects", json={
        "name": "ProjA",
        "description": "Initial",
        "owner_id": user["id"]
    }).json()
    r = client.patch(f"/api/projects/{p['id']}", json={"description": "Changed"})
    assert r.status_code == 200
    assert r.json()["description"] == "Changed"
