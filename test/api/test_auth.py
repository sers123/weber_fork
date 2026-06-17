import os
import tempfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from .. import test_module

log = test_module.config.get_logger()
model = test_module.model
schema = test_module.schema

Crud = test_module.crud.Crud
build_app = test_module.api.build_app

@pytest.fixture(scope="module")
def setup_test_env():
    tmp_dir = tempfile.mkdtemp()
    test_db = f"{tmp_dir}/test_auth.db"
    connection_string = f"sqlite:///{os.path.abspath(test_db)}"
    engine: Engine = create_engine(connection_string)
    model.Base.metadata.create_all(engine)

    crud = Crud(engine)
    app: FastAPI = build_app(crud)
    client = TestClient(app)

    # Create a user to test auth
    new_user = schema.UserBase(
        user_name="testuser",
        name="Test User",
        password_hash="plainpassword123"
    )
    created_user = crud.create_user(new_user)

    yield client, crud, created_user

    os.remove(test_db)
    os.removedirs(tmp_dir)

def test_password_hashing(setup_test_env):
    client, crud, created_user = setup_test_env
    # Retrieve user from DB and check the password_hash is not the plaintext
    users = crud.get_users(schema.UserFilter(user_name="testuser"))
    assert len(users) == 1
    db_user = users[0]

    assert db_user.password_hash != "plainpassword123"
    assert db_user.password_hash.startswith("$2")  # bcrypt hashes start with $2b$ or $2a$

    # Verify using auth utils directly
    from BACKEND_NAME_PLACEHOLDER.utils._auth import verify_password
    assert verify_password("plainpassword123", db_user.password_hash)

def test_login_success(setup_test_env):
    client, crud, created_user = setup_test_env
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "plainpassword123"}
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure(setup_test_env):
    client, crud, created_user = setup_test_env
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == "Incorrect username or password"
 