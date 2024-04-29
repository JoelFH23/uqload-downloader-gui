from PyQt5.QtCore import QThreadPool, QMutex


class CustomThreadPool(QThreadPool):
    """
    Custom thread pool with additional functionality for limiting the number of tasks and threads.

    Attributes:
        max_size (int): Maximum number of tasks allowed in the thread pool.
        __current_tasks (int): Number of currently active tasks in the thread pool.
        __mutex (QMutex): Mutex for thread-safe access to shared resources.
    """

    def __init__(self, max_workers: int = 2, max_size: int = 5) -> None:
        """
        Initialize the CustomThreadPool instance.

        Args:
            max_workers (int): Maximum number of worker threads.
            max_size (int): Maximum number of tasks allowed in the thread pool.
        """
        super().__init__()
        self.setMaxThreadCount(max_workers)
        self.setStackSize(max_size)
        self.__current_tasks = 0
        self.__mutex = QMutex()

    @property
    def current_tasks(self) -> int:
        """
        Get the number of currently active tasks in the thread pool.

        Returns:
            int: The number of currently active tasks.
        """
        self.__mutex.lock()
        total = self.__current_tasks
        self.__mutex.unlock()
        return total

    @current_tasks.setter
    def current_tasks(self, value) -> None:
        """
        Set the number of currently active tasks in the thread pool.

        Args:
            value (int): The new value for the number of currently active tasks.
        """
        self.__mutex.lock()
        self.__current_tasks = int(value)
        self.__mutex.unlock()

    def submit_task(self, task) -> None:
        """
        Submit a task to the thread pool if the maximum size has not been reached.

        Args:
            task: The task to be submitted to the thread pool.
        """
        if self.__current_tasks >= self.stackSize():
            return
        self.start(task)
        self.__current_tasks += 1

    def full(self) -> bool:
        """
        Check if the thread pool is full (maximum number of tasks reached).

        Returns:
            bool: True if the thread pool is full, False otherwise.
        """
        self.__mutex.lock()
        is_full = True if self.__current_tasks >= self.stackSize() else False
        self.__mutex.unlock()
        return is_full
