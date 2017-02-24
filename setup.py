from distutils.core import setup

from errator import __version__

setup(
    name="errator",
    py_modules=["errator"],
    version="0.0.1",
    description="Errator allows you to create human-readable exception narrations",
    author="Syrrim",
    author_email="syrrim0@gmail.com",
    url="https://github.com/syrrim/errator",
    keywords=["exception", "logging", "traceback", "stacktrace"],
    classifiers=[],
)
