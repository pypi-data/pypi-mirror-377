from typing import Iterable, Iterator, TypeVar

from .exceptions import InputNotIterableError, EmptyIterableError

T = TypeVar('T')


def tail(iterable: Iterable[T]) -> Iterator[T]:
    try:
        # Sequences can be handled more efficiently than Iterables
        # noinspection PyUnresolvedReferences
        tail_items: Iterator[T] = iter(iterable[1:])
    except TypeError:
        try:
            iterator: Iterator[T] = iter(iterable)
        except TypeError as exception:
            raise InputNotIterableError(f"'{iterable}' is not iterable.") from exception

        try:
            _: T = next(iterator)
            tail_items: Iterator[T] = iterator
        except StopIteration:
            tail_items: Iterator[T] = iter(())

    return tail_items
