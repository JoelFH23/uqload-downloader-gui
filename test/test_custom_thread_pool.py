import time
from PyQt5.QtCore import QRunnable
from uqload_dl_gui.customThreadPool import CustomThreadPool


def test_default_values() -> None:
    class Task(QRunnable):
        def run(self) -> None:
            time.sleep(0.2)

    thread_pool = CustomThreadPool()
    assert thread_pool.maxThreadCount() == 2

    thread_pool = CustomThreadPool(5)

    for _ in range(10):
        task = Task()
        thread_pool.submit_task(task)

    assert thread_pool.maxThreadCount() == 5
    assert thread_pool.activeThreadCount() == 5

    thread_pool.waitForDone(1000)

    assert thread_pool.activeThreadCount() == 0
