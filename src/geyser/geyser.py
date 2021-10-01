import argparse
import json
import plistlib
import sys
from collections import OrderedDict
from inspect import isfunction
from logging import config as logging_config, getLogger as get_logger
from os import environ, system
from os.path import abspath
from pathlib import Path
from platform import python_version, python_compiler, python_build, platform, python_implementation
from sys import path as sys_path
from typing import Callable, MutableMapping, Mapping, Text, Type, Any, Sequence

from more_itertools import flatten

if sys.version_info < (3, 10):
    try:
        from importlib_metadata import entry_points
    except ModuleNotFoundError:
        from pkg_resources import iter_entry_points


        def entry_points(*args, **kwargs):
            return tuple(iter_entry_points(*args, **kwargs))
else:
    from importlib.metadata import entry_points

import pyhocon
import toml
from ruamel import yaml
from setproctitle import setproctitle
from taskflow.atom import Atom
from taskflow.flow import Flow
from taskflow.patterns.graph_flow import Flow as GraphFLow, TargetedFlow
from taskflow.patterns.linear_flow import Flow as LinearFlow
from taskflow.patterns.unordered_flow import Flow as UnorderedFlow

from .context import Context
from .typedef import FunctorMeta, AtomMeta

__version__ = '0.4.8'


class Geyser(object):
    """
    # 基本用法

    从`geyser`导入`Geyser`类。

    Example:

    ```python
    from geyser import Geyser
    ```

    `Geyser`类是Geyser的入口，同时你也可以通过[Geyser.task][geyser.Geyser.task]和[Geyser.functor][geyser.Geyser.functor]引入你自定义的任务。

    Raises:
        FileNotFoundError: 当配置文件路径搜索不到文件时，会触发该异常。
        NotImplementedError: 当配置文件格式不受支持时，会触发该异常。
    
    
    """
    _atom_classes: MutableMapping[Text, AtomMeta] = OrderedDict()
    _functors: MutableMapping[Text, FunctorMeta] = OrderedDict()
    _flow_classes: Mapping[Text, Type[Flow]] = OrderedDict((
        ('linear', LinearFlow),
        ('unordered', UnorderedFlow),
        ('graph', GraphFLow),
        ('targeted_graph', TargetedFlow),
    ))

    _logger = None

    @classmethod
    def task(
            cls,
            provides: Sequence[Text] = (),
            requires: Sequence[Text] = (),
            revert_requires: Sequence[Text] = ()
    ) -> Callable[[Type[Atom]], Type[Atom]]:
        """

        # 任务注册器

        注册一个任务，你可以完全继承[Atom][taskflow.atom.Atom]来定义任务所有的行为，也可以通过继承[Task][taskflow.task.Task]来简单定义任务行为。

        ## 提供参数

        任务的返回值需要按照[Results specification](https://docs.openstack.org/taskflow/latest/user/arguments_and_results.html#results-specification)中返回值的规定。
        
        简单来讲，即符合以下规则：

        |`provides`类型|示例      |返回值                  |
        |-------------|----------|-----------------------|
        |`tuple(...)` |`('foo',)`|`return 'FOO',`        |
        |`set(...)`   |`{'set',}`|`return {'foo': 'FOO'}`|

        Warning:
            当`provides`只包含一个参数名时，需要在返回值时确保返回的参数被打包成序列的形式。

            Example:
                ```python
                from geyser import Geyser
                from taskflow.task import Task

                @Geyser.task(provides=('foo',))
                class Foo(Task):
                    def execute(self, foo):
                        return 'FOO', # 或者 ['FOO']
                        #           ^ 注意这里的逗号！
                ```
        
        ## 注入日志记录器

        当`execute`函数中定义了logger参数，Geyser将自动注入一个[Logger][logging.Logger]实例，但logger作为参数不需要在`provides`中定义。

        ## 其他

        关于任务行为的定义方法，详见[Task][taskflow.task.Task]。

        `Geyser.task`是一个装饰器函数，如果需要显式调用，可以依照如下方式。

        Example:
            ```python
            from geyser import Geyser
            from taskflow.task import Task

            class Foo(Task):
                def execute(self, foo):
                    return 'FOO', # 或者 ['FOO']
                    #           ^ 注意这里的逗号！
            
            Geyser.task(provides=('foo',))(Foo)
            ```
        
        `Geyser.task`不会改变代码原类定义的任何性质，仍然可以通过显式调用的方式对任务进行调用。

        Args:
            provides (Sequence[Text], optional): 任务提供的参数。
            requires (Sequence[Text], optional): 任务依赖的参数。
            revert_requires (Sequence[Text], optional): 任务回退提供的参数。

        Returns:
            Callable[[Type[Atom]], Type[Atom]]: 注册函数。
        """
        def wrapper(atom: Type[Atom]) -> Type[Atom]:
            reference = f'{atom.__module__}.{atom.__name__}'
            if issubclass(atom, Atom):
                cls._atom_classes[reference] = AtomMeta(
                    atom=atom,
                    provides=provides,
                    requires=requires,
                    revert_requires=revert_requires
                )
            else:
                cls._logger.error(f'Type "{reference}" is NOT a subclass of taskflow.atom.Atom')
            return atom

        return wrapper

    @classmethod
    def functor(
            cls,
            provides: Sequence[Text] = (),
            requires: Sequence[Text] = (),
            revert_requires: Sequence[Text] = ()
    ) -> Callable[[Callable], Callable]:
        """
        函数注册器

        通过[FunctorTask][taskflow.task.FunctorTask]对函数进行封装，注册封装后的`FunctorTask`。

        其他特性与[Geyser.task][geyser.Geyser.task]相同。

        Warning:
            通过Geyser进行任务编排时位置形参会失效，需要再次封装将位置形参作为某个参数传入函数，关于这方面的语言特定详见[函数定义](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#function-definitions)。

        Args:
            provides (Sequence[Text], optional): [description]. Defaults to ().
            requires (Sequence[Text], optional): [description]. Defaults to ().
            revert_requires (Sequence[Text], optional): [description]. Defaults to ().

        Returns:
            Callable[[Callable], Callable]: [description]
        """
        def wrapper(functor: Callable) -> Callable:
            reference = f'{functor.__module__}.{"".join(map(lambda it: it.capitalize(), functor.__name__.split("_")))}'
            if isfunction(functor):
                cls._functors[reference] = FunctorMeta(
                    functor=functor,
                    provides=provides,
                    requires=requires,
                    revert_requires=revert_requires
                )
            else:
                cls._logger.error(f'Object "{reference}" is NOT a function')
            return functor

        return wrapper

    @classmethod
    def _build_context(cls, profile: Mapping[Text, Any]):
        return Context(profile, cls._atom_classes, cls._functors, cls._flow_classes)

    @classmethod
    def _profile_search_paths(cls):
        return [
            Path('.').absolute(),
            *tuple(flatten(map(
                lambda it: it.profile_paths(),
                filter(
                    lambda it: hasattr(it, 'profile_paths'),
                    map(
                        lambda it: it.load(),
                        entry_points(group='geyser.profile')
                    )
                )
            )))
        ]

    @classmethod
    def _load_profile(cls, path: Text) -> Mapping[Text, Any]:
        for profile_root in cls._profile_search_paths():
            print(profile_root)
            profile_path = profile_root.joinpath(path)
            if profile_path.exists():
                suffix = path.split('.')[-1].lower()
                return getattr(cls, f'_load_profile_{suffix}', cls._load_profile_)(str(profile_path))

        raise FileNotFoundError(
            f'File {path} does NOT exist in ({", ".join(map(lambda it: str(it), cls._profile_search_paths()))})')

    @classmethod
    def _load_profile_(cls, path: Text) -> Mapping[Text, Any]:
        raise NotImplementedError(f'Format of profile "{path}" is not supported')

    @classmethod
    def _load_profile_json(cls, path: Text) -> Mapping[Text, Any]:
        with open(path, 'r') as fp:
            return json.load(fp)

    @classmethod
    def _load_profile_plist(cls, path: Text) -> Mapping[Text, Any]:
        with open(path, 'rb') as fp:
            return plistlib.load(fp)

    @classmethod
    def _load_profile_yaml(cls, path: Text) -> Mapping[Text, Any]:
        with open(path, 'r') as fp:
            return yaml.load(fp, Loader=yaml.Loader)

    @classmethod
    def _load_profile_yml(cls, path: Text) -> Mapping[Text, Any]:
        return cls._load_profile_yaml(path)

    @classmethod
    def _load_profile_toml(cls, path: Text) -> Mapping[Text, Any]:
        with open(path, 'r') as fp:
            return toml.load(fp)

    @classmethod
    def _load_profile_tml(cls, path: Text) -> Mapping[Text, Any]:
        return cls._load_profile_toml(path)

    @classmethod
    def _load_profile_hocon(cls, path: Text) -> Mapping[Text, Any]:
        if pyhocon:
            return pyhocon.ConfigFactory.parse_file(path)
        else:
            return cls._load_profile_(path)

    @classmethod
    def execute(cls, profile: Mapping[Text, Any]):
        context = cls._build_context(profile)
        return context()

    @classmethod
    def _build_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            'geyser',
            description='Inject and execute tasks.'
        )
        parser.add_argument(
            '-v', '--version',
            action='version',
            version=f'%(prog)s {__version__}'
        )
        parser.add_argument(
            '-d', '--debug',
            action='store_true',
        )
        parser.add_argument(
            '-l', '--log',
            nargs='+'
        )
        parser.add_argument(
            '-q', '--quiet',
            action='store_true'
        )
        parser.add_argument(
            '-e', '--edit',
            action='store_true'
        )
        parser.add_argument(
            'profile',
            nargs='+',
        )
        return parser

    @classmethod
    def _setting_logging(cls, ns):
        handlers = {}
        if not ns.quiet and not ns.log:
            handlers['console'] = {
                'class': 'logging.StreamHandler',
                'formatter': 'colored',
                'level': 'DEBUG' if ns.debug else 'INFO',
                'stream': 'ext://sys.stdout',
            }
        else:
            sys.stdin.close()
            sys.stdin = open('/dev/null', 'r')
            sys.stdout.close()
            sys.stdout = open('/dev/null', 'r')
            sys.stderr.close()
            sys.stderr = open('/dev/null', 'w')
        handlers.update(map(lambda it: (f'file{it[0]}', {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'plain',
            'level': 'DEBUG',
            'when': 'D',
            'filename': it[1]
        }), enumerate(ns.log if ns.log else [])))
        logging_config.dictConfig({
            'version': 1,
            'formatters': {
                'colored': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': "%(log_color)s(%(asctime)s)[%(levelname)s][%(process)d][%(thread)d][%(name)s]%(reset)s:"
                              " %(message)s",
                },
                'plain': {
                    '()': 'logging.Formatter',
                    'format': "(%(asctime)s)[%(levelname)s][%(process)d][%(thread)d][%(name)s]: %(message)s"
                }
            },
            'handlers': handlers,
            'root': {
                'level': 'NOTSET',
                'handlers': list(handlers.keys())
            }
        })
        cls._logger = get_logger(f'{cls.__module__}.{cls.__name__}')

    @classmethod
    def _setting_module_path(cls):
        sys_path.append(abspath('.'))
        path_file = Path.home() / '.geyser' / 'PYTHONPATH'
        if path_file.exists():
            with path_file.open('r') as fp:
                for path in fp.readlines():
                    sys_path.append(path.strip())

    @classmethod
    def _call_editor(cls, ns):
        editor_file = Path.home() / '.geyser' / 'EDITOR'
        if 'EDITOR' in environ:
            editor = environ['EDITOR']
        elif editor_file.exists():
            editor = editor_file.open('r').readline().strip()
        else:
            editor = 'vi'
        for profile in ns.profile:
            system(f'{editor} {profile}')

    @classmethod
    def entry(cls):
        """
        # 入口

        Geyser主程序入口。


        Example:
            ```bash
            # 通过`geyser`命令
            geyser --help
            # 通过调用`geyser`包：
            python -m geyser --help
            ```
        """
        ns = cls._build_parser().parse_args()
        cls._setting_module_path()
        cls._setting_logging(ns)
        cls._logger.info(f'Geyser {__version__}')
        cls._logger.info(
            f'Python ({python_implementation()}) {python_version()} {python_compiler()} {python_build()[1]}')
        cls._logger.info(f'OS {platform()}')
        if ns.edit:
            cls._call_editor(ns)
        else:
            for profile in ns.profile:
                setproctitle(f'geyser {profile}')
                context = cls._build_context(cls._load_profile(profile))
                context()
        return 0
