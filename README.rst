Errator
=======

Provide human-readable error narration of exception tracebacks with Errator.

#. `Intro <#intro>`__
#. `Example <#example>`__
#. `Reason For Forking <#reason-for-forking>`__

Intro
-----

A stack trace generally provides a small amount of the information required to
understand the reason behind an error. Normally you need not just the function
stack leading to an error, but the values that were passed to each function as
well. This is usually done by logging the values, even when no error has
occurred. This can clog the output, and make it hard to tell which line of log
comes from where. 

The solution provided here it to interweave logging and stack traces. The log
will only be output if an exception flows passed the logging function. Further,
it will be output inline with the stacktrace, making it easier to understand
where each log is from. 

Example
-------

.. code:: python
    
    @narrate()
    def f2(val):
        if val > 10:
            with narrate("big val"):
                raise Exception("Too large")
        else:
            with narrate("small val")
                raise Exception("Too small")


    @narrate()
    def f1():
        return f2() + 1

    f1()

Running this code results in this output::

    Traceback (most recent call last): (errator)
      File 'example.py', line 17, in <module>
        f1()
      at example.py:15 in f1: 
        return f2(7) + 1
      at example.py:10 in f2: 
      at example.py:10 in f2: small val
        raise Exception("Too small")
    Exception: Too small


Reason For Forking
------------------

When I saw the upstream module, I thought it was a sensible idea, and had been
thinking about doing something similar. However, I felt the author had brought in unneeded complexity:
    
#. Global state

   Rather than attaching state to the exception, a global bank of state was
   maintained. Naturally, this brought on complexity with dealing with threads
   which had to be fixed. It also meant that the state wasn't always synced to
   what you were doing, and you had to manually sync it. Since narration
   occurred due to exceptions anyways, it seemed sensible to attach the state to
   the exception instead. 

#. Messing up stack traces

   By default, the original version would interject in the middle of stack
   traces with a decorated function. Like most things, this could be configured
   away, but it seemed quite silly for the default behaviour. 


#. Manual outputting

   In order to get nice looking output, you had to manually iterate over the
   narration and output each line individually. This was purported to be
   because you might want to remove some of the lines, but I felt this was too
   uncommon a situation to make the default. 
   
#. Manually formatting

   No formatting of the narration would be done by default; the user was
   expected to write every character they wanted output. In the example code,
   every narration had the exact same format, which seemed like a job the
   library could be doing trivially. While the output can be reformatted, it
   provides useful information without requiring any work on the part of the
   user. 

#. Separate functions

   This one is simple, but still silly. For some reason, the author chose to
   make the functions for decorator and context managers different, being
   ``narrate`` and ``narrate_cm`` respectively. Since context manager and
   decorators have completely different interfaces, and the two functions took
   the same  arguments, they were very easy to merge. 


While all this details the reason for not using haxsaw/errator, it doesn't
explain why a full rewrite required a fork. This is simply because I thought
the name was nice, and didn't want to come up with a new one. 
