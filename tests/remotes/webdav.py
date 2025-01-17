# pylint:disable=abstract-method
import os
from pathlib import Path
from wsgiref.simple_server import make_server

import pytest
from funcy import first
from wsgidav.wsgidav_app import WsgiDAVApp

from dvc.path_info import WebDAVURLInfo
from dvc.utils.fs import makedirs
from tests.utils.httpd import run_server_on_thread

from .base import Base

AUTH = {"user1": {"password": "password1"}}


class Webdav(Base, WebDAVURLInfo):
    @staticmethod
    def get_url(port):  # pylint: disable=arguments-differ
        return f"webdav://localhost:{port}"

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        assert parents
        makedirs(self.path, exist_ok=exist_ok)

    def write_bytes(self, contents):
        Path(self.path).write_bytes(contents)

    def write_text(self, contents, encoding=None, errors=None):
        Path(self.path).write_text(contents, encoding=encoding, errors=errors)


@pytest.fixture
def webdav_server(tmp_path_factory):
    host, port = "localhost", 0
    directory = os.fspath(tmp_path_factory.mktemp("http"))
    dirmap = {"/": directory}

    app = WsgiDAVApp(
        {
            "host": host,
            "port": port,
            "provider_mapping": dirmap,
            "simple_dc": {"user_mapping": {"*": AUTH}},
        }
    )
    server = make_server(host, port, app)
    with run_server_on_thread(server) as httpd:
        yield httpd


@pytest.fixture
def webdav(webdav_server):
    url = Webdav.get_url(webdav_server.server_port)
    ret = Webdav(url)
    user, secrets = first(AUTH.items())
    ret.config = {"url": url, "user": user, **secrets}
    yield ret
