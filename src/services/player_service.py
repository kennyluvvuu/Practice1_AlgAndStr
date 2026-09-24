"""Сервис приложения плеера, связывающий модель связного списка и аудиодвижок"""

import os

import pygame

from src.models import Composition, PlayList


class PlayerService:
    """Управление состоянием плейлистов и воспроизведением аудио через pygame.mixer"""

    def __init__(self) -> None:
        """Инициализация сервиса и аудиоподсистемы"""
        self.playlists: dict[str, PlayList] = {}
        self.active_playlist_name: str | None = None
        self.selected_track_index: int | None = None
        self._is_paused: bool = False
        self._volume: float = 0.7
        self._initialized: bool = False

        self._init_audio()
        self._init_default_playlist()

    def _init_audio(self) -> None:
        """Инициализация pygame.mixer с защитой от сбоев CoreAudio"""
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self._volume)
            self._initialized = True
        except (pygame.error, Exception):
            self._initialized = False

    def _init_default_playlist(self) -> None:
        """Создание начального плейлиста по умолчанию"""
        default_pl = PlayList("main")
        self.playlists[default_pl.name] = default_pl
        self.active_playlist_name = default_pl.name

    def get_active_playlist(self) -> PlayList | None:
        """Получение текущего активного плейлиста"""
        if self.active_playlist_name is not None:
            return self.playlists.get(self.active_playlist_name)
        return None

    def create_playlist(self, name: str) -> bool:
        """Создание нового плейлиста"""
        clean_name = name.strip()
        if not clean_name or clean_name in self.playlists:
            return False
        self.playlists[clean_name] = PlayList(clean_name)
        self.switch_playlist(clean_name)
        return True

    def delete_playlist(self, name: str) -> bool:
        """Удаление плейлиста"""
        if len(self.playlists) <= 1 or name not in self.playlists:
            return False
        del self.playlists[name]
        if self.active_playlist_name == name:
            self.active_playlist_name = next(iter(self.playlists))
            self.selected_track_index = None
        return True

    def switch_playlist(self, name: str) -> None:
        """Переключение активного плейлиста"""
        if name in self.playlists:
            self.active_playlist_name = name
            self.selected_track_index = None

    def add_track_file(self, file_path: str) -> Composition | None:
        """Добавление аудиофайла в активный плейлист"""
        playlist = self.get_active_playlist()
        if playlist is None or not os.path.exists(file_path):
            return None
        filename = os.path.basename(file_path)
        title, _ = os.path.splitext(filename)
        track = Composition(title=title, path=file_path)
        playlist.append(track)
        return track

    def add_tracks_from_directory(self, dir_path: str, extensions: list[str]) -> int:
        """Добавление всех поддерживаемых файлов из каталога"""
        playlist = self.get_active_playlist()
        if playlist is None or not os.path.isdir(dir_path):
            return 0
        added = 0
        ext_set = set(extensions)
        for entry in sorted(os.listdir(dir_path)):
            ext = os.path.splitext(entry)[1].lower()
            if ext in ext_set:
                full_path = os.path.join(dir_path, entry)
                title, _ = os.path.splitext(entry)
                playlist.append(Composition(title=title, path=full_path))
                added += 1
        return added

    def remove_track(self, index: int) -> bool:
        """Удаление трека по индексу"""
        playlist = self.get_active_playlist()
        if playlist is None or index < 0 or index >= len(playlist):
            return False
        node_to_del = playlist[index]
        if playlist.current is node_to_del:
            self.stop()
        playlist.remove(node_to_del)
        if len(playlist) == 0:
            self.selected_track_index = None
        elif self.selected_track_index is not None and self.selected_track_index >= len(
            playlist
        ):
            self.selected_track_index = len(playlist) - 1
        return True

    def move_track(self, from_index: int, to_index: int) -> bool:
        """Перемещение трека на новую позицию"""
        playlist = self.get_active_playlist()
        if playlist is None or len(playlist) <= 1:
            return False
        try:
            playlist.move_track(from_index, to_index)
            self.selected_track_index = to_index
            return True
        except IndexError:
            return False

    def play_track(self, index: int | None = None) -> bool:
        """Воспроизведение трека по индексу или текущего"""
        playlist = self.get_active_playlist()
        if playlist is None or len(playlist) == 0:
            return False
        if index is not None:
            self.selected_track_index = index
            playlist.play_all(index)
        elif playlist.current is None:
            playlist.play_all()

        current_node = playlist.current
        if current_node is None:
            return False
        track: Composition = current_node.data
        if not track.path or not os.path.exists(track.path):
            return False

        if not self._initialized:
            self._init_audio()
        try:
            pygame.mixer.music.load(track.path)
            pygame.mixer.music.play()
            self._is_paused = False
            return True
        except (pygame.error, Exception):
            return False

    def toggle_play(self) -> bool:
        """Переключение состояния пауза/воспроизведение"""
        if self._is_paused:
            if self._initialized:
                try:
                    pygame.mixer.music.unpause()
                except (pygame.error, Exception):
                    pass
            self._is_paused = False
            return True
        if self.is_playing():
            if self._initialized:
                try:
                    pygame.mixer.music.pause()
                except (pygame.error, Exception):
                    pass
            self._is_paused = True
            return False
        return self.play_track(self.selected_track_index)

    def next_track(self) -> bool:
        """Переход к следующему треку"""
        playlist = self.get_active_playlist()
        if playlist is None or len(playlist) == 0:
            return False
        playlist.next_track()
        if playlist.current is not None:
            self.selected_track_index = None
            for idx, node in enumerate(playlist):
                if node is playlist.current:
                    self.selected_track_index = idx
                    break
        return self.play_track()

    def previous_track(self) -> bool:
        """Переход к предыдущему треку"""
        playlist = self.get_active_playlist()
        if playlist is None or len(playlist) == 0:
            return False
        playlist.previous_track()
        if playlist.current is not None:
            self.selected_track_index = None
            for idx, node in enumerate(playlist):
                if node is playlist.current:
                    self.selected_track_index = idx
                    break
        return self.play_track()

    def stop(self) -> None:
        """Остановка воспроизведения"""
        if self._initialized:
            try:
                pygame.mixer.music.stop()
            except (pygame.error, Exception):
                pass
        self._is_paused = False

    def is_playing(self) -> bool:
        """Проверка активности проигрывания"""
        if not self._initialized:
            return False
        try:
            return bool(pygame.mixer.music.get_busy()) and not self._is_paused
        except (pygame.error, Exception):
            return False

    def is_paused(self) -> bool:
        """Проверка статуса паузы"""
        return self._is_paused

    def get_volume(self) -> float:
        """Получение текущего уровня громкости"""
        return self._volume

    def set_volume(self, val: float) -> None:
        """Установка уровня громкости"""
        self._volume = max(0.0, min(1.0, val))
        if self._initialized:
            try:
                pygame.mixer.music.set_volume(self._volume)
            except (pygame.error, Exception):
                pass

    def get_now_playing(self) -> Composition | None:
        """Получение текущей играющей композиции"""
        playlist = self.get_active_playlist()
        if playlist is not None and playlist.current is not None:
            return playlist.current.data
        return None

    def check_auto_advance(self, was_playing: bool) -> bool:
        """Автоматический переход к следующему треку при окончании текущего"""
        if was_playing and not self.is_playing() and not self._is_paused:
            self.next_track()
            return True
        return False
