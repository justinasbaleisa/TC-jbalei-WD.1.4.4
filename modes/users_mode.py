import urwid as u

from modes.base_mode import BaseMode


class UsersMode(BaseMode):
    def __init__(self, app_manager):
        super().__init__(
            app_manager,
            "User Management",
            "Some stuff here | Ctrl+D to return to Menu",
        )

    def _create_body(self) -> u.Widget:
        body_widget = u.Filler(
            u.Text(
                "User management features (Add, Edit, Delete) go here.\n\n"
                "type 'A' for add\n"
                "type 'E' for edit\n"
                "type 'D' for delete\n",
                align="center",
            )
        )

        return body_widget

    def handle_input(self, key: str) -> str | None:
        if key == "ctrl d":
            self.app_manager.show("main_menu")
            return None

        return key
