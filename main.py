"""Точка входа для запуска аудиоплеера"""

from src.ui.main_window import MusicPlayerApp


def main() -> None:
    """Запуск приложения"""
    app = MusicPlayerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
