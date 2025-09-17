from typing import Iterable, Iterator, TypeVar

from .exceptions import InputNotIterableError

T = TypeVar('T')


def init_iterator(tail_iterator: Iterator[T], head_item: T) -> Iterator[T]:
    while True:
        try:
            next_item: T = next(tail_iterator)
        except StopIteration:
            break
        else:
            yield head_item
            head_item = next_item


def init(iterable: Iterable[T]) -> Iterator[T]:
    try:
        # Sequences can be handled more efficiently than Iterables
        # noinspection PyUnresolvedReferences
        init_items: Iterator[T] = iter(iterable[:-1])
    except TypeError:
        try:
            iterator: Iterator[T] = iter(iterable)
        except TypeError as exception:
            raise InputNotIterableError(f"'{iterable}' is not iterable.") from exception

        try:
            head_item: T = next(iterator)
        except StopIteration:
            init_items: Iterator[T] = iter(())
        else:
            init_items: Iterator[T] = init_iterator(tail_iterator=iterator, head_item=head_item)

    return init_items
