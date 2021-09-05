from taskflow.task import Task

from geyser import Geyser


@Geyser.task()
class EchoTask(Task):
    def execute(self, *args, **kwargs):
        print(args)
        print(kwargs)


@Geyser.functor()
def echo_functor(*args, **kwargs):
    print(args)
    print(kwargs)


class TestGeyser(object):
    def test_bind_meta(self):
        assert 'tests.test_geyser.EchoTask' in Geyser._atom_classes
        assert 'tests.test_geyser.EchoFunctor' in Geyser._functors
