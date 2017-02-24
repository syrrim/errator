import sys
import errator
from errator import narrate, narration

def test_dec():
    @narrate("help", fmt="{msg}")
    def func():
        raise Exception()
    try:
        func()
    except Exception as e:
        assert hasattr(e, "narration")
        assert len(e.narration.levels) == 1
        assert e.narration.levels[0][0]() == "help"
    else:
        assert False

def test_cm():
    try:
        with narrate("help", fmt="{msg}"):
            raise Exception()
    except Exception as e:
        assert hasattr(e, "narration")
        assert len(e.narration.levels) == 1
        assert e.narration.levels[0][0]() == "help"
    else:
        assert False

def test_narration():
    with narration():
        1/0

