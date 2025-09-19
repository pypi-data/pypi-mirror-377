from collections.abc import MutableSet
from itertools import chain
from typing import AbstractSet, Any, Generic, Iterable, Literal, Optional, TypeVar

T = TypeVar('T')

NIL = 0


def _map(iterable: Iterable[T]) -> Iterable[tuple[T, Literal[0]]]:
    return map(lambda x: (x, NIL), iterable)


class OrderedSet(Generic[T], MutableSet, AbstractSet[T]):
    def __init__(self, iterable: Optional[Iterable[T]] = None):
        # NOTE: A dictionary guarantees iteration order to be insertion order since
        # Python 3.6 in CPython and since Python 3.7 for all compliant
        # implementations. This implementation tries to work with these version
        # constraints.
        self._dict: dict[T, Literal[0]] = {} if iterable is None else dict(_map(iterable))

    # NOTE: The following are required by the MutableSet ABC

    def __contains__(self, key: Any):
        return key in self._dict

    def __iter__(self):
        # NOTE: This follows insertion order
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def add(self, value: T):
        self._dict[value] = NIL

    def discard(self, value: T):
        self._dict.pop(value, NIL)

    # NOTE: The following are required by the ordered nature of OrderedSet

    def __reversed__(self):
        return reversed(self._dict.keys())

    def pop(self):
        return self._dict.popitem()[0]

    # NOTE: The following are only required if performance matters

    def remove(self, value: T):
        del self._dict[value]

    def clear(self):
        self._dict.clear()

    # NOTE: The following mimic the behavior of native sets

    def update(self, *iterables: Iterable[T]):
        self._dict.update(_map(chain(*iterables)))

    def copy(self):
        return OrderedSet(self)

    def __repr__(self):
        c = self.__class__.__name__
        if self:
            return f'{c}(%r)' % (list(self),)
        return f'{c}()'
