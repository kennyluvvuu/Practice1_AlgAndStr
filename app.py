"""Модуль графического интерфейса аудиоплеера на CustomTkinter в монохромной теме"""

import os
import platform
import subprocess
from typing import Dict, List, Optional
from tkinter import filedialog, Event
import customtkinter as ctk

from src.models.linked_list import Composition, LinkedListItem, PlayList
from audio_player import AudioPlayer

FONT_NAME = "Iosevka Nerd Font"


def pick_files_macos() -> Optional[List[str]]:
    """Нативный диалог выбора файлов для macOS через AppleScript"""
    script = (
        'tell application "System Events"\n'
        "activate\n"
        'set fileList to choose file with prompt "Select audio files:" '
        "with multiple selections allowed\n"
        "set posixList to {}\n"
        "repeat with aFile in fileList\n"
        "set end of posixList to POSIX path of aFile\n"
        "end repeat\n"
        "set AppleScript's text item delimiters to linefeed\n"
        "return posixList as text\n"
        "end tell"
    )
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return [
            line.strip() for line in result.stdout.strip().split("\n") if line.strip()
        ]
    if result.returncode != 0 and (
        "User canceled" in result.stderr or "-128" in result.stderr
    ):
        return []
    return None


def pick_folder_macos() -> Optional[str]:
    """Нативный диалог выбора папки для macOS через AppleScript"""
    script = (
        'tell application "System Events"\n'
        "activate\n"
        'set aFolder to choose folder with prompt "Select music folder:"\n'
        "return POSIX path of aFolder\n"
        "end tell"
    )
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    if result.returncode != 0 and (
        "User canceled" in result.stderr or "-128" in result.stderr
    ):
        return ""
    return None


class MusicPlayerApp(ctk.CTk):
    """Главное окно приложения музыкального плеера"""

    def __init__(self) -> None:
        """Инициализация окна и компонентов приложения"""
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.title("player")
        self.geometry("1060x680")
        self.minsize(900, 560)

        self.player: AudioPlayer = AudioPlayer()
        self.playlists: Dict[str, PlayList] = {}
        self.active_playlist_name: Optional[str] = None
        self.selected_track_index: Optional[int] = None
        self.drag_start_index: Optional[int] = None

        self._track_row_frames: List[ctk.CTkFrame] = []
        self._playlist_buttons: Dict[str, ctk.CTkButton] = {}

        self.sidebar_frame: Optional[ctk.CTkFrame] = None
        self.playlist_scroll: Optional[ctk.CTkScrollableFrame] = None
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.playlist_title_label: Optional[ctk.CTkLabel] = None
        self.tracks_scroll: Optional[ctk.CTkScrollableFrame] = None
        self.bottom_frame: Optional[ctk.CTkFrame] = None
        self.track_info_frame: Optional[ctk.CTkFrame] = None
        self.now_playing_title: Optional[ctk.CTkLabel] = None
        self.now_playing_artist: Optional[ctk.CTkLabel] = None
        self.play_btn: Optional[ctk.CTkButton] = None
        self.vol_slider: Optional[ctk.CTkSlider] = None

        self._init_data()
        self._build_ui()
        self._refresh_playlists_ui()
        self._refresh_tracks_ui()
        self._start_poll_loop()

    def _init_data(self) -> None:
        """Создание начального плейлиста"""
        default_pl = PlayList("main")
        self.playlists[default_pl.name] = default_pl
        self.active_playlist_name = default_pl.name

    def _build_ui(self) -> None:
        """Построение сетки интерфейса"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main_panel()
        self._build_bottom_bar()

    def _build_sidebar(self) -> None:
        """Построение боковой панели управления плейлистами"""
        self.sidebar_frame = ctk.CTkFrame(
            self, width=230, corner_radius=0, fg_color="#101012"
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        app_title = ctk.CTkLabel(
            self.sidebar_frame,
            text="player",
            font=ctk.CTkFont(family=FONT_NAME, size=20, weight="bold"),
            text_color="#f4f4f5",
        )
        app_title.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="w")

        btn_box = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        btn_box.grid(row=1, column=0, padx=16, pady=4, sticky="ew")

        add_pl_btn = ctk.CTkButton(
            btn_box,
            text="+ playlist",
            width=100,
            height=30,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color="#18181b",
            text_color="#f4f4f5",
            border_width=1,
            border_color="#27272a",
            hover_color="#27272a",
            command=self._on_create_playlist,
        )
        add_pl_btn.pack(side="left", padx=(0, 6))

        del_pl_btn = ctk.CTkButton(
            btn_box,
            text="delete",
            width=85,
            height=30,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color="#18181b",
            text_color="#a1a1aa",
            border_width=1,
            border_color="#27272a",
            hover_color="#27272a",
            command=self._on_delete_playlist,
        )
        del_pl_btn.pack(side="left")

        self.playlist_scroll = ctk.CTkScrollableFrame(
            self.sidebar_frame,
            label_text="playlists",
            label_font=ctk.CTkFont(family=FONT_NAME, size=12, weight="bold"),
            label_text_color="#71717a",
            fg_color="transparent",
        )
        self.playlist_scroll.grid(row=2, column=0, padx=12, pady=(8, 16), sticky="nsew")

    def _build_main_panel(self) -> None:
        """Построение центральной области списка треков"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#09090b")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        title_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_bar.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))

        self.playlist_title_label = ctk.CTkLabel(
            title_bar,
            text="main [0]",
            font=ctk.CTkFont(family=FONT_NAME, size=20, weight="bold"),
            text_color="#f4f4f5",
        )
        self.playlist_title_label.pack(side="left")

        toolbar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))

        add_files_btn = ctk.CTkButton(
            toolbar,
            text="add files",
            width=100,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color="#ededed",
            text_color="#09090b",
            hover_color="#ffffff",
            command=self._on_add_tracks,
        )
        add_files_btn.pack(side="left", padx=(0, 8))

        add_folder_btn = ctk.CTkButton(
            toolbar,
            text="add folder",
            width=105,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color="#18181b",
            text_color="#ededed",
            border_width=1,
            border_color="#27272a",
            hover_color="#27272a",
            command=self._on_add_folder,
        )
        add_folder_btn.pack(side="left", padx=(0, 8))

        add_path_btn = ctk.CTkButton(
            toolbar,
            text="+ path",
            width=80,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color="#18181b",
            text_color="#ededed",
            border_width=1,
            border_color="#27272a",
            hover_color="#27272a",
            command=self._on_add_path_dialog,
        )
        add_path_btn.pack(side="left", padx=(0, 8))

        del_track_btn = ctk.CTkButton(
            toolbar,
            text="remove track",
            width=115,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color="#18181b",
            text_color="#ededed",
            border_width=1,
            border_color="#27272a",
            hover_color="#27272a",
            command=self._on_remove_track,
        )
        del_track_btn.pack(side="left", padx=(0, 16))

        order_label = ctk.CTkLabel(
            toolbar,
            text="order:",
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            text_color="#71717a",
        )
        order_label.pack(side="left", padx=(0, 6))

        move_up_btn = ctk.CTkButton(
            toolbar,
            text="up",
            width=65,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color="#18181b",
            text_color="#ededed",
            border_width=1,
            border_color="#27272a",
            hover_color="#27272a",
            command=self._on_move_up,
        )
        move_up_btn.pack(side="left", padx=(0, 6))

        move_down_btn = ctk.CTkButton(
            toolbar,
            text="down",
            width=65,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color="#18181b",
            text_color="#ededed",
            border_width=1,
            border_color="#27272a",
            hover_color="#27272a",
            command=self._on_move_down,
        )
        move_down_btn.pack(side="left")

        self.tracks_scroll = ctk.CTkScrollableFrame(
            self.main_frame, fg_color="transparent"
        )
        self.tracks_scroll.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self.tracks_scroll.grid_columnconfigure(0, weight=1)

    def _build_bottom_bar(self) -> None:
        """Построение нижней панели управления воспроизведением"""
        self.bottom_frame = ctk.CTkFrame(
            self, height=90, corner_radius=0, fg_color="#101012"
        )
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=2)
        self.bottom_frame.grid_columnconfigure(2, weight=1)

        self.track_info_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.track_info_frame.grid(row=0, column=0, sticky="w", padx=24, pady=12)

        self.now_playing_title = ctk.CTkLabel(
            self.track_info_frame,
            text="no track selected",
            font=ctk.CTkFont(family=FONT_NAME, size=13, weight="bold"),
            text_color="#f4f4f5",
            anchor="w",
        )
        self.now_playing_title.pack(anchor="w")

        self.now_playing_artist = ctk.CTkLabel(
            self.track_info_frame,
            text="",
            font=ctk.CTkFont(family=FONT_NAME, size=11),
            text_color="#71717a",
            anchor="w",
        )
        self.now_playing_artist.pack(anchor="w")

        controls_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=1, pady=12)

        buttons_box = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_box.pack()

        prev_btn = ctk.CTkButton(
            buttons_box,
            text="prev",
            width=65,
            height=36,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color="#18181b",
            text_color="#ededed",
            border_width=1,
            border_color="#27272a",
            hover_color="#27272a",
            command=self._on_prev_track,
        )
        prev_btn.pack(side="left", padx=6)

        self.play_btn = ctk.CTkButton(
            buttons_box,
            text="play",
            width=110,
            height=36,
            font=ctk.CTkFont(family=FONT_NAME, size=12, weight="bold"),
            fg_color="#ededed",
            text_color="#09090b",
            hover_color="#ffffff",
            command=self._on_toggle_play,
        )
        self.play_btn.pack(side="left", padx=6)

        next_btn = ctk.CTkButton(
            buttons_box,
            text="next",
            width=65,
            height=36,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color="#18181b",
            text_color="#ededed",
            border_width=1,
            border_color="#27272a",
            hover_color="#27272a",
            command=self._on_next_track,
        )
        next_btn.pack(side="left", padx=6)

        loop_badge = ctk.CTkLabel(
            buttons_box,
            text="[loop: on]",
            font=ctk.CTkFont(family=FONT_NAME, size=11),
            text_color="#71717a",
        )
        loop_badge.pack(side="left", padx=14)

        right_box = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        right_box.grid(row=0, column=2, sticky="e", padx=24, pady=12)

        vol_label = ctk.CTkLabel(
            right_box,
            text="vol:",
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            text_color="#71717a",
        )
        vol_label.pack(side="left", padx=(0, 8))

        self.vol_slider = ctk.CTkSlider(
            right_box,
            from_=0.0,
            to=1.0,
            width=110,
            button_color="#ededed",
            button_hover_color="#ffffff",
            progress_color="#52525b",
            fg_color="#27272a",
            command=self._on_volume_change,
        )
        self.vol_slider.set(self.player.volume)
        self.vol_slider.pack(side="left")

    def _refresh_playlists_ui(self) -> None:
        """Обновление списка плейлистов в боковой панели"""
        for btn in self._playlist_buttons.values():
            btn.destroy()
        self._playlist_buttons.clear()

        for name in self.playlists:
            is_active = name == self.active_playlist_name
            color = "#27272a" if is_active else "transparent"
            hover = "#3f3f46" if is_active else "#18181b"
            text_color = "#ffffff" if is_active else "#a1a1aa"
            btn = ctk.CTkButton(
                self.playlist_scroll,
                text=name,
                anchor="w",
                font=ctk.CTkFont(family=FONT_NAME, size=12),
                fg_color=color,
                text_color=text_color,
                hover_color=hover,
                height=32,
                command=lambda n=name: self._switch_playlist(n),
            )
            btn.pack(fill="x", pady=2)
            self._playlist_buttons[name] = btn

    def _switch_playlist(self, name: str) -> None:
        """Переключение на другой плейлист"""
        if name in self.playlists:
            self.active_playlist_name = name
            self.selected_track_index = None
            self._refresh_playlists_ui()
            self._refresh_tracks_ui()

    def _on_create_playlist(self) -> None:
        """Создание нового плейлиста"""
        dialog = ctk.CTkInputDialog(text="playlist name:", title="new playlist")
        name = dialog.get_input()
        if name and name.strip():
            name = name.strip()
            if name not in self.playlists:
                self.playlists[name] = PlayList(name)
                self._switch_playlist(name)

    def _on_delete_playlist(self) -> None:
        """Удаление активного плейлиста"""
        if len(self.playlists) <= 1:
            return
        if self.active_playlist_name and self.active_playlist_name in self.playlists:
            del self.playlists[self.active_playlist_name]
            self.active_playlist_name = next(iter(self.playlists))
            self.selected_track_index = None
            self._refresh_playlists_ui()
            self._refresh_tracks_ui()

    def _get_active_playlist(self) -> Optional[PlayList]:
        """Получение текущего активного плейлиста"""
        if self.active_playlist_name:
            return self.playlists.get(self.active_playlist_name)
        return None

    def _refresh_tracks_ui(self) -> None:
        """Отрисовка списка треков активного плейлиста"""
        for frame in self._track_row_frames:
            frame.destroy()
        self._track_row_frames.clear()

        playlist = self._get_active_playlist()
        if not playlist:
            if self.playlist_title_label:
                self.playlist_title_label.configure(text="no playlists")
            return

        total_tracks = len(playlist)
        if self.playlist_title_label:
            self.playlist_title_label.configure(
                text=f"{playlist.name} [{total_tracks}]"
            )

        for idx, node in enumerate(playlist):
            self._create_track_row(idx, node, playlist)

    def _create_track_row(
        self, idx: int, node: LinkedListItem, playlist: PlayList
    ) -> None:
        """Создание виджета строки одного трека с поддержкой Drag-and-Drop"""
        is_playing = playlist.current is node and self.player.is_busy()
        is_selected = self.selected_track_index == idx

        bg_color = (
            "#27272a" if is_selected else ("#1c1c20" if is_playing else "#121214")
        )
        row = ctk.CTkFrame(
            self.tracks_scroll,
            fg_color=bg_color,
            corner_radius=4,
            height=40,
        )
        row.pack(fill="x", pady=2, padx=2)
        row.pack_propagate(False)

        drag_icon = ctk.CTkLabel(
            row,
            text="::",
            width=24,
            font=ctk.CTkFont(family=FONT_NAME, size=13, weight="bold"),
            text_color="#52525b",
        )
        drag_icon.pack(side="left", padx=(10, 4))

        num_lbl = ctk.CTkLabel(
            row,
            text=f"{idx + 1:02d}",
            width=28,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            text_color="#71717a",
        )
        num_lbl.pack(side="left")

        title = str(node.data)
        title_lbl = ctk.CTkLabel(
            row,
            text=title,
            anchor="w",
            font=ctk.CTkFont(
                family=FONT_NAME,
                size=12,
                weight="bold" if is_playing else "normal",
            ),
            text_color="#ffffff" if is_playing else "#d4d4d8",
        )
        title_lbl.pack(side="left", padx=12, fill="x", expand=True)

        status_lbl = ctk.CTkLabel(
            row,
            text="[playing]" if is_playing else "",
            text_color="#ededed",
            font=ctk.CTkFont(family=FONT_NAME, size=11),
        )
        status_lbl.pack(side="right", padx=16)

        for widget in (row, drag_icon, num_lbl, title_lbl, status_lbl):
            widget.bind("<Button-1>", lambda _e, i=idx: self._on_track_click(i))
            widget.bind(
                "<Double-Button-1>", lambda _e, i=idx: self._on_track_double_click(i)
            )
            widget.bind("<B1-Motion>", lambda _e, i=idx: self._on_track_drag(_e, i))
            widget.bind(
                "<ButtonRelease-1>", lambda _e, i=idx: self._on_track_drop(_e, i)
            )

        self._track_row_frames.append(row)

    def _on_track_click(self, index: int) -> None:
        """Выбор трека в списке"""
        self.selected_track_index = index
        self._refresh_tracks_ui()

    def _on_track_double_click(self, index: int) -> None:
        """Воспроизведение трека по двойному щелчку"""
        playlist = self._get_active_playlist()
        if not playlist or index >= len(playlist):
            return
        self.selected_track_index = index
        playlist.play_all(index)
        self._start_playing_current()

    def _on_track_drag(self, _event: Event, from_index: int) -> None:
        """Обработка процесса перетаскивания строки"""
        self.drag_start_index = from_index

    def _on_track_drop(self, event: Event, from_index: int) -> None:
        """Завершение перетаскивания и смена позиции трека"""
        if self.drag_start_index is None:
            return
        playlist = self._get_active_playlist()
        if not playlist or len(playlist) <= 1:
            self.drag_start_index = None
            return

        delta_y = event.y
        row_height = 42
        offset = round(delta_y / row_height)
        to_index = max(0, min(len(playlist) - 1, from_index + offset))

        if to_index != from_index:
            playlist.move_track(from_index, to_index)
            self.selected_track_index = to_index
            self._refresh_tracks_ui()

        self.drag_start_index = None

    def _on_move_up(self) -> None:
        """Смещение выбранного трека на одну позицию вверх"""
        playlist = self._get_active_playlist()
        if (
            not playlist
            or self.selected_track_index is None
            or self.selected_track_index <= 0
        ):
            return
        old_idx = self.selected_track_index
        new_idx = old_idx - 1
        playlist.move_track(old_idx, new_idx)
        self.selected_track_index = new_idx
        self._refresh_tracks_ui()

    def _on_move_down(self) -> None:
        """Смещение выбранного трека на одну позицию вниз"""
        playlist = self._get_active_playlist()
        if not playlist or self.selected_track_index is None:
            return
        if self.selected_track_index >= len(playlist) - 1:
            return
        old_idx = self.selected_track_index
        new_idx = old_idx + 1
        playlist.move_track(old_idx, new_idx)
        self.selected_track_index = new_idx
        self._refresh_tracks_ui()

    def _on_add_tracks(self) -> None:
        """Диалог выбора аудиофайлов и добавление их в плейлист"""
        playlist = self._get_active_playlist()
        if not playlist:
            return

        files: List[str] = []
        if platform.system() == "Darwin":
            mac_files = pick_files_macos()
            if mac_files is not None:
                files = mac_files

        if not files and platform.system() != "Darwin":
            file_types = [
                ("all files", "*.*"),
                ("mp3 audio", "*.mp3"),
                ("wav audio", "*.wav"),
                ("ogg audio", "*.ogg"),
                ("flac audio", "*.flac"),
            ]
            raw_files = filedialog.askopenfilenames(
                title="select audio files",
                filetypes=file_types,
            )
            if isinstance(raw_files, str):
                files = list(self.tk.splitlist(raw_files))
            elif raw_files:
                files = list(raw_files)

        for path in files:
            if not path or not os.path.exists(path):
                continue
            filename = os.path.basename(path)
            title, _ = os.path.splitext(filename)
            track = Composition(title=title, path=path)
            playlist.append(track)

        self._refresh_tracks_ui()

    def _on_add_folder(self) -> None:
        """Диалог выбора папки с аудиофайлами"""
        playlist = self._get_active_playlist()
        if not playlist:
            return

        folder: Optional[str] = None
        if platform.system() == "Darwin":
            mac_folder = pick_folder_macos()
            if mac_folder is not None:
                folder = mac_folder

        if not folder and platform.system() != "Darwin":
            folder = filedialog.askdirectory(title="select music folder")

        if not folder or not os.path.exists(folder):
            return

        valid_exts = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
        for entry in sorted(os.listdir(folder)):
            ext = os.path.splitext(entry)[1].lower()
            if ext in valid_exts:
                full_path = os.path.join(folder, entry)
                title, _ = os.path.splitext(entry)
                track = Composition(title=title, path=full_path)
                playlist.append(track)
        self._refresh_tracks_ui()

    def _on_add_path_dialog(self) -> None:
        """Добавление файлов или папки по прямому пути"""
        playlist = self._get_active_playlist()
        if not playlist:
            return
        dialog = ctk.CTkInputDialog(text="file or folder path:", title="add path")
        user_path = dialog.get_input()
        if not user_path or not user_path.strip():
            return
        cleaned = os.path.expanduser(user_path.strip())
        if not os.path.exists(cleaned):
            return
        if os.path.isdir(cleaned):
            valid_exts = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
            for entry in sorted(os.listdir(cleaned)):
                ext = os.path.splitext(entry)[1].lower()
                if ext in valid_exts:
                    full_path = os.path.join(cleaned, entry)
                    title, _ = os.path.splitext(entry)
                    playlist.append(Composition(title=title, path=full_path))
        else:
            filename = os.path.basename(cleaned)
            title, _ = os.path.splitext(filename)
            playlist.append(Composition(title=title, path=cleaned))
        self._refresh_tracks_ui()

    def _on_remove_track(self) -> None:
        """Удаление выбранного трека из активного плейлиста"""
        playlist = self._get_active_playlist()
        if not playlist or self.selected_track_index is None:
            return
        if self.selected_track_index < len(playlist):
            node_to_del = playlist[self.selected_track_index]
            if playlist.current is node_to_del:
                self.player.stop()
                self._update_now_playing_display()
            playlist.remove(node_to_del)
            if len(playlist) == 0:
                self.selected_track_index = None
            elif self.selected_track_index >= len(playlist):
                self.selected_track_index = len(playlist) - 1
            self._refresh_tracks_ui()

    def _start_playing_current(self) -> None:
        """Запуск воспроизведения текущего выбранного трека"""
        playlist = self._get_active_playlist()
        if not playlist or not playlist.current:
            self._update_now_playing_display()
            return
        track: Composition = playlist.current.data
        if track.path and os.path.exists(track.path):
            self.player.play(track.path)
            if self.play_btn:
                self.play_btn.configure(text="pause")
        self._update_now_playing_display()
        self._refresh_tracks_ui()

    def _on_toggle_play(self) -> None:
        """Переключение воспроизведение/пауза"""
        playlist = self._get_active_playlist()
        if not playlist or len(playlist) == 0:
            return
        if self.player.is_paused:
            self.player.resume()
            if self.play_btn:
                self.play_btn.configure(text="pause")
        elif self.player.is_busy():
            self.player.pause()
            if self.play_btn:
                self.play_btn.configure(text="play")
        else:
            if not playlist.current:
                playlist.play_all()
            self._start_playing_current()

    def _on_next_track(self) -> None:
        """Переход и воспроизведение следующего трека"""
        playlist = self._get_active_playlist()
        if not playlist or len(playlist) == 0:
            return
        playlist.next_track()
        self._start_playing_current()

    def _on_prev_track(self) -> None:
        """Переход и воспроизведение предыдущего трека"""
        playlist = self._get_active_playlist()
        if not playlist or len(playlist) == 0:
            return
        playlist.previous_track()
        self._start_playing_current()

    def _on_volume_change(self, value: float) -> None:
        """Изменение громкости воспроизведения"""
        self.player.volume = value

    def _update_now_playing_display(self) -> None:
        """Обновление текстовых меток текущего трека"""
        playlist = self._get_active_playlist()
        if playlist and playlist.current:
            track: Composition = playlist.current.data
            if self.now_playing_title:
                self.now_playing_title.configure(text=track.title)
            if self.now_playing_artist:
                self.now_playing_artist.configure(text=track.artist or "local file")
        else:
            if self.now_playing_title:
                self.now_playing_title.configure(text="no track selected")
            if self.now_playing_artist:
                self.now_playing_artist.configure(text="")
            if self.play_btn:
                self.play_btn.configure(text="play")

    def _start_poll_loop(self) -> None:
        """Запуск циклической проверки состояния плеера"""
        playlist = self._get_active_playlist()
        if playlist and playlist.current:
            if not self.player.is_busy() and not self.player.is_paused:
                if self.play_btn and self.play_btn.cget("text") == "pause":
                    playlist.next_track()
                    self._start_playing_current()
        self.after(500, self._start_poll_loop)
