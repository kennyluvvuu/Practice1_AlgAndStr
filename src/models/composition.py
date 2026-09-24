"""Модель музыкальной композиции с метаданными трека"""


class Composition:
    """Музыкальная композиция"""

    def __init__(
        self,
        title: str,
        artist: str = "",
        duration: int = 0,
        path: str = "",
    ) -> None:
        """Инициализация музыкальной композиции"""
        self.title: str = title
        self.artist: str = artist
        self.duration: int = duration
        self.path: str = path

    def __repr__(self) -> str:
        """Строковое представление композиции для отладки"""
        return f"Composition({self.title!r}, {self.artist!r})"

    def __str__(self) -> str:
        """Строковое представление композиции для пользователя"""
        if self.artist:
            return f"{self.artist} - {self.title}"
        return self.title

    def __eq__(self, other: object) -> bool:
        """Сравнение композиций"""
        if isinstance(other, Composition):
            return self.path == other.path and self.title == other.title
        if isinstance(other, str):
            return self.title == other or str(self) == other
        return False
