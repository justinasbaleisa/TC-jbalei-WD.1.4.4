import urwid as u

from modes.list_menu_mode import ListMenuMode, MenuItemData

from ui.app_modes import AppModes


class MenuMode(ListMenuMode):
    def __init__(self, app_manager):

        super().__init__(
            app_manager,
            "Main Menu",
            "Use Arrows/Enter to select option | Ctrl+D to logout",
        )

    def _get_items_data(self) -> list[MenuItemData]:
        return [
            (
                "Therapy",
                "Start a new therapy session.",
                lambda _button: self.app_manager.show(AppModes.THERAPY),
            ),
            (
                "Profile",
                "Edit user profile.\n\nYou can:\n- edit profile details:\n  - name,\n  - email,\n  - password/passcode,\n- delete user.",
                lambda _button: self.app_manager.show(AppModes.PROFILE),
            ),
            (
                "Log out",
                "Return to login view.",
                lambda _button: self.app_manager.logout(),
            ),
        ]

    def handle_input(self, key: str) -> str | None:
        if key == "ctrl d":
            self.app_manager.logout()
            return None
        return key
