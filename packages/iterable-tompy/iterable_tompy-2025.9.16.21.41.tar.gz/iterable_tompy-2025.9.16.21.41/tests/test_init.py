from typing import Iterator

import pytest

from src.iterable_tompy.init import init
from src.iterable_tompy.exceptions import InputNotIterableError


def test_init_non_iterator_failure():
    # Setup
    float0: float = 0.25

    # Validation
    with pytest.raises(InputNotIterableError):
        # noinspection PyTypeChecker
        _: Iterator = init(float0)


def test_init_empty_success():
    # Setup
    list0: list = []
    list1: list = []

    # Execution
    iterator0: Iterator = init(list0)

    # Validation
    assert list(iterator0) == list1


def test_init_single_item_success():
    # Setup
    integer0: int = 0
    integer1: int = 1
    integer2: int = 0
    list0: list = [integer0, integer1]
    list1: list = [integer2]

    # Execution
    iterator0: Iterator = init(list0)

    # Validation
    assert list(iterator0) == list1


def test_init_multiple_items_success():
    # Setup
    integer0: int = 0
    integer1: int = 1
    integer2: int = 2
    integer3: int = 3
    integer4: int = 4
    integer5: int = 0
    integer6: int = 1
    integer7: int = 2
    integer8: int = 3
    list0: list = [integer0, integer1, integer2, integer3, integer4]
    list1: list = [integer5, integer6, integer7, integer8]

    # Execution
    iterator0: Iterator = init(list0)

    # Validation
    assert list(iterator0) == list1
