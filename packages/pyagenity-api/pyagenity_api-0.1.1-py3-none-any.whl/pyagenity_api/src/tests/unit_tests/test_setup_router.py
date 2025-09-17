from fastapi import FastAPI
from fastapi.testclient import TestClient

from pyagenity_api.src.app.core.config.setup_middleware import setup_middleware
from pyagenity_api.src.app.routers.setup_router import init_routes


HTTP_NOT_FOUND = 404
HTTP_OK = 200


def test_init_routes_includes_ping_only():
    app = FastAPI()
    setup_middleware(app)
    init_routes(app)
    client = TestClient(app)

    r = client.get("/v1/ping")
    assert r.status_code == HTTP_OK
    assert r.json()["data"] == "pong"

    # Graph and checkpointer routers are present but actual endpoints may be complex.
    # Just verify that non-existent path returns 404 to execute include_router lines.
    r2 = client.get("/v1/non-existent")
    assert r2.status_code == HTTP_NOT_FOUND
