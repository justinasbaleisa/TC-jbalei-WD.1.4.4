import logging
import urwid as u

from managers.users_manager import UsersManager
from managers.ai_manager import AIManager

from models.user import User

from modes.login_mode import LoginMode
from modes.register_mode import RegisterMode
from modes.menu_mode import MenuMode
from modes.therapy_mode import TherapyMode
from modes.profile_mode import ProfileMode

from ui.app_modes import AppModes


class AppManager:
    def __init__(self):
        self.users_manager = UsersManager()
        self.ai_manager = AIManager()
        self._active_user: User | None = None

        self.login_mode = LoginMode(self, self.users_manager)
        self.register_mode = RegisterMode(self, self.users_manager)
        self.menu_mode = MenuMode(self)
        self.therapy_mode = TherapyMode(self, self.users_manager, self.ai_manager)
        self.profile_mode = ProfileMode(self, self.users_manager)

        self.palette = [
            ("inactive", "dark gray", "default"),
            ("focus", "light gray", "dark red", "standout"),
            ("header", "white", "dark blue"),
            ("sub_header", "white", "default"),
            ("chat", "dark gray", "default"),
            ("chat_last", "white", "default"),
            ("chat_speaker", "yellow", "default"),
            ("input", "white", "dark gray"),
            ("footer", "yellow", "default"),
            ("error", "dark red", "default"),
            ("label", "light gray", "default"),
            ("button", "white", "dark blue", "standout"),
        ]
        self.modes = {
            AppModes.LOGIN: self.login_mode,
            AppModes.REGISTER: self.register_mode,
            AppModes.MENU: self.menu_mode,
            AppModes.THERAPY: self.therapy_mode,
            AppModes.PROFILE: self.profile_mode,
        }
        self.loop = None
        self.active_frame = None
        self.active_mode = None

    @property
    def active_user(self) -> User | None:
        return self._active_user

    @active_user.setter
    def active_user(self, user: User | None) -> None:
        self._active_user = user

    def logout(self, button=None) -> None:
        logging.info(
            f"User has logged out: {self.active_user.name} <{self.active_user.email}> ({self.active_user.id})."
        )
        self.active_user = None
        self.show(AppModes.LOGIN)

    def exit_app(self, button=None) -> None:
        raise u.ExitMainLoop()

    def set_view(self, mode_instance, new_frame_widget) -> None:
        self.active_mode = mode_instance
        self.active_frame = new_frame_widget
        if self.loop:
            self.loop.widget = self.active_frame
            self.loop.draw_screen()

    def show(self, mode_enum: AppModes) -> None:
        mode = self.modes.get(mode_enum)
        if not mode:
            logging.error(f"Attempted to show unknown mode: {mode_enum}")
            mode = self.modes.get(AppModes.LOGIN)
            return
        frame = mode.get_frame()
        self.set_view(mode, frame)
        mode.on_activate()

    def handle_input(self, key: str) -> str | None:
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
        self.show(AppModes.LOGIN)
        if not self.active_frame:
            logging.critical("No active frame set after initial show(). Cannot start.")
            return
        self.loop = u.MainLoop(
            self.active_frame, self.palette, unhandled_input=self.handle_input
        )
        self.loop.screen.set_terminal_properties(colors=256)
        self.loop.run()

