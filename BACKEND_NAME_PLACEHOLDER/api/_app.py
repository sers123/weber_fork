from fastapi import FastAPI

from ..config import get_logger
from ..crud import Crud
from ..engine import get_engine
from ._routes import define_routes

log = get_logger()

_app: FastAPI | None = None
_crud: Crud | None = None


"""
Function to build and initialize the application. This function sets up the CRUD object and FastAPI
instance, and defines the routes if they haven't been defined yet. If environment variable
'CONFIG_FILE' is set, it uses that file for configuration.

Returns:
    The initialized FastAPI application instance.
"""
def build_app(crud: Crud | None = None):

    global _crud
    global _app

    if not _crud:
        if crud:
            log.debug(f"Crud Entities in build_app: {crud.get_entities()}")
            _crud = crud
            log.debug("Existing crud provided.")
        else:
            engine = get_engine()
            _crud = Crud(engine)
            log.debug("Creating new crud")

    global _app

    if not _app:
        log.debug("Creating app")
        _app = FastAPI()
        log.debug(f"Provided crud{crud} used crud{_crud}")
        log.debug(f"Crud Entities in build_app with _crud: {_crud.get_entities()}")
        define_routes(_app, _crud)
    else:
        log.debug("App already created")

    return _app
