import ast
import logging
import re
import traceback
from collections import deque
from importlib.metadata import metadata
from platform import python_implementation, python_version, python_compiler

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import ThreadedCompleter
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import PromptSession, yes_no_dialog, CompleteStyle
from prompt_toolkit.styles import style_from_pygments_cls
from pygments.lexers.python import Python3Lexer
from pygments.styles import get_style_by_name

from .base import Kernel
from .exception import LoopExit
from .jedi import Python3Completer
from ..const import ConfigAttrs


class InteractiveKernel(Kernel):
    def _key_bindings(self):
        bindings = KeyBindings()

        @bindings.add('enter', 'enter')
        def _(event: KeyPressEvent):
            if event.current_buffer.text.strip():
                event.current_buffer.validate_and_handle()

        @bindings.add('c-c')
        def _(event: KeyPressEvent):
            event.current_buffer.reset()

        @bindings.add('c-d')
        def _(event: KeyPressEvent):
            event.current_buffer.reset()
            event.current_buffer.insert_text('exit()')
            event.current_buffer.validate_and_handle()

        return bindings

    def _prompt_continuation(self, width, line_number, is_soft_wrap):
        cursor_line = self.prompt.default_buffer.text[:self.prompt.default_buffer.cursor_position].count('\n')
        if line_number == cursor_line:
            return ' +' + '-' * (width - 4) + '> '
        else:
            return ' +' + ' ' * (width - 2)

    def _tweak_tree(self, tree: ast.Module):
        tail = tree.body.pop()
        if isinstance(tail, ast.Expr):
            tree.body.append(ast.Assign(
                targets=[
                    ast.Name(id=f'_{self.exec_idx}', ctx=ast.Store())
                ],
                value=tail.value
            ))
            tree.body.append(ast.If(
                test=ast.Compare(
                    left=ast.Name(id=f'_{self.exec_idx}', ctx=ast.Load()),
                    ops=[ast.IsNot()],
                    comparators=[ast.Constant(value=None)]
                ),
                body=[ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id='print', ctx=ast.Load()),
                        args=[
                            ast.Call(
                                func=ast.Name(id='repr', ctx=ast.Load()),
                                args=[
                                    tail.value
                                ],
                                keywords=[]
                            )
                        ],
                        keywords=[]
                    )
                )],
                orelse=[]
            ))
        else:
            tree.body.append(tail)

        ast.fix_missing_locations(tree)
        return tree

    def __init__(self, args):
        super(InteractiveKernel, self).__init__(args)

        self.style = style_from_pygments_cls(get_style_by_name(self.config[ConfigAttrs.Interactive.STYLE]))
        self.completer = Python3Completer()
        self.prompt = PromptSession(
            lexer=PygmentsLexer(Python3Lexer), style=self.style,
            completer=ThreadedCompleter(self.completer), complete_in_thread=True,
            complete_while_typing=True, multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
            mouse_support=False, key_bindings=self._key_bindings(),
            prompt_continuation=self._prompt_continuation,
            editing_mode=EditingMode.VI, complete_style=CompleteStyle.MULTI_COLUMN
        )
        self.exec_idx = 1
        self.globals = {}
        self.locals = {}
        self.commands = deque()
        self.last_success = 0
        self._initialize_globals()

    def _upgrade_locals(self):
        def _filter(item):
            return not (re.match(r'_[0-9]+', item[0]) and item[1] is None)

        self.globals.update(filter(_filter, self.locals.items()))
        self.locals.clear()

    def _initialize_globals(self):
        def _exit(this, *args, **kwargs):
            raise LoopExit()

        self.globals['exit'] = type('exit', (), {
            'name': 'exit',
            'eof': 'Ctrl-D',
            '__name__': exit.__class__.__name__,
            '__module__': exit.__class__.__module__,
            '__str__': exit.__class__.__str__,
            '__repr__': exit.__class__.__repr__,
            '__call__': _exit
        })()

        logger = logging.getLogger('geyser')

        def _printd(this, *args, **kwargs):
            logger.debug(*args, **kwargs)

        self.globals['printd'] = self.wrap_function_object('PrintDebug', _printd)

        def _printi(this, *args, **kwargs):
            logger.info(*args, **kwargs)

        self.globals['printi'] = self.wrap_function_object('PrintInfo', _printi)

        def _printw(this, *args, **kwargs):
            logger.warning(*args, **kwargs)

        self.globals['printw'] = self.wrap_function_object('PrintWarning', _printw)

        def _printe(this, *args, **kwargs):
            logger.error(*args, **kwargs)

        self.globals['printe'] = self.wrap_function_object('PrintError', _printe)

        def _printc(this, *args, **kwargs):
            logger.critical(*args, **kwargs)

        self.globals['printc'] = self.wrap_function_object('PrintCritical', _printc)

        def _print(this, *args, **kwargs):
            if 'file' in kwargs and kwargs['file'] != sys.stdout:
                print(*args, **kwargs)
            else:
                logger.info(*args)

        self.globals['print'] = self.wrap_function_object('Print', _print)

    def execute(self):
        if self.commands:
            command: str = self.commands.pop()
            fname = f'<input@{self.exec_idx}>'
            tree = self._tweak_tree(ast.parse(command, fname, 'exec'))
            code = compile(tree, fname, 'exec', optimize=2)
            exec(code, self.globals, self.locals)
            self._upgrade_locals()
            self.completer.history.append(command)
            self.last_success = self.exec_idx

    def on_start(self):
        version = metadata("geyser")['Version']
        print(
            f'\U000026F2 Geyser v{version} '
            f'| \U0001f40D {python_implementation()} {python_version()} '
            f'| \U0001F680 {python_compiler()}'
        )

    def on_end(self):
        print('Bye!')

    def on_error(self, exception):
        if isinstance(exception, LoopExit):
            pass
        else:
            print(traceback.format_exc())

    def on_execution_start(self):
        message = [
            ('class:pygments.literal.string.symbol', f'['),
            ('class:pygments.literal.number.integer', f'{self.exec_idx}'),
            ('class:pygments.literal.string.symbol', f']> '),
        ]
        command = self.prompt.prompt(
            message
        )
        if command.strip():
            self.commands.appendleft(command)

    def on_execution_end(self):
        if self.last_success == self.exec_idx:
            self.exec_idx += 1

    def on_execution_error(self, exception):
        if isinstance(exception, LoopExit):
            if yes_no_dialog('Geyser', 'Do you really want to exit?').run():
                raise exception
            else:
                self.exec_idx += 1
        else:
            print(traceback.format_exc())
