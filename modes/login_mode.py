import logging
import urwid as u

from managers.exceptions import UserNotFoundError, InvalidPasswordError
from models.user import User
from modes.base_mode import BaseMode


class LoginMode(BaseMode):

    def __init__(self, app_manager, users_manager):
        self.app_manager = app_manager
        self.users_manager = users_manager
        self.status_message = u.Text("")

        super().__init__(
            app_manager,
            "Log In (guest)",
            "Enter e-mail, password and passcode to log in, use Arrows to navigate | Ctrl + D to exit the program",
        )

    def _create_body(self) -> u.Widget:

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

        login_button = u.Button("Login", align="center")
        clear_button = u.Button("Clear", align="center")
        register_button = u.Button("Register (create new user)", align="center")

        u.connect_signal(login_button, "click", self.handle_login)
        u.connect_signal(clear_button, "click", self.handle_clear)
        u.connect_signal(register_button, "click", self.handle_register)

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
                ("weight", 2, u.AttrMap(login_button, "button")),
                ("weight", 2, u.AttrMap(clear_button, "button")),
            ],
            dividechars=1,
        )
        register_row = u.Columns(
            [
                ("weight", 1, u.AttrMap(u.Text(""), "label")),
                ("weight", 4, u.AttrMap(register_button, "button")),
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
                email_row,
                u.Divider(),
                password_row,
                u.Divider(),
                passcode_row,
                u.Divider(),
                button_row,
                u.Divider(),
                register_row,
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

    def handle_login(self, _button):
        email = self.email_field.get_edit_text()
        password = self.password_field.get_edit_text()
        passcode = self.passcode_field.get_edit_text()

        if not email:
            self.status_message.set_text("Please enter email.")
            self.form.focus_position = 0
        elif not User.is_valid_email(email):
            self.status_message.set_text(f"Invalid e-mail format.")
            self.form.focus_position = 0
        elif not password:
            self.status_message.set_text("Please enter password.")
            self.form.focus_position = 2
        elif not passcode:
            self.status_message.set_text("Please enter passcode.")
            self.form.focus_position = 4
        else:
            try:
                user = self.users_manager.authenticate_user(email, password, passcode)
                if user:
                    self.email_field.set_edit_text("")
                    self.password_field.set_edit_text("")
                    self.passcode_field.set_edit_text("")
                    self.status_message.set_text("")
                    logging.info(
                        f"User has logged in: {user.name} <{user.email}> ({user.id})."
                    )
                    self.app_manager.active_user = user
                    self.form.focus_position = 0
                    self.app_manager.show("main_menu")
            except UserNotFoundError as e:
                self.status_message.set_text(str(e))
                self.email_field.set_edit_text("")
                self.password_field.set_edit_text("")
                self.passcode_field.set_edit_text("")
                self.form.focus_position = 0
            except InvalidPasswordError as e:
                self.status_message.set_text(str(e))
                self.password_field.set_edit_text("")
                self.passcode_field.set_edit_text("")
                self.form.focus_position = 2
            except Exception as e:
                logging.exception(f"An unexpected error occurred during login: {e}.")
                self.status_message.set_text(
                    "An unexpected error occurred during login."
                )
                self.form.focus_position = 0

    def handle_clear(self, _button):
        self.email_field.set_edit_text("")
        self.password_field.set_edit_text("")
        self.passcode_field.set_edit_text("")
        self.status_message.set_text("")
        self.form.focus_position = 0

    def handle_register(self, _button):
        self.form.focus_position = 0
        self.app_manager.show("register")
