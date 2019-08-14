from smev_int.singleton import Singleton


def test_singleton():
    class Test(metaclass=Singleton):
        pass
    a = Test()
    b = Test()
    assert a is b