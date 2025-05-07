
from abc import ABC  # , abstractmethod
import logging
from threading import Lock, Thread
import time

from Modules.module_logger import ModuleLogger


class ModuleThread(ABC, Thread):
    def __init__(self, logger=None, logger_name: str = "", logger_level_stdo: int = logging.DEBUG, logger_level_file: int = logging.DEBUG, logger_file_path: str = "", mode="a", maxBytes=1 * 1024 * 1024, backupCount=5, *args, **kwargs):
        super(ModuleThread, self).__init__(*args, **kwargs)

        # # Log Collection Lock # #
        self.safe_task_lock = Lock()
        self.task_stop_lock = Lock()

        if logger is None:
            if logger_name == "":
                logger_name = self.__class__.__name__

            self.module_logger = ModuleLogger(
                logger_name=logger_name,
                logger_file_path=logger_file_path,
                logger_level_stdo=logger_level_stdo,
                logger_level_file=logger_level_file,
                mode=mode,
                maxBytes=maxBytes,
                backupCount=backupCount
            )
            self.logger = self.module_logger.get_Logger()
        else:
            self.logger = logger

        self.__parameters_template: dict = {}
        self.parameters = self.__parameters_template.copy()

        # Flags
        self._flag_thread_stop = False
        self._flag_task_stop = True

        # Information
        self.is_running = False
        self.is_finished = False

        # Configuration
        self.daemon = True

    def run(self) -> None:
        self.is_running = False
        self.is_finished = False

        while not self.is_Thread_Stopped():
            while not self.is_Task_Stopped():

                self.is_running = True
                self.is_finished = False

                self.before_task_call()
                response = self.task(
                    **self.get_Parameters()
                )
                self.after_task_call()

                self.is_running = False

                if response == 0:
                    self.logger.info("Task Finished Successfully")
                    self.is_finished = True
                else:
                    self.logger.warning("Task Manually Stopped")

                self.stop_Task()
                time.sleep(1)
            time.sleep(1)

    def stop_Thread(self) -> int:
        self._flag_thread_stop = True
        self._flag_task_stop = True
        self.join()
        self.logger.warning("Thread Stopped")
        return 0

    def stop_Task(self) -> int:
        self._flag_task_stop = True
        self.logger.warning("Task Stopped")
        return 0

    def stop_Action_Control(self):
        return self.is_Thread_Stopped() or self.is_Task_Stopped()

    def wait_To_Stop_Once_Task(self) -> int:
        self.logger.warning("Waiting to stop task once...")

        time.sleep(1)  # Wait for the thread to start
        while self.is_Running():
            time.sleep(1)

        self.logger.warning("Task once stopped...")
        return 0

    def wait_To_Stop_Task(self) -> int:
        self.logger.warning("Waiting to stop task fully...")

        time.sleep(1)  # Wait for the thread to start
        while self.is_Running() and self.is_Thread_Started():
            time.sleep(1)

        self.logger.warning("Task fully stopped...")
        return 0

    def is_Running(self) -> bool:
        return self.is_running

    def overwrite_Running_Status(self, status: bool):
        self.is_running = status

    def is_Thread_Stopped(self) -> bool:
        return self._flag_thread_stop

    def is_Finished(self) -> bool:
        return self.is_finished

    def is_Thread_Started(self) -> bool:
        return not self._flag_thread_stop

    def is_Task_Stopped(self) -> bool:
        return self._flag_task_stop

    def overwrite_Task_Stop_Status(self, status: bool):
        self._flag_task_stop = status

    def overwrite_Thread_Stop_Status(self, status: bool):
        self._flag_thread_stop = status

    def get_Parameters(self) -> dict[str, str]:
        return self.parameters.copy()

    def start_Task(self) -> int:
        if self.is_Thread_Stopped():
            self.logger.warning("Thread already stopped. Can NOT do the task!")
            return 1

        self._flag_task_stop = False
        self.logger.info("Task Started")
        return 0

    def start_Thread(self, start_task: bool = False) -> int:
        self._flag_thread_stop = False
        self.start()

        if start_task:
            self.start_Task()

        self.logger.info("Thread Started")
        return 0

    # @abstractmethod
    def set_Parameters(self, *args, **kwargs):
        #  Re-Write set_Parameter Function to set parameters for Task Function
        raise NotImplementedError

    # @abstractmethod
    def task(self, *args, **kwargs):
        #  Re-Write Task Function
        raise NotImplementedError

    def before_task_call(self):
        #  Re-Write before_task_call Function
        pass

    def after_task_call(self):
        #  Re-Write after_task_call Function
        pass

    def sleep(self, ms: float = 0):
        time.sleep(ms)
