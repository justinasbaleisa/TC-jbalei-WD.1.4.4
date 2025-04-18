from abc import ABC, abstractmethod
import logging
import urwid as u


class BaseMode(ABC):

    def __init__(self, app_manager, header_text: str, footer_text: str):
        self.app_manager = app_manager
        self._header_text = header_text
        self._footer_text = footer_text

        self.header_widget = self._create_header()
        self.body_widget = self._create_body()
        self.footer_widget = self._create_footer()

        self.frame = u.Frame(
            body=self.body_widget,
            header=self.header_widget,
            footer=self.footer_widget if self.footer_widget else None,
        )

    def _create_header(self) -> u.Widget:
        header_txt = u.Text(f"\n{self._header_text.strip()}\n", align="center")
        return u.AttrMap(header_txt, "header")

    @abstractmethod
    def _create_body(self) -> u.Widget:
        raise NotImplementedError("Subclasses must implement _create_body")

    def _create_additional_footer_widgets(self) -> list[u.Widget]:
        return []

    def _create_footer(self) -> u.Widget:
        footer_contents = []
        additional_widgets = self._create_additional_footer_widgets()
        if additional_widgets:
            footer_contents.extend(additional_widgets)

        footer_txt = u.Text(f"\n{self._footer_text.strip()}\n", align="center")
        footer_styled = u.AttrMap(footer_txt, "footer")
        footer_contents.append(footer_styled)
        return u.Pile(footer_contents)

    def get_frame(self) -> u.Frame:
        return self.frame

    def handle_input(self, key: str) -> str | None:
        return key

    def on_activate(self) -> None:
        active_user = self.app_manager.active_user
        dynamic_header_text = self._header_text
        if active_user and hasattr(active_user, 'name'):
            dynamic_header_text += f"  ({active_user.name} <{active_user.email}>)"
        header_map = getattr(self, "header_widget", None)
        header_text_widget = getattr(header_map, 'original_widget', None) if header_map else None

        if isinstance(header_text_widget, u.Text):
             try:
                  header_text_widget.set_text(f"\n{dynamic_header_text.strip()}\n")
             except Exception as e:
                  logging.error(f"Failed updating header text in {self.__class__.__name__}: {e}")
