Errator
=======

Provide human-readable error narration of exception tracebacks with Errator.

#. `Intro <#intro>`__
#. `How it works <#how-it-works>`__
#. `Requirements <#requirements>`__
#. `Installing <#installing>`__
#. `Quick Tutorial <#quick-tutorial>`__

Intro
-----

Errator came as an idea on the back of trying to figure out what the semantics
of an exception traceback are in non-trivial pieces of code.

When an exception occurs deep inside a call stack within some generic utility
function that is used in numerous contexts, the traceback doesn't provide
enough information to diagnose the problem. Data values aren't obvious, and the
initial starting conditions of the error can't easily been seen.

Logging is a step in the right direction, but in general outputs too much
information; often, there is lots of info regarding error-free processing in
the log, making it hard to find the right log output that is associated with
the error. 

Errator is something of a marriage between logging and tracebacks: as an
exception flows down the call stack, extra information about the conditions of
the call can be attached to the exception.

How it works
------------

Errator uses decorators and context managers to maintain a stack of "narration
fragments" behind the scenes. When code executes without exceptions, these
fragments are never created.  However, when an exception is raised, the
narration fragments are created and attached to the exception. When the
exception reaches the top level, the narration will be interwoven with the stack
trace, allowing interpretation of both pieces of information together. 

Errator is transparently thread-safe, since it doesn't maintain any global
state, and only maintains state on each exception. 

Requirements
------------

Errator doesn't have any external dependencies. It is compatible Python 3.x.

Installing
----------

Errator is a single file, and can be installed by running
'python setup.py install' after cloning the Git project.

Quick Tutorial
--------------

The next section discusses Errator with functions, but you can also use the
decorators described with methods too.

Start with pulling errator into your module that you want to narrate:

.. code:: python

    from errator import narrate

Now, suppose you have a utility function that performs some specialized string
formatting, but it is possible to pass in arguments that cause a exception to
be raised.  Your function is called all over the place for a variety of
different reasons, often very deep down the call stack where it isn't obvious
what the original functional intent was, or where the source of bad arguments
may have been.


To start building the narration to your function's execution, you can use the
``narrate()`` decorator to associate a bit of text with your utility function
to provide easily understandable explanations about what's going on:

.. code:: python

    @narrate("I'm trying to format a string")
    def special_formatter(fmt_string, **kwargs):
        # magic format code that sometimes raises an exception

The ``narrate()`` decorator knows to look for exceptions and doesn't impede
their propagation, but captures that bit of text in an internal stack when an
exception occurs. So if you write:

.. code:: python

    try:
        s = special_formatter(fmt, **args)
    except Exception as e:
        e.narration.print()

...and ``special_formatter()`` raises an exception, the exception will still
bubble up the stack, but ``narration.print()`` will output to stderr the
narration of what led to the exception. You can also use the ``narration``
context manager to do this automatically:
    
.. code:: python
    
    with narration():
        s = special_formatter(fmt, **args)


To further control what each narration looks like, there are two levels of
customization. The first argument to ``narrate`` will be formatted with the
locals of the function/context manager it decorates, and you can use them to
describe what happened. 

.. code:: python

    @narrate("I'm trying to format a string with {fmt_string!r} and args {kwargs}")
    def special_formatter(fmt_string, **kwargs):
        # magic format code that sometimes raises an exception

The second argument to ``narrate`` (or the keyword argument ``fmt``) describes
the full text that will be output for that level of the stack trace. It is also
a formatting string, and receives the args "msg" (the first arg, described
above), "filename", "name" (of the function), "lineno", and "line". It defaults
to this:

"  at {filename}:{lineno} in {name}: {msg}\n    {line}"

``narrate`` works the exact same way when used as a context manager, allowing
you to narrate your function in finer detail:


.. code:: python

    def special_formatter(fmt_string, **kwargs):
        for format_token in parse_format(fmt_string):
            if format_token.type == float:
                with narrate("I started processing a float format"):
                    # do magic stuff for floats...
            elif format_token.type == int:
                with narrate("I started processing an int format"):
                    # do magic stuff for ints...


Let's look at an example with more complex calling relationships.  Suppose we
have functions ``A``, ``B``, ``C``, ``D``, ``E``, and ``F``. They have the
following calling relationships:


* ``A`` calls ``B`` then ``C``
* ``B`` calls ``D``
* ``C`` calls ``E`` or ``F``
* ``D`` calls ``F``


We'll make it so that if we're unlucky enough to call ``E``, we'll get an
exception raised.  This will happen only for input values of ``A`` greater than
10.

So let's define these functions and narrate them-- paste these into an
interactive Python session after you've imported errator:

.. code:: python

    @narrate("val: {val}")
    def A(val):
        B(val / 2)
        C(val * 2)
        
    @narrate("val: {val}")
    def B(val):
        D(val * 10)
        
    @narrate("val: {val}")
    def C(val):
        if val > 20:
            E(val)
        else:
            F(val)
            
    @narrate("val: {val}")
    def D(val):
        F(val * 3)
        
    @narrate("val: {val}")
    def E(val):
        raise ValueError("how dare you call me with such a value?")
        
    @narrate("val: {val}")
    def F(val):
        print("very well")

Now run ``A`` with a value less than 11, and look at the output:

.. code:: python

    >>> A(3)
    very well
    very well

Now run ``A`` with a value greater than 10:

.. code:: python

    >>> A(11)
    very well
    Traceback (most recent call last): (errator)
    File '<stdin>', line 1, in <module>
	
    at /home/cameron/errator/example.py:6 in A: val: 12
	C(val * 2)
    at /home/cameron/errator/example.py:15 in C: val: 24
	E(val)
    at /home/cameron/errator/example.py:25 in E: val: 24
	raise ValueError("how dare you call me with such a value?")
    ValueError: how dare you call me with such a value?
    >>> 

In this way you can recieve a more detailed view of what caused the error to happen.

