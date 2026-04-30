import os
import tempfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK

from .. import test_module

log = test_module.config.get_logger()
model = test_module.model

Crud = test_module.crud.Crud
build_app = test_module.api.build_app
get_engine = test_module.engine.get_engine


@pytest.fixture(scope="module")
def client():
    tmp_dir = tempfile.mkdtemp()
    test_db = f"{tmp_dir}/test.db"
    log.debug(f"test-db: {test_db}")
    connection_string = f"sqlite:///{os.path.abspath(test_db)}"
    log.debug(f"connection_string: {connection_string}")
    engine: Engine = create_engine(connection_string)
    model.Base.metadata.create_all(engine)
    session = Session(engine)
    entity_01 = model.Entity(id=1, name="Entity_01")
    entity_02 = model.Entity(id=2, name="Entity_02")
    session.add_all([entity_01, entity_02])
    session.commit()
    crud = Crud(engine)
    log.debug(f"Crud Entities: {crud.get_entities()}")
    app: FastAPI = build_app(crud)
    client = TestClient(app)
    yield client
    os.remove(test_db)
    os.removedirs(tmp_dir)


@pytest.mark.asyncio
async def test_entity_get(client: TestClient):
    response = client.get(f"/entity/")
    assert response.status_code == HTTP_200_OK
    data: list[test_module.schema.EntityFull] = list(
        response.json()  # pyright: ignore[reportAny]
    )
    assert data
    assert len(data) == 2
    assert str(data[0]) == "{'name': 'Entity_01', 'id': 1}"
