import urwid as u

from modes.main_menu_mode import MainMenuMode
from modes.therapy_mode import TherapyMode
from modes.users_mode import UsersMode


class AppManager:
    def __init__(self):
        self.main_menu_mode = MainMenuMode(self)
        self.therapy_mode = TherapyMode(self)
        self.users_mode = UsersMode(self)
        self.palette = [
            ("inactive",    "dark gray",  "default"),
            ("focus",       "light gray", "dark red", "standout"),
            ("header",      "white",      "dark blue"),
            ("chat",        "dark gray",  "default"),
            ("chat_last",   "white",      "default"),
            ("chat_speaker","yellow",     "default"),
            ("input",       "white",      "dark gray"),
            ("footer",      "yellow",     "default"),
            ("error",       "yellow",     "dark gray"),
        ]
        self.modes = {
            "main_menu": self.main_menu_mode,
            "therapy": self.therapy_mode,
            "users": self.users_mode,
        }
        self.loop = None
        self.active_frame = None
        self.active_mode = None

    def exit_app(self, button=None) -> None:
        raise u.ExitMainLoop()

    def set_view(self, mode_instance, new_view_widget) -> None:
        self.active_mode = mode_instance
        self.active_frame = new_view_widget
        if self.loop:
            self.loop.widget = self.active_frame
            self.loop.draw_screen()

    def show(self, mode_name: str):
        mode = self.modes.get(mode_name)
        frame = mode.get_frame()
        self.set_view(mode, frame)
        mode.on_activate()

        match mode_name:
            case "main_menu":
                mode.update_description()
            case "therapy":
                mode.focus_input()
            case "users":
                pass

    def handle_input(self, key: str) -> str:
        processed_key = key
        mode_handled = False

        if self.active_mode and hasattr(self.active_mode, "handle_input"):
            result = self.active_mode.handle_input(processed_key)
            if result is None:
                mode_handled = True
            else:
                processed_key = result

        if mode_handled:
            return None

        if processed_key == "ctrl d":
             self.exit_app()
             return None

        return processed_key

    def start(self) -> None:
        self.show("main_menu")
        self.loop = u.MainLoop(
            self.active_frame,
            self.palette,
            unhandled_input=self.handle_input
        )
        self.loop.screen.set_terminal_properties(colors=256)
        self.loop.run()