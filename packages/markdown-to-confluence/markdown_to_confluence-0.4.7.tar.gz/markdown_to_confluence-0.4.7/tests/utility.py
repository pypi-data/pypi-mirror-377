"""
Publish Markdown files to Confluence wiki.

Copyright 2022-2025, Levente Hunyadi

:see: https://github.com/hunyadi/md2conf
"""

import unittest
from collections.abc import Container, Iterable
from typing import Optional, TypeVar, Union
from unittest.util import safe_repr

T = TypeVar("T")


class TypedTestCase(unittest.TestCase):
    def assertEqual(self, first: T, second: T, msg: Optional[str] = None) -> None:
        super().assertEqual(first, second, msg)

    def assertNotEqual(self, first: T, second: T, msg: Optional[str] = None) -> None:
        super().assertNotEqual(first, second, msg)

    def assertIn(self, member: T, container: Union[Iterable[T], Container[T]], msg: Optional[str] = None) -> None:
        super().assertIn(member, container, msg)

    def assertNotIn(self, member: T, container: Union[Iterable[T], Container[T]], msg: Optional[str] = None) -> None:
        super().assertNotIn(member, container, msg)

    def assertListEqual(self, list1: list[T], list2: list[T], msg: Optional[str] = None) -> None:
        super().assertListEqual(list1, list2, msg=msg)

    def assertStartsWith(self, text: str, prefix: str, msg: Optional[str] = None) -> None:
        """Just like self.assertTrue(text.startswith(prefix)), but with a nicer default message."""

        if not text.startswith(prefix):
            standardMsg = "%s does not start with %s" % (
                safe_repr(text),
                safe_repr(prefix),
            )
            self.fail(self._formatMessage(msg, standardMsg))
