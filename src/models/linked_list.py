"""Модуль кольцевого двусвязного списка и узла списка"""

from collections.abc import Iterator
from typing import Any, Optional


class LinkedListItem:
    """Узел связного списка"""

    def __init__(self, data: Any = None) -> None:
        """Инициализация узла"""
        self.data: Any = data
        self._next_item: LinkedListItem | None = None
        self._previous_item: LinkedListItem | None = None

    @property
    def next_item(self) -> Optional["LinkedListItem"]:
        """Получение следующего элемента"""
        return self._next_item

    @next_item.setter
    def next_item(self, value: Optional["LinkedListItem"]) -> None:
        """Установка следующего элемента"""
        if self._next_item is value:
            return
        old_next = self._next_item
        self._next_item = value
        if old_next is not None and old_next.previous_item is self:
            old_next._previous_item = None
        if value is not None and value.previous_item is not self:
            value._previous_item = self

    @property
    def previous_item(self) -> Optional["LinkedListItem"]:
        """Получение предыдущего элемента"""
        return self._previous_item

    @previous_item.setter
    def previous_item(self, value: Optional["LinkedListItem"]) -> None:
        """Установка предыдущего элемента"""
        if self._previous_item is value:
            return
        old_prev = self._previous_item
        self._previous_item = value
        if old_prev is not None and old_prev.next_item is self:
            old_prev._next_item = None
        if value is not None and value.next_item is not self:
            value._next_item = self

    def __eq__(self, other: object) -> bool:
        """Проверка равенства по значению узла"""
        if isinstance(other, LinkedListItem):
            return self.data == other.data
        return self.data == other

    def __repr__(self) -> str:
        """Строковое представление узла"""
        return f"LinkedListItem({self.data!r})"


class LinkedList:
    """Кольцевой двусвязный список"""

    def __init__(self, first_item: LinkedListItem | None = None) -> None:
        """Инициализация связного списка"""
        self.first_item: LinkedListItem | None = first_item

    @property
    def last(self) -> LinkedListItem | None:
        """Получение последнего элемента списка"""
        if self.first_item is None:
            return None
        if (
            self.first_item.previous_item is not None
            and self.first_item.previous_item.next_item is self.first_item
        ):
            return self.first_item.previous_item
        curr = self.first_item
        while curr.next_item is not None and curr.next_item is not self.first_item:
            curr = curr.next_item
        return curr

    def append_left(self, item: Any) -> None:
        """Добавление элемента в начало списка"""
        node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        if self.first_item is None:
            node.next_item = node
            node.previous_item = node
            self.first_item = node
            return
        last_node = self.last
        node.next_item = self.first_item
        if last_node is not None:
            last_node.next_item = node
        self.first_item = node

    def append_right(self, item: Any) -> None:
        """Добавление элемента в конец списка"""
        node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        if self.first_item is None:
            node.next_item = node
            node.previous_item = node
            self.first_item = node
            return
        last_node = self.last
        if last_node is not None:
            last_node.next_item = node
        node.next_item = self.first_item

    def append(self, item: Any) -> None:
        """Алиас для добавления элемента в конец списка"""
        self.append_right(item)

    def remove(self, item: Any) -> None:
        """Удаление элемента из списка"""
        if self.first_item is None:
            raise ValueError(f"{item} not in list")
        target: LinkedListItem | None = None
        for node in self:
            if node == item or node.data == item or node is item:
                target = node
                break
        if target is None:
            raise ValueError(f"{item} not in list")
        if len(self) == 1:
            self.first_item = None
            target._next_item = None
            target._previous_item = None
            return
        prev_node = target.previous_item
        next_node = target.next_item
        if target is self.first_item:
            self.first_item = next_node
        if prev_node is not None and next_node is not None:
            prev_node.next_item = next_node
        target._next_item = None
        target._previous_item = None

    def insert(self, previous: Any, item: Any) -> None:
        """Вставка элемента после указанного узла"""
        if self.first_item is None:
            raise ValueError(f"{previous} not in list")
        prev_node: LinkedListItem | None = None
        if isinstance(previous, LinkedListItem):
            prev_node = previous
        else:
            for node in self:
                if node == previous or node.data == previous or node is previous:
                    prev_node = node
                    break
        if prev_node is None:
            raise ValueError(f"{previous} not in list")
        node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        next_node = prev_node.next_item
        prev_node.next_item = node
        node.next_item = next_node

    def __len__(self) -> int:
        """Вычисление длины списка"""
        if self.first_item is None:
            return 0
        count = 1
        curr = self.first_item
        while curr.next_item is not None and curr.next_item is not self.first_item:
            count += 1
            curr = curr.next_item
        return count

    def __iter__(self) -> Iterator[LinkedListItem]:
        """Итератор по элементам списка"""
        if self.first_item is None:
            return
        curr = self.first_item
        while True:
            yield curr
            curr = curr.next_item
            if curr is None or curr is self.first_item:
                break

    def __getitem__(self, index: int) -> LinkedListItem:
        """Получение элемента по индексу"""
        total = len(self)
        if total == 0:
            raise IndexError("Index out of range")
        if index < 0:
            index = total + index
        if index < 0 or index >= total:
            raise IndexError("Index out of range")
        curr = self.first_item
        for _ in range(index):
            if curr is not None:
                curr = curr.next_item
        if curr is None:
            raise IndexError("Index out of range")
        return curr

    def __contains__(self, item: Any) -> bool:
        """Проверка наличия элемента в списке"""
        if self.first_item is None:
            return False
        return any(node == item or node.data == item or node is item for node in self)

    def __reversed__(self) -> Iterator[LinkedListItem]:
        """Итератор по элементам списка в обратном порядке"""
        if self.first_item is None:
            return
        curr = self.last
        for _ in range(len(self)):
            if curr is not None:
                yield curr
                curr = curr.previous_item
