from typing import Iterable, Iterator, TypeVar

from .exceptions import InputNotIterableError, EmptyIterableError

T = TypeVar('T')


def head(iterable: Iterable[T]) -> T:
    try:
        # Sequences can be handled more efficiently than Iterables
        # noinspection PyUnresolvedReferences
        head_item: T = iterable[0]
    except (TypeError, IndexError):
        try:
            iterator: Iterator[T] = iter(iterable)
        except TypeError as exception:
            raise InputNotIterableError(f"'{iterable}' is not iterable.") from exception

        try:
            head_item: T = next(iterator)
        except StopIteration as exception:
            raise EmptyIterableError(f"'{iterable}' contains no items.") from exception

    return head_item
