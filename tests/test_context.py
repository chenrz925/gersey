from geyser import Geyser
from taskflow.patterns.linear_flow import Flow
from taskflow import engines


@Geyser.functor()
def f(test, *args, **kwargs):
    assert test == 'TEST'


class TestContext(object):
    def test_empty_profile(self):
        context = Geyser._build_context({})

    def test_context_task(self, capsys):
        context = Geyser._build_context({})
        context.inject_atoms([{
            'reference': 'tests.test_geyser.EchoTask',
            'name': 'echo_task',
            'type': 'task'
        }])
        context._atoms['echo_task'].execute(1, 2, 3, a=1, b=2, c=3)
        assert capsys.readouterr().out == "(1, 2, 3)\n{'a': 1, 'b': 2, 'c': 3}\n"

    def test_context_functor_inject(self):
        context = Geyser._build_context({})
        context.inject_atoms([{
            'reference': 'tests.test_context.F',
            'name': 'f_task',
            'type': 'functor',
            'inject': {
                'test': 'TEST'
            }
        }])
        flow = Flow('flow')
        flow.add(context._atoms['f_task'])
        e = engines.load(flow)
        e.run()
