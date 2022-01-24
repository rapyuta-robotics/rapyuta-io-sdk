# encoding: utf-8
from __future__ import absolute_import
from rapyuta_io import Client

AUTH_TOKEN = 'test_auth_token'
PROJECT = 'test_project'
headers = {'project': PROJECT, 'Authorization': 'Bearer ' + AUTH_TOKEN}
HOST = 'https://gacatalog.apps.okd4v2.prod.rapyuta.io'


def get_client():
    auth_token = AUTH_TOKEN
    project = PROJECT
    client = Client(auth_token, project)
    return client


def remove_auth_token(obj):
    delattr(obj, '_host')
    delattr(obj, '_auth_token')
    delattr(obj, '_project')


def add_auth_token(obj):
    setattr(obj, '_host', HOST)
    setattr(obj, '_auth_token', 'Bearer ' + AUTH_TOKEN)
    setattr(obj, '_project', PROJECT)
