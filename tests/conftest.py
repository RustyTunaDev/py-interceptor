from typing import Type

import pytest

METHODS = [
    "public_method",
    "_protected_method",
    "_DummyTarget__private_method",
    "static_method",
    "class_method"
]


class DummyTarget:
    def public_method(self, a: int, b: int):
        return a + b

    def _protected_method(self, a: int, b: int):
        return a + b

    def __private_method(self, a: int, b: int):
        return a + b

    @staticmethod
    def static_method(a: int, b: int):
        return a + b

    @classmethod
    def class_method(cls, a: int, b: int):
        return a + b

