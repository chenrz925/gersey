import json
import logging
from logging.config import dictConfig as logging_config
from abc import ABCMeta, abstractmethod
from argparse import Namespace
from pathlib import Path
import sys
from datetime import datetime
from uuid import uuid4

from ..const import ConfigAttrs


class Kernel(object, metaclass=ABCMeta):
    _user_config = Path.home() / '.geyser' / 'config.json'
    _project_config = Path.cwd() / '.geyser' / 'config.json'
    _default_config = {
        ConfigAttrs.MODULE_PATHS: list(filter(lambda it: it, sys.path)),
        ConfigAttrs.Interactive.STYLE: 'material'
    }

    def __init__(self, args: Namespace):
        self.args = args
        self.config = {}
        self._load_config()

        sys.path.clear()
        sys.path.extend(self.config[ConfigAttrs.MODULE_PATHS])

        self._init_logging()

    def wrap_function_object(self, name, func):
        return type(name, (), {
            '__name__': name,
            '__module__': 'geyser',
            '__call__': func
        })()

    def wrap_method(self, func):
        def wrapper(this, *args, **kwargs):
            func(*args, **kwargs)

        return wrapper

    def _init_logging(self):
        filename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}.{uuid4().hex}'
        logging_dir = Path.cwd() / '.geyser' / 'logs' / filename
        if not logging_dir.exists():
            logging_dir.mkdir(parents=True, exist_ok=True)
        handlers = {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'brief',
                'level': 'INFO',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'precise',
                'level': 'DEBUG',
                'filename': logging_dir / filename,
                'when': 'H',
            }
        }
        if self.args.verbose:
            handlers['console']['level'] = 'DEBUG'
        logging_config({
            'version': 1,
            'formatters': {
                'brief': {
                    'format': '[%(levelname)s] %(asctime)s: %(message)s',
                    'datefmt': '%Y-%m-%dT%H:%M:%S'
                },
                'precise': {
                    'format': '[%(levelname)s] (%(name)s) %(asctime)s: %(message)s',
                    'datefmt': '%Y-%m-%dT%H:%M:%S%z'
                }
            },
            'root': {
                'level': 'DEBUG',
                'handlers': list(handlers.keys())
            },
            'handlers': handlers
        })

    def _load_config(self):
        self.config.update(self._default_config)
        self._load_user_config()
        self._load_project_config()

    def _load_user_config(self):
        if not self._user_config.exists():
            self._init_user_config()
        with open(self._user_config, 'r') as fp:
            self.config.update(json.load(fp))

    def _init_user_config(self):
        if not self._user_config.parent.exists():
            self._user_config.parent.mkdir(parents=True, exist_ok=True)
        with open(self._user_config, 'w') as fp:
            json.dump({}, fp)

    def _load_project_config(self):
        if not self._project_config.exists():
            self._init_project_config()
        with open(self._project_config, 'r') as fp:
            self.config.update(json.load(fp))

    def _init_project_config(self):
        if not self._project_config.parent.exists():
            self._project_config.parent.mkdir(parents=True, exist_ok=True)
        with open(self._project_config, 'w') as fp:
            json.dump({}, fp)

    def run(self):
        try:
            self.on_start()
            while True:
                try:
                    self.on_execution_start()
                    self.execute()
                    self.on_execution_end()
                except BaseException as e:
                    self.on_execution_error(e)
        except BaseException as e:
            self.on_error(e)
        self.on_end()

    @abstractmethod
    def on_start(self):
        raise NotImplementedError(f'Method "on_start" is NOT implemented')

    @abstractmethod
    def on_end(self):
        raise NotImplementedError(f'Method "on_end" is NOT implemented')

    @abstractmethod
    def on_error(self, exception):
        raise NotImplementedError(f'Method "on_error" is NOT implemented')

    @abstractmethod
    def on_execution_start(self):
        raise NotImplementedError(f'Method "on_execution_start" is NOT implemented')

    @abstractmethod
    def on_execution_end(self):
        raise NotImplementedError(f'Method "on_execution_end" is NOT implemented')

    @abstractmethod
    def on_execution_error(self, exception):
        raise NotImplementedError(f'Method "on_execution_error" is NOT implemented')

    @abstractmethod
    def execute(self):
        raise NotImplementedError(f'Method "execute" is NOT implemented')
