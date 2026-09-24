"""Список треков с поддержкой выделения, двойного клика и Drag-and-Drop"""

from collections.abc import Callable
from tkinter import Event

import customtkinter as ctk

from src.models import LinkedListItem, PlayList
from src.ui.constants import (
    COLOR_BG_CARD,
    COLOR_BG_PLAYING,
    COLOR_BG_SELECTED,
    COLOR_BORDER_DRAG,
    COLOR_BORDER_DROP,
    COLOR_TEXT_DIM,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_SECONDARY,
    FONT_NAME,
)


class TrackListView(ctk.CTkScrollableFrame):
    """Виджет списка треков с Drag-and-Drop и визуальной подсветкой"""

    def __init__(
        self,
        master: ctk.CTkFrame,
        on_select_track: Callable[[int], None],
        on_play_track: Callable[[int], None],
        on_move_track: Callable[[int, int], None],
    ) -> None:
        """Инициализация списка треков"""
        super().__init__(master, fg_color="transparent")
        self.on_select_track = on_select_track
        self.on_play_track = on_play_track
        self.on_move_track = on_move_track

        self.drag_start_index: int | None = None
        self._track_row_frames: list[ctk.CTkFrame] = []
        self._current_playlist: PlayList | None = None
        self._is_busy: bool = False

    def _find_target_row_index(self, y_root: int) -> int:
        """Поиск целевого индекса строки по абсолютной координате y_root"""
        if not self._track_row_frames:
            return 0
        if y_root <= self._track_row_frames[0].winfo_rooty():
            return 0
        last_frame = self._track_row_frames[-1]
        if y_root >= last_frame.winfo_rooty() + last_frame.winfo_height():
            return len(self._track_row_frames) - 1
        best_idx = 0
        min_dist = float("inf")
        for idx, frame in enumerate(self._track_row_frames):
            center_y = frame.winfo_rooty() + frame.winfo_height() / 2
            dist = abs(y_root - center_y)
            if dist < min_dist:
                min_dist = dist
                best_idx = idx
        return best_idx

    def _on_track_press(self, index: int) -> None:
        """Начало перетаскивания и выбор строки"""
        self.drag_start_index = index
        self.set_selected(index)
        self.on_select_track(index)

    def set_selected(self, selected_index: int | None) -> None:
        """Обновление подсветки строк без пересоздания виджетов"""
        playlist = self._current_playlist
        for idx, frame in enumerate(self._track_row_frames):
            is_playing = (
                playlist is not None
                and idx < len(playlist)
                and playlist.current is playlist[idx]
                and self._is_busy
            )
            is_selected = selected_index == idx
            bg_color = (
                COLOR_BG_SELECTED
                if is_selected
                else (COLOR_BG_PLAYING if is_playing else COLOR_BG_CARD)
            )
            frame.configure(fg_color=bg_color)

    def _on_track_double_click(self, index: int) -> None:
        """Воспроизведение трека по двойному клику"""
        self.on_play_track(index)

    def _on_track_drag(self, event: Event) -> None:
        """Визуальная индикация перемещения строки"""
        if self.drag_start_index is None or not self._track_row_frames:
            return
        target_idx = self._find_target_row_index(event.y_root)
        for idx, frame in enumerate(self._track_row_frames):
            if idx == self.drag_start_index:
                frame.configure(border_width=1, border_color=COLOR_BORDER_DRAG)
            elif idx == target_idx:
                frame.configure(border_width=1, border_color=COLOR_BORDER_DROP)
            else:
                frame.configure(border_width=0)

    def _on_track_drop(self, event: Event) -> None:
        """Завершение перетаскивания и перемещение трека"""
        if self.drag_start_index is None:
            return
        target_idx = self._find_target_row_index(event.y_root)
        if target_idx != self.drag_start_index:
            self.on_move_track(self.drag_start_index, target_idx)
        self.drag_start_index = None

    def refresh_tracks(
        self,
        playlist: PlayList | None,
        selected_index: int | None,
        is_busy: bool,
    ) -> None:
        """Полная перерисовка списка треков"""
        self._current_playlist = playlist
        self._is_busy = is_busy
        for frame in self._track_row_frames:
            frame.destroy()
        self._track_row_frames.clear()

        if playlist is None:
            return

        for idx, node in enumerate(playlist):
            is_playing = playlist.current is node and is_busy
            is_selected = selected_index == idx
            self._create_track_row(idx, node, is_playing, is_selected)

    def _create_track_row(
        self,
        idx: int,
        node: LinkedListItem,
        is_playing: bool,
        is_selected: bool,
    ) -> None:
        """Создание элемента строки трека"""
        bg_color = (
            COLOR_BG_SELECTED
            if is_selected
            else (COLOR_BG_PLAYING if is_playing else COLOR_BG_CARD)
        )
        row = ctk.CTkFrame(self, fg_color=bg_color, corner_radius=4, height=40)
        row.pack(fill="x", pady=2, padx=2)
        row.pack_propagate(False)

        drag_icon = ctk.CTkLabel(
            row,
            text="::",
            width=24,
            font=ctk.CTkFont(family=FONT_NAME, size=13, weight="bold"),
            text_color=COLOR_TEXT_DIM,
        )
        drag_icon.pack(side="left", padx=(10, 4))

        num_lbl = ctk.CTkLabel(
            row,
            text=f"{idx + 1:02d}",
            width=28,
            font=ctk.CTkFont(family=FONT_NAME, size=12),
            text_color=COLOR_TEXT_MUTED,
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
            text_color="#ffffff" if is_playing else COLOR_TEXT_SECONDARY,
        )
        title_lbl.pack(side="left", padx=12, fill="x", expand=True)

        status_lbl = ctk.CTkLabel(
            row,
            text="[playing]" if is_playing else "",
            text_color=COLOR_TEXT_MAIN,
            font=ctk.CTkFont(family=FONT_NAME, size=11),
        )
        status_lbl.pack(side="right", padx=16)

        for widget in (row, drag_icon, num_lbl, title_lbl, status_lbl):
            widget.bind("<Button-1>", lambda _e, i=idx: self._on_track_press(i))
            widget.bind(
                "<Double-Button-1>", lambda _e, i=idx: self._on_track_double_click(i)
            )
            widget.bind("<B1-Motion>", self._on_track_drag)
            widget.bind("<ButtonRelease-1>", self._on_track_drop)

        self._track_row_frames.append(row)
