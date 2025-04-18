import urwid as u

from modes.list_menu_mode import ListMenuMode, MenuItemData


class MainMenuMode(ListMenuMode):
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
                lambda _button: self.app_manager.show("therapy"),
            ),
            (
                "Profile",
                "Edit user profile.\n\nYou can:\n- edit profile details (name, email, credentials),\n- delete user.",
                lambda _button: self.app_manager.show("profile"),
            ),
            (
                "Log out",
                "Return to login view.",
                lambda _button: self.app_manager.logout(),
            ),
        ]
