from heros import RemoteHERO
from boss.starter import run
import multiprocessing
import time


def test_autostart(default_starter_env, cleanup):
    boss_processes = [
        multiprocessing.Process(
            target=run,
            args=(
                [
                    "--no-autostart",
                    "-e",
                    "BOSS1",
                    "--expose",
                    "--log=debug",
                    "--name=test_boss",
                ],
            ),
        ),
        multiprocessing.Process(
            target=run,
            args=(
                [
                    "-e",
                    "BOSS2",
                    "--expose",
                    "--log=debug",
                    "--name=test_boss2",
                ],
            ),
        ),
    ]
    cleanup["boss"] = boss_processes
    for boss_process in boss_processes:
        boss_process.start()
    time.sleep(1)
    boss = RemoteHERO("test_boss")
    cleanup["heros"].append(boss)
    assert boss.status()["test_dev"]["status"] == "stopped"

    boss2 = RemoteHERO("test_boss2")
    cleanup["heros"].append(boss2)
    assert boss2.status()["test_dev2"]["status"] == "running"
