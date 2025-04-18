from abc import abstractmethod
import urwid as u

from modes.base_mode import BaseMode

from ui.app_widgets import PlainButton, MenuListBox
from collections.abc import Callable


MenuItemData = tuple[str, str, Callable]


class ListMenuMode(BaseMode):

    def __init__(self, app_manager, header_text: str, footer_text: str):
        self.items_data: list[MenuItemData] = []
        self.description_widget: u.Text | None = None
        self.listbox: MenuListBox | None = None
        super().__init__(app_manager, header_text, footer_text)

    @abstractmethod
    def _get_items_data(self) -> list[MenuItemData]:
        raise NotImplementedError("Subclasses must implement _get_items_data")

    def _create_body(self) -> u.Widget:
        self.items_data = self._get_items_data()
        self.description_widget = u.Text("Select an item.")
        menu_buttons = self._create_list_buttons(self.items_data)

        self.listbox = MenuListBox(
            u.SimpleFocusListWalker(menu_buttons), self.update_description_text
        )
        if menu_buttons:
            self.listbox.set_focus(0)

        col_1 = u.Pile([self.listbox])
        col_2 = u.Padding(self.description_widget, left=2, right=1)
        columns_widget = u.Columns(
            [("weight", 1, col_1), ("weight", 3, col_2)], dividechars=1
        )
        return columns_widget

    def on_activate(self) -> None:
        super().on_activate()
        
        try:
            if self.frame:
                self.frame.set_focus("body")
            if self.listbox:
                self.listbox.set_focus(self.listbox.focus_position or 0)
        except Exception as e:
            raise ValueError(
                f"Error setting focus in " f"{self.__class__.__name__}.on_activate: {e}"
            )

        self.update_description_text()

    def _create_list_buttons(self, items_data: list[MenuItemData]) -> list[u.Widget]:
        buttons = []
        for label, _, action in items_data:
            button = PlainButton(label, on_press=action)
            buttons.append(
                u.AttrMap(
                    u.Padding(
                        u.Pile([u.Text(""), button, u.Text("")]),
                        left=1,
                        right=1,
                        min_width=15,
                    ),
                    "inactive",
                    "focus",
                )
            )
        return buttons

    def update_description_text(self):
        listbox = getattr(self, "listbox", None)
        description_widget = getattr(self, "description_widget", None)
        items_data = getattr(self, "items_data", [])

        if listbox is None or description_widget is None:
            return

        focus_widget, focus_pos = listbox.get_focus()
        if focus_widget is None:
            description_widget.set_text("Item to focus not found.")
            return

        try:
            button = focus_widget.original_widget.original_widget.contents[1][0]
            label = button.original_label.strip()

            description = "Description not found."
            for item_label, item_desc, _ in items_data:
                if item_label == label:
                    description = item_desc
                    break
            description_widget.set_text(description)

        except (AttributeError, IndexError, TypeError) as e:
            if description_widget:
                description_widget.set_text("Could not get description.")
            else:
                raise ValueError(
                    f"Error updating description in " f"{self.__class__.__name__}: {e}"
                )
