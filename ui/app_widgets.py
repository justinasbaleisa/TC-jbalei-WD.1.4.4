import urwid as u

# Custom icon that doesn't show a cursor.
class NoCursorSelectableIcon(u.SelectableIcon):
    def __init__(self, text, cursor_position=0):
        super().__init__(str(text), cursor_position=cursor_position)

    def get_cursor_coords(self, size):
        return None

# Custom button
class PlainButton(u.Button):
    button_left = u.Text("")
    button_right = u.Text("")

    def __init__(self, label, on_press=None, user_data=None):
        self.original_label = label
        super().__init__(label, on_press=on_press, user_data=user_data)
        self._w = NoCursorSelectableIcon(self.original_label, 0)

    def get_label(self):
        return self.original_label

    def set_label(self, new_label):
        self._w.set_text(str(new_label))
        self._invalidate()

    def mouse_event(self, size, event, button, col, row, focus):
        if event == 'mouse press' and button == 1:
            self._emit('click')
            return True
        return super().mouse_event(size, event, button, col, row, focus)


# Modified MenuListBox that accepts an update callback.
class MenuListBox(u.ListBox):
    def __init__(self, body, update_callback=None):
        super().__init__(body)
        self.update_callback = update_callback

    def keypress(self, size, key):
        # Store focus position before keypress
        old_focus_pos = self.focus_position
        # Let the parent ListBox handle the keypress first (moves focus)
        result = super().keypress(size, key)

        # If a movement key was pressed, focus might have changed.
        # Call the callback directly *after* the parent handled the key.
        if key in ("up", "down", "page up", "page down", "home", "end") and self.update_callback:
            # Check if focus actually changed to avoid redundant calls
             if self.focus_position != old_focus_pos:
                self.update_callback() # Call directly

        return result

    def mouse_event(self, size, event, button, col, row, focus):
        # Store focus position before mouse event
        old_focus_pos = self.focus_position
        # Let the parent ListBox handle the mouse event first
        result = super().mouse_event(size, event, button, col, row, focus)

        # If it was a click that potentially changed focus, call the callback.
        if event == 'mouse press' and button == 1 and self.update_callback:
             # Check if focus actually changed
             if self.focus_position != old_focus_pos:
                self.update_callback() # Call directly

        return result