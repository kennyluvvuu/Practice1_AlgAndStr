"""Модель плейлиста, расширяющая кольцевой двусвязный список"""

from src.models.composition import Composition
from src.models.linked_list import LinkedList, LinkedListItem


class PlayList(LinkedList):
    """Плейлист на базе связного списка"""

    def __init__(
        self, name: str = "Default", first_item: LinkedListItem | None = None
    ) -> None:
        """Инициализация плейлиста"""
        super().__init__(first_item)
        self.name: str = name
        self._current: LinkedListItem | None = first_item

    @property
    def current(self) -> LinkedListItem | None:
        """Получение текущего трека"""
        return self._current

    def play_all(
        self,
        item: LinkedListItem | Composition | int | None = None,
    ) -> LinkedListItem | None:
        """Запуск проигрывания треков начиная с указанного"""
        if self.first_item is None:
            self._current = None
            return None
        if item is None:
            self._current = self.first_item
        elif isinstance(item, int):
            self._current = self[item]
        elif isinstance(item, LinkedListItem):
            self._current = item
        else:
            found = None
            for node in self:
                if node.data == item:
                    found = node
                    break
            self._current = found if found is not None else self.first_item
        return self._current

    def next_track(self) -> LinkedListItem | None:
        """Переход к следующему треку"""
        if self.first_item is None:
            self._current = None
            return None
        if self._current is None:
            self._current = self.first_item
        else:
            self._current = self._current.next_item
        return self._current

    def previous_track(self) -> LinkedListItem | None:
        """Переход к предыдущему треку"""
        if self.first_item is None:
            self._current = None
            return None
        if self._current is None:
            self._current = self.last
        else:
            self._current = self._current.previous_item
        return self._current

    def move_track(self, from_index: int, to_index: int) -> None:
        """Перемещение трека с одной позиции на другую"""
        total = len(self)
        if total <= 1 or from_index == to_index:
            return
        if from_index < 0 or from_index >= total or to_index < 0 or to_index >= total:
            raise IndexError("Index out of range")
        node_to_move = self[from_index]
        was_current = self._current is node_to_move
        self.remove(node_to_move)
        if to_index == 0:
            self.append_left(node_to_move)
        elif to_index >= len(self):
            self.append_right(node_to_move)
        else:
            prev_node = self[to_index - 1]
            self.insert(prev_node, node_to_move)
        if was_current:
            self._current = node_to_move
