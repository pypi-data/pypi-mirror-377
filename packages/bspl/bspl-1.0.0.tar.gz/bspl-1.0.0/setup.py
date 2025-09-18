#!/usr/bin/env python
from setuptools import setup
from setuptools.command.build_py import build_py
import sys


class Build(build_py):
    def run(self):
        # Try to build parser if possible, but don't fail if bspl isn't available yet
        try:
            sys.path.append("./")
            from bspl.parsers.bspl.build import build_parser, save_parser
            model = build_parser()
            save_parser(model)
        except ImportError:
            # Parser generation requires bspl to be available, skip during initial build
            pass
        super(Build, self).run()


setup(
    cmdclass={
        "build_py": Build,
    }
)
