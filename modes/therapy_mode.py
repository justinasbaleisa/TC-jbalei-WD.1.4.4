import logging
import urwid as u

from modes.base_mode import BaseMode

from ui.app_modes import AppModes


class TherapyFrame(u.Frame):
    def __init__(
        self, therapy_mode_instance, body, header=None, footer=None, focus_part="body"
    ):
        self.therapy_mode = therapy_mode_instance
        super().__init__(body, header=header, footer=footer, focus_part=focus_part)

    def mouse_event(self, size, event, button, col, row, focus):
        if event == "mouse press" and button == 1:
            if self.therapy_mode:
                self.therapy_mode.focus_input()
            return True
        return super().mouse_event(size, event, button, col, row, focus)


class TherapyMode(BaseMode):
    def __init__(self, app_manager, users_manager, ai_manager):
        self.app_manager = app_manager
        self.users_manager = users_manager
        self.ai_manager = ai_manager

        self.messages = []

        self.chat_window = None
        self.edit_box = None
        self.styled_input_area = None
        super().__init__(
            app_manager,
            "Therapy Session",
            "Type message and press enter | Ctrl+D to return to main menu",
        )

        base_frame = self.frame
        self.frame = TherapyFrame(
            self,
            body=base_frame.body,
            header=base_frame.header,
            footer=base_frame.footer,
            focus_part="footer",
        )

    def _create_body(self) -> u.Widget:
        initial_widgets = self._build_message_widgets()
        self.chat_window = u.ListBox(u.SimpleListWalker(initial_widgets))
        padded_chat = u.Padding(self.chat_window, left=1, right=1)
        line_box = u.LineBox(padded_chat, title="Chat")
        styled_chat = u.AttrMap(line_box, "chat")
        return styled_chat

    def _create_additional_footer_widgets(self) -> list[u.Widget]:
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
        super().on_activate()

        user = self.app_manager.active_user
        if user:
            history_obj = user.chat_history
            if history_obj:
                self.messages = history_obj.copy()
                self.messages.append(("System", f"Continuing previous chat session from here..."))
            else:
                self.messages = [("System", "Chat session started...")]
        else:
            logging.warning(
                "TherapyMode.on_activate: No active user! Cannot load/save history."
            )
            self.messages = [("System", "Chat session started (No User)...")]

        try:
            if self.chat_window is None:
                logging.error(
                    "TherapyMode.on_activate: self.chat_window is None before UI update."
                )
            else:
                list_walker = getattr(self.chat_window, "body", None)
                if isinstance(list_walker, u.SimpleListWalker):
                    message_widgets = self._build_message_widgets()
                    list_walker.clear()
                    list_walker.extend(message_widgets)
                    if message_widgets:
                        try:
                            self.chat_window.set_focus(
                                len(list_walker) - 1
                            )
                        except IndexError:
                            pass
                        except Exception as focus_err:
                            logging.exception(f"Error setting focus: {focus_err}")
                    if self.app_manager and self.app_manager.loop:
                        self.app_manager.loop.draw_screen()
                elif list_walker is None:
                    logging.error(
                        "TherapyMode.on_activate: self.chat_window.body is None."
                    )
                else:
                    logging.error(
                        f"TherapyMode.on_activate: self.chat_window.body is not SimpleListWalker, type: {type(list_walker)}"
                    )
        except Exception as e:
            logging.exception("TherapyMode.on_activate: EXCEPTION during UI update.")

        self.focus_input()

    def custom_mouse_event(self, size, event, button, col, row, focus):
        if event == "mouse press":
            self.focus_input()
            return True
        return super().mouse_event(size, event, button, col, row, focus)

    def _build_message_widgets(self) -> list[u.Widget]:
        message_widgets = []
        num_messages = len(self.messages)
        if num_messages == 0:
            return []
        for i, (sender, body) in enumerate(self.messages):
            try:
                is_last = i == num_messages - 1
                content_style = "chat_last" if is_last else "chat"
                speaker_part = f"{sender}: "

                body_str = str(body) if body is not None else ""
                markup = [("chat_speaker", speaker_part), (content_style, body_str)]
                text_widget = u.Text(markup)
                message_widgets.append(text_widget)

            except Exception as e:
                logging.exception(
                    f"_build_message_widgets: ERROR creating widget for item {i} - Sender: {sender}, Body: {body[:50]}... Error: {e}"
                )
        return message_widgets

    def _build_single_message_widget(
        self, sender: str, body: str, is_last: bool
    ) -> u.Widget:
        content_style = "chat_last" if is_last else "chat"
        speaker_part = f"{sender}: "
        markup = [("chat_speaker", speaker_part), (content_style, body)]
        return u.Text(markup)

    def focus_input(self):
        if self.frame and self.styled_input_area and self.edit_box:
            self.frame.set_focus("footer")
            try:
                input_pile_widget = self.styled_input_area.original_widget
                edit_widget_padding = input_pile_widget.contents[1][0]
                input_pile_widget.set_focus(edit_widget_padding)
                if self.app_manager and self.app_manager.loop:
                    self.app_manager.loop.draw_screen()
            except (AttributeError, IndexError, KeyError, TypeError):
                pass

    def update_chat(self, sender: str | None, body: str | None) -> None:
        if sender is None or body is None:
            return
        self.messages.append((sender, body))

        if self.chat_window is None:
            logging.error("Chat window IS None in update_chat!")
            return

        try:
            list_walker = getattr(self.chat_window, "body", None)
            if not isinstance(list_walker, u.SimpleListWalker):
                logging.error(
                    f"Chat window body is not SimpleListWalker in update_chat! Type: {type(list_walker)}"
                )
                return

            num_widgets = len(list_walker)
            if num_widgets > 0:
                previous_last_index = num_widgets - 1

                if len(self.messages) >= 2:
                    prev_sender, prev_body = self.messages[-2]

                    try:
                        widget_to_update = self._build_single_message_widget(
                            prev_sender, prev_body, is_last=False
                        )
                        list_walker[previous_last_index] = widget_to_update

                    except Exception as replace_err:
                        logging.exception(
                            f"update_chat: Failed to replace/restyle widget at index {previous_last_index}: {replace_err}"
                        )

            new_widget = self._build_single_message_widget(sender, body, is_last=True)

            list_walker.append(new_widget)

            new_focus_index = len(list_walker) - 1
            self.chat_window._invalidate()  # Mark for recalculation
            self.chat_window.set_focus(new_focus_index)
            self.chat_window.set_focus_valign("bottom")  # Ensure visibility

            if self.app_manager and self.app_manager.loop:
                self.app_manager.loop.draw_screen()

        except Exception as e:
            logging.exception(f"[TherapyMode] Error updating chat window: {e}")

    def handle_input(self, key: str) -> str | None:
        if key == "ctrl d":
            user = self.app_manager.active_user
            if user:
                user.chat_history = self.messages.copy()
                try:
                    self.users_manager.save_users()
                    logging.info(f"Chat history saved for user {user.email}")
                except AttributeError:
                    logging.exception("Could not find users_manager to save history.")
                except Exception as e:
                    logging.exception(
                        f"Failed to save chat history for user {user.email}: {e}"
                    )
            else:
                logging.warning("No active user found, chat history not saved.")

            self.app_manager.show(AppModes.MENU)
            return None

        elif key == "enter":
            if self.edit_box:
                message_body = self.edit_box.get_edit_text().strip()
                if message_body:
                    
                    try:
                        self.update_chat(
                            "You", message_body
                        )  # Appends to self.messages
                        self.edit_box.set_edit_text("")
                        # Log state BEFORE API call

                        ai_response = self.ai_manager.get_response(self.messages)
                        self.update_chat("AI", ai_response)

                    except Exception as e:
                        logging.exception(f"Error fetching response: {e}")
                        self.update_chat("System", f"error fetching response: {e}")
            return None
        return key
