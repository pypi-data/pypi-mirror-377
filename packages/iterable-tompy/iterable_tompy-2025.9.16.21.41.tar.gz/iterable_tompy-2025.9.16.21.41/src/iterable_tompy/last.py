from typing import Iterable, Iterator, TypeVar

from .exceptions import InputNotIterableError, EmptyIterableError

T = TypeVar('T')


def last_iterator(tail_iterator: Iterator[T], head_item: T) -> T:
    last_item: T = head_item

    for next_item in tail_iterator:
        last_item = next_item

    return last_item


def last(iterable: Iterable[T]) -> T:
    try:
        # Sequences can be handled more efficiently than Iterables
        # noinspection PyUnresolvedReferences
        last_item: T = iterable[-1]
    except (TypeError, IndexError):
        try:
            iterator: Iterator[T] = iter(iterable)
        except TypeError as exception:
            raise InputNotIterableError(f"'{iterable}' is not iterable.") from exception

        try:
            head_item: T = next(iterator)
        except StopIteration as exception:
            raise EmptyIterableError(f"'{iterable}' contains no items.") from exception
        else:
            last_item: T = last_iterator(tail_iterator=iterator, head_item=head_item)

    return last_item
