import logging
from logging.handlers import RotatingFileHandler
from os import listdir
from pathlib import Path
import sys


class ModuleLogger():
    def __init__(
        self,
        logger_name: str = "",
        logger_file_path: str | Path = "",
        logger=None,
        logger_level_stdo: int = logging.DEBUG,
        logger_level_file: int = logging.DEBUG,
        mode="a",
        maxBytes=1 * 1024 * 1024,
        backupCount=5,
        *args, **kwargs
    ):
        super(ModuleLogger, self).__init__(*args, **kwargs)

        self.logger_file_path = Path(logger_file_path)

        if logger is None:
            if logger_name == "":
                logger_name = self.__class__.__name__

            self.logger = self.create_logger(
                name=logger_name,
                path=self.logger_file_path,
                level_stdout=logger_level_stdo,
                level_file=logger_level_file,
                mode=mode,
                maxBytes=maxBytes,
                backupCount=backupCount
            )
        else:
            self.logger = logger

        self.logger.debug(f"Logger created: {self.logger_file_path}")

    def get_Logger(self) -> logging.Logger:
        """
        This method is used to get the logger.
        """
        return self.logger

    def set_Logger(self, logger: logging.Logger):
        """
        This method is used to set the logger.
        """
        self.logger = logger

    def get_Logs(self) -> list[Path]:
        """
        This method is used to get the logs from the logger file path.
        """
        root_path_log = self.logger_file_path.parent
        log_file_name = self.logger_file_path.name
        return [root_path_log / i for i in listdir(root_path_log) if log_file_name in i]

    def clear_logs(self):
        """
        This method is used to clear the logs.
        """
        for log in self.get_Logs():
            log.unlink()
        self.logger.debug(f"Logs cleared: {self.get_Logs()}")

    @staticmethod
    def create_logger(
        name: str,
        path: str | Path = "",
        level_stdout: int = logging.DEBUG,
        level_file: int = logging.DEBUG,
        mode: str = "a",
        maxBytes: int = 5 * 1024 * 1024,
        backupCount: int = 2
    ) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        stdout_formatter = logging.Formatter(
            '%(levelname)s | %(name)s | %(message)s'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            '%m-%d-%Y %H:%M:%S'
        )

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(level_stdout)
        stdout_handler.setFormatter(stdout_formatter)
        logger.addHandler(stdout_handler)

        if path:
            path_obj = Path(path)
            if not path_obj.parent.is_dir():
                if not path_obj.parent.exists():
                    path_obj.parent.mkdir(parents=True, exist_ok=True)

                file_handler = RotatingFileHandler(
                    path_obj, mode=mode, maxBytes=maxBytes, backupCount=backupCount
                )
                file_handler.setLevel(level_file)
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

        return logger
