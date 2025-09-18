import pytest
import os
from unittest import mock
import json
import time


@pytest.fixture()
def default_starter_env():
    boss_config = json.dumps({
        "_id": "test_dev",
           "classname": "boss.dummies.Dummy",
           "arguments": {
           }
       })
    boss_config2 = json.dumps({
        "_id": "test_dev2",
           "classname": "boss.dummies.Dummy",
           "arguments": {
           }
       })
    with mock.patch.dict(os.environ, {"BOSS1": boss_config, "BOSS2": boss_config2}):
        yield

@pytest.fixture()
def cleanup():
    cleanups = {"boss": [], "heros":[]}
    yield cleanups
    for boss_process in cleanups["boss"]:
        boss_process.terminate()
    for boss_process in cleanups["boss"]:
        while boss_process.exitcode is None:
            time.sleep(0.1)
    for hero in cleanups["heros"]:
        hero._destroy_hero()
        hero._session_manager.force_close()
