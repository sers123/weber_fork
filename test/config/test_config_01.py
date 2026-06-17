import os

from .. import test_module

Config = test_module.config.Config


def test_config_load_file_01():
    test_directory = os.path.dirname(__file__)
    test_config_file_name = os.path.join(test_directory, "test_config.json")
    config = Config.get_instance(test_config_file_name)
    assert "testconnectionstring" == config.connection_string


def test_config_load_env_01(monkeypatch):
    monkeypatch.setenv("DB_CONNECTION_STRING", "env-connection-string")
    monkeypatch.setenv("ROOT_USER_NAME", "root-user")
    monkeypatch.setenv("ROOT_USER_PASSWORD", "root-password")

    config = Config.get_instance("does-not-exist.json")

    assert "env-connection-string" == config.connection_string
    assert "root-user" == config.root_user_name
    assert "root-password" == config.root_user_password
