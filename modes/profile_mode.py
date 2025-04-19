import logging
import urwid as u

from managers.exceptions import (
    UserAlreadyExistsError,
    InvalidPasswordError,
    UserNotFoundError,
)

from models.user import User
from modes.base_mode import BaseMode

from ui.app_modes import AppModes


class ProfileMode(BaseMode):

    def __init__(self, app_manager, users_manager):
        self.app_manager = app_manager
        self.users_manager = users_manager
        self.status_message = u.Text("")
        self._status_alarm_handle = None

        super().__init__(
            app_manager,
            "Profile",
            "Edit name, e-mail, password, passcode, and Save, use Arrows to navigate | Ctrl + D to return to menu",
        )

    def _create_body(self) -> u.Widget:

        name_label = u.Text("\nName:", align="right")
        self.name_field = u.Edit()
        self.name_edit = u.Pile(
            [u.Divider(), u.Padding(self.name_field, left=1, right=1), u.Divider()]
        )

        email_label = u.Text("\nE-mail:", align="right")
        self.email_field = u.Edit()
        self.email_edit = u.Pile(
            [u.Divider(), u.Padding(self.email_field, left=1, right=1), u.Divider()]
        )

        password_label = u.Text("\nPassword:", align="right")
        self.password_field = u.Edit(mask="*")
        self.password_edit = u.Pile(
            [u.Divider(), u.Padding(self.password_field, left=1, right=1), u.Divider()]
        )

        passcode_label = u.Text("\nPasscode:", align="right")
        self.passcode_field = u.Edit(mask="*")
        self.passcode_edit = u.Pile(
            [u.Divider(), u.Padding(self.passcode_field, left=1, right=1), u.Divider()]
        )

        save_button = u.Button("Save", align="center")
        clear_button = u.Button("Clear", align="center")
        delete_button = u.Button("Delete profile", align="center")

        u.connect_signal(save_button, "click", self.handle_save)
        u.connect_signal(clear_button, "click", self.handle_clear)
        u.connect_signal(delete_button, "click", self.handle_delete)

        name_row = u.Columns(
            [
                ("weight", 1, u.AttrMap(name_label, "label")),
                ("weight", 4, u.AttrMap(self.name_edit, "input")),
            ],
            dividechars=1,
        )
        email_row = u.Columns(
            [
                ("weight", 1, u.AttrMap(email_label, "label")),
                ("weight", 4, u.AttrMap(self.email_edit, "input")),
            ],
            dividechars=1,
        )
        password_row = u.Columns(
            [
                ("weight", 1, u.AttrMap(password_label, "label")),
                ("weight", 4, u.AttrMap(self.password_edit, "input")),
            ],
            dividechars=1,
        )
        passcode_row = u.Columns(
            [
                ("weight", 1, u.AttrMap(passcode_label, "label")),
                ("weight", 4, u.AttrMap(self.passcode_edit, "input")),
            ],
            dividechars=1,
        )
        button_row = u.Columns(
            [
                ("weight", 1, u.AttrMap(u.Text(""), "label")),
                ("weight", 2, u.AttrMap(save_button, "button")),
                ("weight", 2, u.AttrMap(clear_button, "button")),
            ],
            dividechars=1,
        )
        delete_row = u.Columns(
            [
                ("weight", 1, u.AttrMap(u.Text(""), "label")),
                ("weight", 4, u.AttrMap(delete_button, "focus")),
            ],
            dividechars=1,
        )
        status_row = u.Columns(
            [
                ("weight", 1, u.Divider()),
                ("weight", 4, u.AttrMap(self.status_message, "error")),
            ],
            dividechars=1,
        )

        self.form = u.Pile(
            [
                name_row,
                u.Divider(),
                email_row,
                u.Divider(),
                password_row,
                u.Divider(),
                passcode_row,
                u.Divider(),
                button_row,
                u.Divider(),
                delete_row,
                u.Divider(),
                u.Divider(),
                status_row,
            ]
        )

        self.body = u.Columns(
            [
                ("weight", 1, u.Divider()),
                ("weight", 4, self.form),
                ("weight", 1, u.Divider()),
            ],
            dividechars=1,
        )

        main_view = u.Filler(self.body, valign="middle")
        return main_view

    def on_activate(self):
        super().on_activate()
        self.load_active_user_data()

    def handle_save(self, _button):
        user = self.app_manager.active_user
        if not user:
            return

        name = self.name_field.get_edit_text()
        email = self.email_field.get_edit_text()
        password = self.password_field.get_edit_text()
        passcode = self.passcode_field.get_edit_text()

        if not name:
            self.status_message.set_text("Please enter name.")
            self.form.focus_position = 0
            return

        if not email:
            self.status_message.set_text("Please enter email.")
            self.form.focus_position = 2
            return

        if not User.is_valid_email(email):
            self.status_message.set_text(f"Invalid e-mail format.")
            self.form.focus_position = 2
            return

        pass_changed = bool(password and passcode)
        if bool(password or passcode) and not pass_changed:
            self.status_message.set_text(
                "Please enter both, password and passcode, to change."
            )
            self.form.focus_position = 4
            return

        name_changed = user.name != name
        email_changed = user.email != email

        if not name_changed and not email_changed and not pass_changed:
            self.delayed_status_message(2, "No changes detected to be saved.")
            logging.info("No changes detected to be saved.")
            return

        try:

            if name_changed:
                self.users_manager.edit_user_name(user.email, name)

            if email_changed:
                self.users_manager.edit_user_email(user.email, email)

            if pass_changed:
                self.users_manager.edit_user_pass(user.email, password, passcode)

            self.users_manager.save_users()
            self.on_activate()  # update header
            self.password_field.set_edit_text("")
            self.passcode_field.set_edit_text("")
            self.form.focus_position = 0
            self.delayed_status_message(2, "Profile updated successfully!")

        except UserAlreadyExistsError as e:
            self.status_message.set_text(str(e))
            self.email_field.set_edit_text(user.email)
            self.form.focus_position = 2

        except ValueError as e:
            logging.exception(f"Profile update failed due to invalid data: {e}")
            self.status_message.set_text(f"Invalid data provided: {e}")
            self.form.focus_position = 0

        except (IOError, OSError, TypeError) as e:
            logging.exception(
                f"Critical error saving profile changes after in-memory update: {e}."
            )
            self.status_message.set_text(f"Critical: changes failed to save!")
            self.form.focus_position = 0

        except Exception as e:
            logging.exception(
                f"An unexpected error occurred during profile update: {e}."
            )
            self.status_message.set_text(
                "An unexpected error occurred during profile update."
            )
            self.form.focus_position = 0

    def handle_delete(self, _button):
        user = self.app_manager.active_user
        if not user:
            return

        password = self.password_field.get_edit_text()
        passcode = self.passcode_field.get_edit_text()
        if not password or not passcode:
            self.status_message.set_text(
                "Please enter both, password and passcode, to delete."
            )
            self.form.focus_position = 4
            return

        name = self.name_field.get_edit_text()
        email = self.email_field.get_edit_text()
        if email != user.email or name != user.name:
            self.status_message.set_text(
                "Profile changes has not been saved before deletion."
            )
            self.form.focus_position = 0
            return

        try:
            self.users_manager.authenticate_user(user.email, password, passcode)
            self.app_manager.active_user = None
            self.users_manager.delete_user(user.email)
            self.form.focus_position = 0
            self.app_manager.show(AppModes.LOGIN)

        except InvalidPasswordError as e:
            self.status_message.set_text(str(e))
            self.password_field.set_edit_text("")
            self.passcode_field.set_edit_text("")
            self.form.focus_position = 4

        except UserNotFoundError as e:
            self.status_message.set_text(str(e))
            self.email_field.set_edit_text(user.email)
            self.form.focus_position = 2

        except (IOError, OSError, TypeError) as e:
            logging.exception(
                f"Critical error saving profile changes after in-memory update: {e}."
            )
            self.status_message.set_text(f"Critical: changes failed to save!")
            self.form.focus_position = 0

        except Exception as e:
            logging.exception(
                f"An unexpected error occurred during profile deletion: {e}."
            )
            self.status_message.set_text(
                "An unexpected error occurred during profile deletion."
            )
            self.form.focus_position = 0

    def delayed_status_message(self, delay: int, message: str) -> None:
        self.status_message.set_text(message)

        loop = self.app_manager.loop
        if not loop:
            return

        if self._status_alarm_handle:
            loop.remove_alarm(self._status_alarm_handle)

        self._status_alarm_handle = loop.set_alarm_in(delay, self.clear_status_message)

    def clear_status_message(self, loop=None, user_data=None) -> None:
        self.status_message.set_text("")
        self._status_alarm_handle = None

    def load_active_user_data(self) -> None:
        user = self.app_manager.active_user
        if not user:
            return

        self.name_field.set_edit_text(user.name)
        self.email_field.set_edit_text(user.email)
        self.password_field.set_edit_text("")
        self.passcode_field.set_edit_text("")
        self.status_message.set_text("")

    def handle_clear(self, _button):
        self.load_active_user_data()
        self.form.focus_position = 0

    def handle_input(self, key: str) -> str | None:
        if key == "ctrl d":
            self.load_active_user_data()
            self.app_manager.show(AppModes.MENU)
            return None
        return key
