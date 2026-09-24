"""Нижняя панель управления воспроизведением и громкостью"""

from collections.abc import Callable

import customtkinter as ctk

from src.ui.constants import (
    COLOR_BG_HOVER,
    COLOR_BG_PANEL,
    COLOR_BORDER,
    COLOR_BTN_PRIMARY_BG,
    COLOR_BTN_PRIMARY_FG,
    COLOR_BTN_PRIMARY_HOVER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    FONT_NAME,
)


class BottomBarView(ctk.CTkFrame):
    """Виджет нижней панели с элементами управления плеером"""

    def __init__(
        self,
        master: ctk.CTk,
        on_prev: Callable[[], None],
        on_toggle_play: Callable[[], None],
        on_next: Callable[[], None],
        on_volume_change: Callable[[float], None],
        initial_volume: float = 0.7,
    ) -> None:
        """Инициализация нижней панели плеера"""
        super().__init__(master, height=90, corner_radius=0, fg_color=COLOR_BG_PANEL)
        self.on_prev = on_prev
        self.on_toggle_play = on_toggle_play
        self.on_next = on_next
        self.on_volume_change = on_volume_change
        self.initial_volume = initial_volume

        self.now_playing_title: ctk.CTkLabel | None = None
        self.now_playing_artist: ctk.CTkLabel | None = None
        self.play_btn: ctk.CTkButton | None = None
        self.vol_slider: ctk.CTkSlider | None = None

        self._build_widgets()

    def _build_widgets(self) -> None:
        """Построение элементов нижней панели"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)

        track_info_frame = ctk.CTkFrame(self, fg_color="transparent")
        track_info_frame.grid(row=0, column=0, sticky="w", padx=24, pady=12)

        self.now_playing_title = ctk.CTkLabel(
            track_info_frame,
            text="no track selected",
            font=ctk.CTkFont(family=FONT_NAME, size=13, weight="bold"),
            text_color=COLOR_TEXT_MAIN,
            anchor="w",
        )
        self.now_playing_title.pack(anchor="w")

        self.now_playing_artist = ctk.CTkLabel(
            track_info_frame,
            text="",
            font=ctk.CTkFont(family=FONT_NAME, size=11),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        )
        self.now_playing_artist.pack(anchor="w")

        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=0, column=1, pady=12)

        buttons_box = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_box.pack()

        prev_btn = ctk.CTkButton(
            buttons_box,
            text="prev",
            width=65,
            height=36,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color=COLOR_BG_HOVER,
            text_color=COLOR_TEXT_MAIN,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color=COLOR_BORDER,
            command=self.on_prev,
        )
        prev_btn.pack(side="left", padx=6)

        self.play_btn = ctk.CTkButton(
            buttons_box,
            text="play",
            width=110,
            height=36,
            font=ctk.CTkFont(family=FONT_NAME, size=12, weight="bold"),
            fg_color=COLOR_BTN_PRIMARY_BG,
            text_color=COLOR_BTN_PRIMARY_FG,
            hover_color=COLOR_BTN_PRIMARY_HOVER,
            command=self.on_toggle_play,
        )
        self.play_btn.pack(side="left", padx=6)

        next_btn = ctk.CTkButton(
            buttons_box,
            text="next",
            width=65,
            height=36,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            fg_color=COLOR_BG_HOVER,
            text_color=COLOR_TEXT_MAIN,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color=COLOR_BORDER,
            command=self.on_next,
        )
        next_btn.pack(side="left", padx=6)

        loop_badge = ctk.CTkLabel(
            buttons_box,
            text="[loop: on]",
            font=ctk.CTkFont(family=FONT_NAME, size=11),
            text_color=COLOR_TEXT_MUTED,
        )
        loop_badge.pack(side="left", padx=14)

        right_box = ctk.CTkFrame(self, fg_color="transparent")
        right_box.grid(row=0, column=2, sticky="e", padx=24, pady=12)

        vol_label = ctk.CTkLabel(
            right_box,
            text="vol:",
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        vol_label.pack(side="left", padx=(0, 8))

        self.vol_slider = ctk.CTkSlider(
            right_box,
            from_=0,
            to=1,
            width=110,
            button_color=COLOR_BTN_PRIMARY_BG,
            button_hover_color=COLOR_BTN_PRIMARY_HOVER,
            progress_color="#52525b",
            fg_color=COLOR_BORDER,
            command=self.on_volume_change,
        )
        self.vol_slider.set(self.initial_volume)
        self.vol_slider.pack(side="left")

    def set_track_info(self, title: str, artist: str, is_playing: bool) -> None:
        """Обновление отображения текущего трека и кнопки воспроизведения"""
        if self.now_playing_title is not None:
            self.now_playing_title.configure(text=title)
        if self.now_playing_artist is not None:
            self.now_playing_artist.configure(text=artist)
        if self.play_btn is not None:
            self.play_btn.configure(text="pause" if is_playing else "play")

    def set_volume(self, val: float) -> None:
        """Установка значения слайдера громкости"""
        if self.vol_slider is not None:
            self.vol_slider.set(val)
