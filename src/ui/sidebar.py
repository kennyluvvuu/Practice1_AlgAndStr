"""Боковая панель управления плейлистами"""

from collections.abc import Callable

import customtkinter as ctk

from src.ui.constants import (
    COLOR_BG_HOVER,
    COLOR_BG_PANEL,
    COLOR_BG_SELECTED,
    COLOR_BORDER,
    COLOR_BTN_PRIMARY_BG,
    COLOR_BTN_PRIMARY_FG,
    COLOR_BTN_PRIMARY_HOVER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_SECONDARY,
    FONT_NAME,
)


class SidebarView(ctk.CTkFrame):
    """Виджет боковой панели со списком плейлистов и кнопками управления"""

    def __init__(
        self,
        master: ctk.CTk,
        on_select_playlist: Callable[[str], None],
        on_create_playlist: Callable[[str], None],
        on_delete_playlist: Callable[[], None],
    ) -> None:
        """Инициализация боковой панели"""
        super().__init__(master, width=240, corner_radius=0, fg_color=COLOR_BG_PANEL)
        self.on_select_playlist = on_select_playlist
        self.on_create_playlist = on_create_playlist
        self.on_delete_playlist = on_delete_playlist

        self._playlist_buttons: dict[str, ctk.CTkButton] = {}
        self.new_playlist_entry: ctk.CTkEntry | None = None
        self.playlist_scroll: ctk.CTkScrollableFrame | None = None

        self._build_widgets()

    def _build_widgets(self) -> None:
        """Построение элементов боковой панели"""
        self.grid_rowconfigure(2, weight=1)

        app_title = ctk.CTkLabel(
            self,
            text="player",
            font=ctk.CTkFont(family=FONT_NAME, size=20, weight="bold"),
            text_color=COLOR_TEXT_MAIN,
        )
        app_title.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="w")

        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.grid(row=1, column=0, padx=14, pady=4, sticky="ew")

        self.new_playlist_entry = ctk.CTkEntry(
            btn_box,
            placeholder_text="new playlist...",
            width=120,
            height=30,
            font=ctk.CTkFont(family=FONT_NAME, size=11),
            fg_color=COLOR_BG_HOVER,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_MAIN,
        )
        self.new_playlist_entry.pack(side="left", padx=(0, 4))
        self.new_playlist_entry.bind("<Return>", lambda _e: self._handle_create())

        add_pl_btn = ctk.CTkButton(
            btn_box,
            text="+",
            width=36,
            height=30,
            font=ctk.CTkFont(family=FONT_NAME, size=13, weight="bold"),
            fg_color=COLOR_BTN_PRIMARY_BG,
            text_color=COLOR_BTN_PRIMARY_FG,
            hover_color=COLOR_BTN_PRIMARY_HOVER,
            command=self._handle_create,
        )
        add_pl_btn.pack(side="left", padx=(0, 4))

        del_pl_btn = ctk.CTkButton(
            btn_box,
            text="del",
            width=42,
            height=30,
            font=ctk.CTkFont(family=FONT_NAME, size=11),
            fg_color=COLOR_BG_HOVER,
            text_color=COLOR_TEXT_SECONDARY,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color=COLOR_BORDER,
            command=self.on_delete_playlist,
        )
        del_pl_btn.pack(side="left")

        self.playlist_scroll = ctk.CTkScrollableFrame(
            self,
            label_text="playlists",
            label_font=ctk.CTkFont(family=FONT_NAME, size=12, weight="bold"),
            label_text_color=COLOR_TEXT_MUTED,
            fg_color="transparent",
        )
        self.playlist_scroll.grid(row=2, column=0, padx=12, pady=(8, 16), sticky="nsew")

    def _handle_create(self) -> None:
        """Обработка добавления плейлиста"""
        if self.new_playlist_entry is None:
            return
        name = self.new_playlist_entry.get().strip()
        if name:
            self.new_playlist_entry.delete(0, "end")
            self.on_create_playlist(name)

    def refresh_playlists(
        self, playlists: list[str], active_name: str | None
    ) -> None:
        """Перерисовка списка плейлистов"""
        if self.playlist_scroll is None:
            return
        for btn in self._playlist_buttons.values():
            btn.destroy()
        self._playlist_buttons.clear()

        for name in playlists:
            is_active = name == active_name
            color = COLOR_BG_SELECTED if is_active else "transparent"
            hover = "#3f3f46" if is_active else COLOR_BG_HOVER
            text_color = "#ffffff" if is_active else COLOR_TEXT_SECONDARY
            btn = ctk.CTkButton(
                self.playlist_scroll,
                text=name,
                anchor="w",
                font=ctk.CTkFont(family=FONT_NAME, size=12),
                fg_color=color,
                text_color=text_color,
                hover_color=hover,
                height=32,
                command=lambda n=name: self.on_select_playlist(n),
            )
            btn.pack(fill="x", pady=2)
            self._playlist_buttons[name] = btn
