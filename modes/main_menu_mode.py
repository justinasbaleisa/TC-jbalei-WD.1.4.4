import urwid as u

from modes.base_mode import BaseMode
from ui.app_widgets import PlainButton, MenuListBox


class MainMenuMode(BaseMode):
    def __init__(self, app_manager):
        super().__init__(app_manager, "Main Menu", "Use Arrows/Enter | Ctrl+D to exit")

    def _create_body(self) -> u.Widget:
        self.menu_description = u.Text("Select a menu item to see its description.")
        self.menu_items = [
            ("Therapy", "Start a new therapy session."),
            (
                "Users",
                "Manage user profiles.\n\nYou can:\n- add new user,\n- edit user profile,\n- change active user,\n- delete user.\n\nPress Enter to continue...",
            ),
            ("Exit program", "Quit the application."),
        ]
        self.menu_buttons = self._create_menu_buttons(self.menu_items)
        self.listbox = MenuListBox(u.SimpleFocusListWalker(self.menu_buttons), self.update_description)
        self.listbox.set_focus(0) # Set initial focus here

        col_1 = u.Pile([self.listbox])
        col_2 = u.Padding(self.menu_description, left=2, right=1)
        columns_widget = u.Columns([("weight", 1, col_1), ("weight", 3, col_2)], dividechars=1)

        return columns_widget

    def on_activate(self) -> None:
        self.update_description()
        
    def _create_menu_buttons(self, menu_items):
        buttons = []
        for label, _ in menu_items:
            action = None
            if label == "Therapy":
                action = lambda _button, name="therapy": self.app_manager.show(name)
            elif label == "Users":
                action = lambda _button, name="users": self.app_manager.show(name)
            elif label == "Exit program":
                action = lambda _button: self.app_manager.exit_app()

            button = PlainButton(label, on_press=action)
            buttons.append(
                u.AttrMap(
                    u.Padding(
                        u.Pile([u.Text(""), button, u.Text("")]),
                        left=1, right=1, min_width=15
                    ),
                    'inactive', 'focus'
                )
            )
        return buttons

    def update_description(self):
        if not hasattr(self, 'listbox') or not hasattr(self, 'menu_description'):
            return

        focus_widget, _ = self.listbox.get_focus()
        if focus_widget:
            try:
                button = focus_widget.original_widget.original_widget.contents[1][0]
                label = button.original_label.strip()
                description = dict(self.menu_items).get(label, "Description not found.")
                self.menu_description.set_text(description)
            except (AttributeError, IndexError):
                 self.menu_description.set_text("Could not get description.")