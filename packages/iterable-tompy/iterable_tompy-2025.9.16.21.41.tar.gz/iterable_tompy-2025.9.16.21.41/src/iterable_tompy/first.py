from typing import Iterable, Iterator, TypeVar

from .exceptions import InputNotIterableError, EmptyIterableError

T = TypeVar('T')


def first(iterable: Iterable[T]) -> T:
    try:
        # Sequences can be handled more efficiently than Iterables
        # noinspection PyUnresolvedReferences
        first_item: T = iterable[0]
    except (TypeError, IndexError):
        try:
            iterator: Iterator = iter(iterable)
        except TypeError as exception:
            raise InputNotIterableError(f"'{iterable}' is not iterable.") from exception

        try:
            first_item: T = next(iterator)
        except StopIteration as exception:
            raise EmptyIterableError(f"'{iterable}' contains no items.") from exception

    return first_item
