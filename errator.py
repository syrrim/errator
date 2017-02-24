import sys
import traceback
from functools import wraps, partial
from contextlib import contextmanager
from itertools import islice


class LazyLine:
    def __init__(self, fn, ln):
        self.fn = fn
        self.ln = ln

    def __str__(self):
        try:
            with open(self.fn, "r") as f:
                return next(islice(f, self.ln - 1, None)).strip()
        except:
            return ""

    __repr__ = __str__


class Narration:
    def __init__(self, exc):
        self.exc = exc
        self.levels = []

    def def_fmt(self, **kw):
        return "  File {filename!r}, line {lineno}, in {name}\n    {line}".format(**kw)

    def print(self, file=sys.stderr):    
        tb = self.exc.__traceback__
        print("Traceback (most recent call last): (errator)", file=file)
        level = len(self.levels) - 1
        while tb is not None:
            if level >= 0 and self.levels[level][1] == tb:
                fmt = self.levels[level][0]
                level -= 1
            else:
                fmt = self.def_fmt
            frame = tb.tb_frame
            fn = frame.f_code.co_filename
            if fn != __file__:
                name = frame.f_code.co_name
                lineno = frame.f_lineno
                line = LazyLine(fn, lineno)
                print(fmt(filename=fn, lineno=lineno, name=name, line=line, local=frame.f_locals), file=file)
            tb = tb.tb_next
        print(self.exc.__class__.__name__ + ":", self.exc, file=file)

    @classmethod
    def append(cls, e, fmt):
        if not hasattr(e, "narration"):
            e.narration = cls(e)
        e.narration.levels.append((fmt, e.__traceback__.tb_next))
           

class narrate: #pep -9 class name
    def __init__(self, msg=None, fmt=None):
        self.msg = msg
        if fmt is not None:
            self.fmt = fmt
    
    fmt =  "  at {filename}:{lineno} in {name}: {msg}\n    {line}"
    def format(self, local={}, **kwargs):
        return self.fmt.format(msg=self.msg.format(**local), **kwargs)

    def __call__(self, f):
        @wraps(f)
        def errator_wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                Narration.append(e, self.format)
                raise 
                
        return errator_wrapper

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc, tb):
        if exc is not None:   
            Narration.append(exc, self.format)


sys_excepthook = sys.excepthook

def excepthook(exc_type, exc, tb):
    if hasattr(exc, "narration"):
        exc.narration.print(sys.stderr)
    else:
        sys_excepthook(exc_type, exc, tb)
        sys.excepthook = excepthook # sys_excepthook tries to reset itself 

sys.excepthook = excepthook


@contextmanager
def narration():
    try:
        yield
    except Exception as e:
        excepthook(e.__class__, e, e.__traceback__)

__all__ = ["narrate", "narration"]
