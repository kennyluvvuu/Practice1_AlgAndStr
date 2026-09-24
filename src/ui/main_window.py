"""Главное окно приложения, объединяющее компоненты интерфейса и сервис"""

import os
from tkinter import filedialog

import customtkinter as ctk

from src.services import PlayerService
from src.ui.bottom_bar import BottomBarView
from src.ui.constants import AUDIO_EXTENSIONS, COLOR_BG_DARK
from src.ui.sidebar import SidebarView
from src.ui.toolbar import ToolbarView
from src.ui.track_list import TrackListView


class MusicPlayerApp(ctk.CTk):
    """Главное окно приложения плеера, координирующее View и Service"""

    def __init__(self) -> None:
        """Инициализация главного окна и компонентов"""
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.title("player")
        self.geometry("1120x680")
        self.minsize(940, 560)

        self.service: PlayerService = PlayerService()

        self.sidebar: SidebarView | None = None
        self.toolbar: ToolbarView | None = None
        self.track_list: TrackListView | None = None
        self.bottom_bar: BottomBarView | None = None

        self._build_ui()
        self._refresh_all()
        self._start_poll_loop()

    def _build_ui(self) -> None:
        """Сборка панелей интерфейса"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = SidebarView(
            master=self,
            on_select_playlist=self._on_switch_playlist,
            on_create_playlist=self._on_create_playlist,
            on_delete_playlist=self._on_delete_playlist,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        main_panel = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_BG_DARK)
        main_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        main_panel.grid_rowconfigure(1, weight=1)
        main_panel.grid_columnconfigure(0, weight=1)

        self.toolbar = ToolbarView(
            master=main_panel,
            on_add_files=self._on_add_files_dialog,
            on_add_folder=self._on_add_folder_dialog,
            on_add_path=self._on_add_path,
            on_remove_track=self._on_remove_track,
            on_move_up=self._on_move_up,
            on_move_down=self._on_move_down,
        )
        self.toolbar.pack(fill="x")

        self.track_list = TrackListView(
            master=main_panel,
            on_select_track=self._on_select_track,
            on_play_track=self._on_play_track,
            on_move_track=self._on_move_track,
        )
        self.track_list.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.bottom_bar = BottomBarView(
            master=self,
            on_prev=self._on_prev,
            on_toggle_play=self._on_toggle_play,
            on_next=self._on_next,
            on_volume_change=self._on_volume_change,
            initial_volume=self.service.get_volume(),
        )
        self.bottom_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _refresh_all(self) -> None:
        """Синхронизация всех представлений с состоянием модели через сервис"""
        playlist = self.service.get_active_playlist()
        playlists_names = list(self.service.playlists.keys())
        active_name = self.service.active_playlist_name

        if self.sidebar is not None:
            self.sidebar.refresh_playlists(playlists_names, active_name)

        if self.toolbar is not None:
            total = len(playlist) if playlist is not None else 0
            title_text = f"{active_name} [{total}]" if active_name else "no playlists"
            self.toolbar.set_title(title_text)

        if self.track_list is not None:
            is_busy = self.service.is_playing() or self.service.is_paused()
            self.track_list.refresh_tracks(
                playlist=playlist,
                selected_index=self.service.selected_track_index,
                is_busy=is_busy,
            )

        self._update_player_display()

    def _update_player_display(self) -> None:
        """Обновление нижней панели управления"""
        now_playing = self.service.get_now_playing()
        is_playing = self.service.is_playing()
        if self.bottom_bar is not None:
            if now_playing is not None:
                artist = now_playing.artist or "local file"
                self.bottom_bar.set_track_info(now_playing.title, artist, is_playing)
            else:
                self.bottom_bar.set_track_info("no track selected", "", False)

    def _on_switch_playlist(self, name: str) -> None:
        """Смена активного плейлиста"""
        self.service.switch_playlist(name)
        self._refresh_all()

    def _on_create_playlist(self, name: str) -> None:
        """Создание нового плейлиста"""
        if self.service.create_playlist(name):
            if self.toolbar is not None:
                self.toolbar.set_status(f"created playlist: {name}")
            self._refresh_all()

    def _on_delete_playlist(self) -> None:
        """Удаление активного плейлиста"""
        current_name = self.service.active_playlist_name
        if current_name is not None and self.service.delete_playlist(current_name):
            if self.toolbar is not None:
                self.toolbar.set_status(f"deleted playlist: {current_name}")
            self._refresh_all()
        elif self.toolbar is not None:
            self.toolbar.set_status("cannot delete last playlist")

    def _on_add_files_dialog(self) -> None:
        """Диалог выбора файлов"""
        try:
            raw = filedialog.askopenfilenames(title="select audio files")
            paths = list(self.tk.splitlist(raw)) if isinstance(raw, str) else list(raw)
        except Exception:
            paths = []
        added = 0
        for path in paths:
            if self.service.add_track_file(path) is not None:
                added += 1
        if added > 0:
            if self.toolbar is not None:
                self.toolbar.set_status(f"added {added} files")
            self._refresh_all()

    def _on_add_folder_dialog(self) -> None:
        """Диалог выбора папки"""
        try:
            folder = filedialog.askdirectory(title="select music folder")
        except Exception:
            folder = ""
        if folder and os.path.exists(folder):
            added = self.service.add_tracks_from_directory(
                folder,
                list(AUDIO_EXTENSIONS),
            )
            if self.toolbar is not None:
                self.toolbar.set_status(f"added {added} tracks from folder")
            self._refresh_all()

    def _on_add_path(self, raw_path: str) -> None:
        """Добавление файлов или папки по введённому пути"""
        cleaned = os.path.expanduser(raw_path.strip("'\""))
        if not os.path.exists(cleaned):
            if self.toolbar is not None:
                self.toolbar.set_status("path not found")
            return
        if os.path.isdir(cleaned):
            added = self.service.add_tracks_from_directory(
                cleaned,
                list(AUDIO_EXTENSIONS),
            )
            if self.toolbar is not None:
                self.toolbar.set_status(f"added {added} tracks from folder")
        else:
            track = self.service.add_track_file(cleaned)
            if self.toolbar is not None and track is not None:
                self.toolbar.set_status(f"added: {track.title}")
        if self.toolbar is not None:
            self.toolbar.clear_path_entry()
        self._refresh_all()

    def _on_remove_track(self) -> None:
        """Удаление выбранного трека"""
        idx = self.service.selected_track_index
        if idx is not None and self.service.remove_track(idx):
            if self.toolbar is not None:
                self.toolbar.set_status("track removed")
            self._refresh_all()

    def _on_move_up(self) -> None:
        """Перемещение трека вверх"""
        idx = self.service.selected_track_index
        if idx is not None and idx > 0 and self.service.move_track(idx, idx - 1):
            self._refresh_all()

    def _on_move_down(self) -> None:
        """Перемещение трека вниз"""
        idx = self.service.selected_track_index
        playlist = self.service.get_active_playlist()
        if (
            idx is not None
            and playlist is not None
            and idx < len(playlist) - 1
            and self.service.move_track(idx, idx + 1)
        ):
            self._refresh_all()

    def _on_select_track(self, index: int) -> None:
        """Выбор трека в списке"""
        self.service.selected_track_index = index
        if self.track_list is not None:
            self.track_list.set_selected(index)

    def _on_play_track(self, index: int) -> None:
        """Воспроизведение трека по клику"""
        self.service.play_track(index)
        self._refresh_all()

    def _on_move_track(self, from_index: int, to_index: int) -> None:
        """Перемещение трека при Drag-and-Drop"""
        if self.service.move_track(from_index, to_index):
            self._refresh_all()

    def _on_toggle_play(self) -> None:
        """Переключение воспроизведение/пауза"""
        self.service.toggle_play()
        self._refresh_all()

    def _on_next(self) -> None:
        """Следующий трек"""
        self.service.next_track()
        self._refresh_all()

    def _on_prev(self) -> None:
        """Предыдущий трек"""
        self.service.previous_track()
        self._refresh_all()

    def _on_volume_change(self, val: float) -> None:
        """Регулировка громкости"""
        self.service.set_volume(val)

    def _start_poll_loop(self) -> None:
        """Проверка авто-перехода к следующему треку"""
        if self.bottom_bar is not None and self.bottom_bar.play_btn is not None:
            was_playing = self.bottom_bar.play_btn.cget("text") == "pause"
            if self.service.check_auto_advance(was_playing):
                self._refresh_all()
        self.after(500, self._start_poll_loop)
