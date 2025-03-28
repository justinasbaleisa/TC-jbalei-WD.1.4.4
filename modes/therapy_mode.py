import urwid as u

from modes.base_mode import BaseMode
from typing import List


class TherapyMode(BaseMode):
    def __init__(self, app_manager):
        self.messages = [("System", "Chat has been started...")]
        self.chat_window = None
        self.edit_box = None
        self.styled_input_area = None
        super().__init__(
            app_manager, "Therapy Session", "Enter message | Ctrl+D to return to Menu"
        )

    def _create_body(self) -> u.Widget:
        initial_widgets = self._build_message_widgets()
        self.chat_window = u.ListBox(u.SimpleListWalker(initial_widgets))
        padded_chat = u.Padding(
            self.chat_window, left=1, right=1
        )
        line_box = u.LineBox(padded_chat, title="Chat")
        styled_chat = u.AttrMap(line_box, "chat")
        return styled_chat

    def _create_additional_footer_widgets(self) -> List[u.Widget]:
        self.edit_box = u.Edit("input > ")
        input_area_pile = u.Pile(
            [
                u.Text(""),
                u.Padding(self.edit_box, left=2, right=2),
                u.Text(""),
            ]
        )
        self.styled_input_area = u.AttrMap(input_area_pile, "input")
        return [self.styled_input_area]

    def on_activate(self) -> None:
        self.focus_input()
        if self.chat_window and self.chat_window.body:
            try:
                self.chat_window.set_focus(len(self.chat_window.body) - 1)
            except IndexError:
                pass

    def _build_message_widgets(self) -> List[u.Widget]:
        message_widgets = []
        num_messages = len(self.messages)

        if num_messages == 0:
            return []

        for i, (sender, body) in enumerate(self.messages):
            is_last = i == num_messages - 1
            content_style = "chat_last" if is_last else "chat"
            speaker_part = f"{sender}: "
            markup = [("chat_speaker", speaker_part), (content_style, body)]
            text_widget = u.Text(markup)
            message_widgets.append(text_widget)

        return message_widgets

    def focus_input(self):
        if self.frame and self.styled_input_area and self.edit_box:
            self.frame.set_focus("footer")
            try:
                input_pile_widget = self.styled_input_area.original_widget
                edit_widget_padding = input_pile_widget.contents[1][0]
                input_pile_widget.set_focus(edit_widget_padding)
            except (AttributeError, IndexError, KeyError, TypeError):
                pass

    def update_chat(self, sender: str | None, body: str | None) -> None:
        if sender is not None and body is not None:
            self.messages.append((sender, body))
        message_widgets = self._build_message_widgets()

        try:
            if self.chat_window:
                self.chat_window.body[:] = message_widgets
                if message_widgets:
                    self.chat_window.set_focus(len(message_widgets) - 1)
            if self.app_manager and self.app_manager.loop:
                self.app_manager.loop.draw_screen()
        except Exception as e:
            print(f"[TherapyMode] Error updating chat window: {e}")

    def handle_input(self, key: str) -> str | None:
        if key == "ctrl d":
            self.app_manager.show("main_menu")
            return None

        elif key == "enter":
            if self.edit_box:
                message_body = self.edit_box.get_edit_text().strip()
                if message_body:
                    self.update_chat("You", message_body)
                    self.edit_box.set_edit_text("")
            return None

        return key