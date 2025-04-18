import logging
import urwid as u

from managers.exceptions import UserAlreadyExistsError

from models.user import User
from modes.base_mode import BaseMode

from ui.app_modes import AppModes


class RegisterMode(BaseMode):

    def __init__(self, app_manager, users_manager):
        self.app_manager = app_manager
        self.users_manager = users_manager
        self.status_message = u.Text("")

        super().__init__(
            app_manager,
            "Register (create new user)f",
            "Enter name, e-mail, password and passcode to register, use Arrows to navigate | Ctrl + D to return to login",
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

        register_button = u.Button("Register", align="center")
        clear_button = u.Button("Clear", align="center")

        u.connect_signal(register_button, "click", self.handle_register)
        u.connect_signal(clear_button, "click", self.handle_clear)

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
                ("weight", 2, u.AttrMap(register_button, "button")),
                ("weight", 2, u.AttrMap(clear_button, "button")),
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

    def handle_register(self, _button):
        name = self.name_field.get_edit_text()
        email = self.email_field.get_edit_text()
        password = self.password_field.get_edit_text()
        passcode = self.passcode_field.get_edit_text()

        if not name:
            self.status_message.set_text("Please enter name.")
            self.form.focus_position = 0
        elif not email:
            self.status_message.set_text("Please enter email.")
            self.form.focus_position = 2
        elif not User.is_valid_email(email):
            self.status_message.set_text(f"Invalid e-mail format.")
            self.form.focus_position = 2
        elif not password:
            self.status_message.set_text("Please enter password.")
            self.form.focus_position = 4
        elif not passcode:
            self.status_message.set_text("Please enter passcode.")
            self.form.focus_position = 6
        else:
            try:
                new_user = self.users_manager.add_user(name, email, password, passcode)
                if new_user:
                    self.name_field.set_edit_text("")
                    self.email_field.set_edit_text("")
                    self.password_field.set_edit_text("")
                    self.passcode_field.set_edit_text("")
                    self.status_message.set_text("")
                    logging.info(
                        f"User has been registered: {new_user.name} <{new_user.email}> ({new_user.id})."
                    )
                    self.app_manager.active_user = new_user
                    self.app_manager.show(AppModes.MENU)
            except UserAlreadyExistsError as e:
                self.status_message.set_text(str(e))
                self.name_field.set_edit_text("")
                self.email_field.set_edit_text("")
                self.password_field.set_edit_text("")
                self.passcode_field.set_edit_text("")
                self.form.focus_position = 2
            except Exception as e:
                logging.exception(
                    f"An unexpected error occurred during registration: {e}."
                )
                self.status_message.set_text(
                    "An unexpected error occurred during registration."
                )
                self.form.focus_position = 0

    def handle_clear(self, _button):
        self.name_field.set_edit_text("")
        self.email_field.set_edit_text("")
        self.password_field.set_edit_text("")
        self.passcode_field.set_edit_text("")
        self.status_message.set_text("")
        if self.body and self.form:
            self.form.focus_position = 0

    def handle_input(self, key: str) -> str | None:
        if key == "ctrl d":
            self.app_manager.show(AppModes.LOGIN)
            return None
        return key
