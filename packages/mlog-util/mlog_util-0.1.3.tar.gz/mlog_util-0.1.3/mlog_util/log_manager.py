import logging
import threading
from rich.logging import RichHandler
from typing import Type, List, Optional

# from .handlers import MultiProcessSafeSizeRotatingHandler, MultiProcessSafeTimeRotatingHandler

class LogManager:
    _logger_cache = {}
    _lock = threading.Lock()  # 多线程安全

    @classmethod
    def get_logger(
        cls,
        name: str,
        logger_cls: Type[logging.Logger] = logging.Logger,
        log_file: str | None = None,
        add_console: bool = True,
        level: int = logging.INFO,
        custom_handlers: list[logging.Handler] | None = None,
    ) -> logging.Logger:
        """
        获取或创建 logger。

        :param name: logger 名称
        :param logger_cls: logger 类
        :param log_file: 日志文件路径
        :param add_console: 是否添加控制台 RichHandler
        :param level: 日志级别
        :param custom_handlers: 自定义 Handler 列表
        """
        cache_key = (name, logger_cls)
        with cls._lock:
            if cache_key not in cls._logger_cache:
                # 创建 logger
                if logger_cls == logging.Logger:
                    logger = logging.getLogger(name)
                else:
                    logger = logger_cls(name)

                logger.setLevel(level)
                logger.propagate = False  # 不向 root logger 冒泡

                # 添加控制台 handler
                if add_console:
                    if not any(isinstance(h, RichHandler) for h in logger.handlers):
                        console_handler = RichHandler(rich_tracebacks=True)
                        console_formatter = logging.Formatter(
                            "%(message)s        [%(name)s - %(asctime)s]",
                            datefmt="%Y-%m-%d %H:%M:%S"
                        )
                        console_handler.setFormatter(console_formatter)
                        logger.addHandler(console_handler)

                # 添加文件 handler
                if log_file:
                    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
                        # handler = MultiProcessSafeSizeRotatingHandler(log_file, maxBytes=10*200, backupCount=3)
                        # file_handler = logging.FileHandler(log_file, encoding="utf-8")

                        handler = logging.FileHandler(log_file, encoding="utf-8")
                        file_formatter = logging.Formatter(
                            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S"
                        )
                        handler.setFormatter(file_formatter)
                        logger.addHandler(handler)

                # 添加自定义 handler
                if custom_handlers:
                    h = custom_handlers
                    if h not in logger.handlers:
                        file_formatter = logging.Formatter(
                            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S"
                        )
                        h.setFormatter(file_formatter)
                        logger.addHandler(h)
                        logger.addHandler(h)

                cls._logger_cache[cache_key] = logger

            return cls._logger_cache[cache_key]


# 全局可用的 get_logger 函数（无需引用 LogManager）
def get_logger(
    name: str=None,
    logger_cls: Type[logging.Logger] = logging.Logger,
    log_file: Optional[str] = None,
    add_console: bool = True,
    level: int = logging.INFO,
    custom_handlers: Optional[List[logging.Handler]] = None,
):
    """
    便捷函数：获取日志记录器，无需关心 LogManager 实例化。
    
    使用示例：
        from log_manager import get_logger
        logger = get_logger("my_module", log_file="app.log")
        logger.info("Hello world")
    """
    if name is None:
        name = "tmp_log"

    return LogManager.get_logger(
        name=name,
        logger_cls=logger_cls,
        log_file=log_file,
        add_console=add_console,
        level=level,
        custom_handlers=custom_handlers
    )

# logger = LogManager().get_logger("tmp_log")

