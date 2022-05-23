import ast
import logging
import sys
from collections import deque
from copy import deepcopy
from inspect import isfunction
from pathlib import Path
from typing import Text

from . import Kernel
from .exception import LoopExit, ScriptExit


class _ScriptTreeTransformer(ast.NodeTransformer):
    def __init__(self, kernel, context):
        super(_ScriptTreeTransformer, self).__init__()
        self.kernel = kernel
        self.context = context
        self.name = None
        self.require = []

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == 'geyser':
            return None
        else:
            return self.visit(node)

    def visit_Call(self, node: ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            if func.id == 'include':
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        path = self.kernel.check_convert_path(arg.value)
                        if path not in self.kernel.scripts:
                            self.kernel.scripts[path] = {}
                    else:
                        raise ValueError('Function "include" only support constant string arguments')
            elif func.id == 'inject':
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        self.require.append(arg.value)
                    else:
                        raise ValueError('Function "inject" only support constant string arguments')
            elif func.id == 'syspath':
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        var = Path(arg.value).absolute()
                        if var not in sys.path:
                            sys.path.append(var)
                    else:
                        raise ValueError('Function "inject" only support constant string arguments')
            elif func.id == 'export':
                for arg in node.args:
                    if not isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        raise ValueError('Function "export" only support constant string arguments')
            elif func.id == 'name':
                arg, = node.args
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    self.name = arg.value
                else:
                    raise ValueError('Function "name" only support constant string arguments')

            return node
        else:
            return node


class ScriptKernel(Kernel):
    def check_convert_path(self, text) -> Path:
        path = Path(text).absolute()
        if not path.exists():
            raise FileNotFoundError(f'Geyser can\'t open file "{path}"')
        else:
            return path

    def __init__(self, args):
        super(ScriptKernel, self).__init__(args)
        self.scripts = dict(map(
            lambda it: (it, {}),
            map(self.check_convert_path, args.args)
        ))
        self.name_idx = {}
        self.next = None
        self.executions = deque()

    def tweak_tree(self, tree: ast.Module, context: Path):
        transformer = _ScriptTreeTransformer(self, context)
        tree = transformer.visit(tree)
        ast.fix_missing_locations(tree)
        self.scripts[context]['name'] = transformer.name
        self.scripts[context]['require'] = transformer.require
        self.name_idx[transformer.name] = context
        return tree

    def schedule_executions(self):
        required = {it['name']: set() for it in self.scripts.values()}
        for key, value in self.scripts.items():
            name_to = value['name']
            for name_from in value['require']:
                required[name_to].add(name_from)

        name_queue = deque()
        switch = True
        while switch:
            if name_queue:
                name = name_queue.popleft()
                if len(required[name]) == 0:
                    self.executions.append(self.name_idx[name])
                    for iname in required.keys():
                        if name in required[iname]:
                            required[iname].remove(name)
                elif name not in self.name_idx:
                    raise ValueError(f'Geyser can\'t find any "{name}"')
                else:
                    name_queue.append(name)
            else:
                name_queue = deque(filter(
                    lambda it: len(required[it]) == 0 and self.name_idx[it] not in self.executions,
                    required.keys()
                ))
                if len(name_queue) == 0:
                    switch = False

    def on_start(self):
        parse_queue = deque(self.scripts.keys())
        parsed_set = set()

        while True:
            if parse_queue:
                key = parse_queue.popleft()
                with open(key, 'r') as fp:
                    self.scripts[key]['ast'] = self.tweak_tree(ast.parse(fp.read()), key)
                    self.scripts[key]['code'] = compile(
                        self.scripts[key]['ast'], filename=str(key), mode='exec', optimize=2
                    )
                    parsed_set.add(key)
            else:
                total_set = set(self.scripts)
                parse_queue.extend(total_set - parsed_set)
                if not parse_queue:
                    break

        self.schedule_executions()

    def on_end(self):
        pass

    def on_error(self, exception):
        if isinstance(exception, LoopExit):
            pass
        else:
            raise exception

    def on_execution_start(self):
        if self.executions:
            self.next = self.executions.popleft()
        else:
            self.next = None

    def on_execution_end(self):
        pass

    def on_execution_error(self, exception):
        if isinstance(exception, ScriptExit):
            pass
        else:
            raise exception

    def build_globals_locals(self):
        glbs = {}
        lcls = {}

        glbs['__name__'] = '__main__'
        glbs['__file__'] = str(self.next)
        context: Path = self.next

        def _name(this, text: Text):
            pass

        glbs['name'] = self.wrap_function_object('Name', _name)

        def _include(this, *args):
            pass

        glbs['include'] = self.wrap_function_object('Include', _include)

        def _export(this, *args, **kwargs):
            if 'export' not in self.scripts[context]:
                self.scripts[context]['export'] = {}
            for var in args:
                self.scripts[context]['export'][var] = lcls[var]
            for var_to, var_from in kwargs.items():
                self.scripts[context]['export'][var_to] = lcls[var_from]

        glbs['export'] = self.wrap_function_object('Export', _export)

        def _repr(key, proto):
            def wrapper(*args, **kwargs):
                txt = '{}{{{}}}'.format(key, ', '.join(proto.keys()))
                return txt

            return wrapper

        def _inject(this, *args):
            for arg in args:
                if arg in self.name_idx:
                    name = ''.join(map(lambda it: it.capitalize(), arg.split('_')))
                    proto = deepcopy(self.scripts[self.name_idx[arg]]['export'])
                    proto['__name__'] = name
                    proto['__module__'] = f'geyser.{arg}'
                    for key in proto.keys():
                        if isfunction(proto[key]):
                            proto[key] = self.wrap_method(proto[key])
                    proto['__repr__'] = _repr(arg, self.scripts[self.name_idx[arg]]['export'])
                    proto['__str__'] = proto['__repr__']
                    lcls[arg] = type(name, (), proto)()
                else:
                    raise ValueError(f'"{arg}" isn\'t a valid name')

        glbs['inject'] = self.wrap_function_object('Export', _inject)

        def _syspath(this, *args):
            pass

        glbs['syspath'] = self.wrap_function_object('Syspath', _syspath)

        logger = logging.getLogger(context.name)

        def _printd(this, *args, **kwargs):
            logger.debug(*args, **kwargs)

        glbs['printd'] = self.wrap_function_object('PrintDebug', _printd)

        def _printi(this, *args, **kwargs):
            logger.info(*args, **kwargs)

        glbs['printi'] = self.wrap_function_object('PrintInfo', _printi)

        def _printw(this, *args, **kwargs):
            logger.warning(*args, **kwargs)

        glbs['printw'] = self.wrap_function_object('PrintWarning', _printw)

        def _printe(this, *args, **kwargs):
            logger.error(*args, **kwargs)

        glbs['printe'] = self.wrap_function_object('PrintError', _printe)

        def _printc(this, *args, **kwargs):
            logger.critical(*args, **kwargs)

        glbs['printc'] = self.wrap_function_object('PrintCritical', _printc)

        def _print(this, *args, **kwargs):
            if 'file' in kwargs and kwargs['file'] != sys.stdout:
                print(*args, **kwargs)
            else:
                logger.info(*args)

        glbs['print'] = self.wrap_function_object('Print', _print)

        def _exit(this, *args, **kwargs):
            raise ScriptExit()

        glbs['exit'] = type('exit', (), {
            '__name__': exit.__class__.__name__,
            '__module__': exit.__class__.__module__,
            '__str__': exit.__class__.__str__,
            '__repr__': exit.__class__.__repr__,
            '__call__': _exit
        })()

        return glbs, lcls

    def execute(self):
        if self.next is None:
            raise LoopExit()
        else:
            exec(self.scripts[self.next]['code'], *self.build_globals_locals())
