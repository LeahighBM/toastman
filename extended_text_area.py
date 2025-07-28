from textual.widgets import TextArea 
from textual import events

class ExtendedTextArea(TextArea):
    def _on_key(self, event: events.Key) -> None:
        
        match event.character:
            case '"':
                self.insert('""')
                self.move_cursor_relative(columns=-1)
                event.prevent_default()
            case "(":
                self.insert('()')
                self.move_cursor_relative(columns=-1)
                event.prevent_default()
            case "{":
                self.insert('{}')
                self.move_cursor_relative(columns=-1)
                event.prevent_default()
            case "[":
                self.insert('[]')
                self.move_cursor_relative(columns=-1)
                event.prevent_default()
