import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk

import ckanext.saml.helpers as h
from ckanext.saml import config
from ckanext.saml.model.user import User


@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_is_saml_user(user):
    assert not tk.h.saml_is_saml_user(user["name"])

    model.Session.add(User(id=user["id"], name_id="test"))
    model.Session.commit()

    assert tk.h.saml_is_saml_user(user["name"])


@pytest.mark.usefixtures("with_plugins")
def test_login_button_text(ckan_config, monkeypatch, faker):
    assert tk.h.saml_login_button_text() == config.DEFAULT_LOGIN_TEXT

    label = faker.sentence()
    monkeypatch.setitem(ckan_config, config.CONFIG_LOGIN_TEXT, label)
    assert tk.h.saml_login_button_text() == label


@pytest.mark.usefixtures("with_plugins")
def test_folder_path(ckan_config, monkeypatch, faker):
    assert tk.h.saml_folder_path() == config.DEFAULT_FOLDER_PATH

    path = faker.file_path()
    monkeypatch.setitem(ckan_config, config.CONFIG_FOLDER_PATH, path)
    assert tk.h.saml_folder_path() == path


@pytest.mark.usefixtures("with_plugins")
def test_attr_mapper(ckan_config, monkeypatch, faker):
    assert tk.h.saml_attr_mapper() is None


@pytest.mark.usefixtures("with_plugins")
def test_settings(ckan_config, monkeypatch, faker):
    assert tk.h.saml_settings() == {}
