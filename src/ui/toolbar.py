"""Панель действий для управления треками и отображения статуса"""

from collections.abc import Callable

import customtkinter as ctk

from src.ui.constants import (
    COLOR_BG_HOVER,
    COLOR_BORDER,
    COLOR_BTN_PRIMARY_BG,
    COLOR_BTN_PRIMARY_FG,
    COLOR_BTN_PRIMARY_HOVER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    FONT_NAME,
)


class ToolbarView(ctk.CTkFrame):
    """Виджет панели инструментов со строкой ввода пути и кнопками действий"""

    def __init__(
        self,
        master: ctk.CTkFrame,
        on_add_files: Callable[[], None],
        on_add_folder: Callable[[], None],
        on_add_path: Callable[[str], None],
        on_remove_track: Callable[[], None],
        on_move_up: Callable[[], None],
        on_move_down: Callable[[], None],
    ) -> None:
        """Инициализация панели инструментов"""
        super().__init__(master, fg_color="transparent")
        self.on_add_files = on_add_files
        self.on_add_folder = on_add_folder
        self.on_add_path = on_add_path
        self.on_remove_track = on_remove_track
        self.on_move_up = on_move_up
        self.on_move_down = on_move_down

        self.playlist_title_label: ctk.CTkLabel | None = None
        self.status_label: ctk.CTkLabel | None = None
        self.path_entry: ctk.CTkEntry | None = None

        self._build_widgets()

    def _build_widgets(self) -> None:
        """Построение элементов панели инструментов"""
        title_bar = ctk.CTkFrame(self, fg_color="transparent")
        title_bar.pack(fill="x", padx=24, pady=(20, 8))

        self.playlist_title_label = ctk.CTkLabel(
            title_bar,
            text="main [0]",
            font=ctk.CTkFont(family=FONT_NAME, size=20, weight="bold"),
            text_color=COLOR_TEXT_MAIN,
        )
        self.playlist_title_label.pack(side="left")

        self.status_label = ctk.CTkLabel(
            title_bar,
            text="ready",
            font=ctk.CTkFont(family=FONT_NAME, size=11),
            text_color=COLOR_TEXT_MUTED,
        )
        self.status_label.pack(side="right")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=24, pady=(0, 12))

        add_files_btn = ctk.CTkButton(
            toolbar,
            text="files",
            width=65,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color=COLOR_BG_HOVER,
            text_color=COLOR_TEXT_MAIN,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color=COLOR_BORDER,
            command=self.on_add_files,
        )
        add_files_btn.pack(side="left", padx=(0, 6))

        add_folder_btn = ctk.CTkButton(
            toolbar,
            text="folder",
            width=70,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color=COLOR_BG_HOVER,
            text_color=COLOR_TEXT_MAIN,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color=COLOR_BORDER,
            command=self.on_add_folder,
        )
        add_folder_btn.pack(side="left", padx=(0, 8))

        self.path_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="file or folder path (e.g. ~/Music or track.mp3)...",
            width=340,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color=COLOR_BG_HOVER,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_MAIN,
        )
        self.path_entry.pack(side="left", padx=(0, 6))
        self.path_entry.bind("<Return>", lambda _e: self._handle_add_path())

        add_btn = ctk.CTkButton(
            toolbar,
            text="add",
            width=55,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12, weight="bold"),
            fg_color=COLOR_BTN_PRIMARY_BG,
            text_color=COLOR_BTN_PRIMARY_FG,
            hover_color=COLOR_BTN_PRIMARY_HOVER,
            command=self._handle_add_path,
        )
        add_btn.pack(side="left", padx=(0, 12))

        del_track_btn = ctk.CTkButton(
            toolbar,
            text="remove",
            width=70,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color=COLOR_BG_HOVER,
            text_color=COLOR_TEXT_MAIN,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color=COLOR_BORDER,
            command=self.on_remove_track,
        )
        del_track_btn.pack(side="left", padx=(0, 14))

        order_label = ctk.CTkLabel(
            toolbar,
            text="order:",
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        order_label.pack(side="left", padx=(0, 6))

        move_up_btn = ctk.CTkButton(
            toolbar,
            text="up",
            width=50,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color=COLOR_BG_HOVER,
            text_color=COLOR_TEXT_MAIN,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color=COLOR_BORDER,
            command=self.on_move_up,
        )
        move_up_btn.pack(side="left", padx=(0, 4))

        move_down_btn = ctk.CTkButton(
            toolbar,
            text="down",
            width=50,
            height=32,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color=COLOR_BG_HOVER,
            text_color=COLOR_TEXT_MAIN,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color=COLOR_BORDER,
            command=self.on_move_down,
        )
        move_down_btn.pack(side="left")

    def _handle_add_path(self) -> None:
        """Обработка добавления треков по пути"""
        if self.path_entry is None:
            return
        text = self.path_entry.get().strip()
        if text:
            self.on_add_path(text)

    def clear_path_entry(self) -> None:
        """Очистка поля ввода пути"""
        if self.path_entry is not None:
            self.path_entry.delete(0, "end")

    def set_title(self, text: str) -> None:
        """Обновление заголовка активного плейлиста"""
        if self.playlist_title_label is not None:
            self.playlist_title_label.configure(text=text)

    def set_status(self, text: str) -> None:
        """Обновление текста статуса"""
        if self.status_label is not None:
            self.status_label.configure(text=text)
