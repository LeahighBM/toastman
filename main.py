import json
import pyperclip
import requests
from textual import on
from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll
from textual.containers import Container
from textual.widgets import (
    Static, 
    Footer, 
    Input, 
    Select, 
    Button, 
    Header, 
    TextArea,
)

class Toastman(App):
    CSS_PATH = "css/toastman.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with HorizontalScroll():
            yield Select(
                options = [
                    ("GET", "GET"),
                    ("POST", "POST"),
                    ("PUT", "PUT"),
                    ("DELETE", "DELETE"),
                ],
                value="GET",
                id="http_verb_select"
                
            )
            yield Input(
                placeholder="https://example.com/items",
                id="url_bar")
            
            yield Button("Send", id="send_button")

    
        with Container():
            yield TextArea(
                read_only=True,
                id="response_text"
                )
            yield Button("Copy to clipboard", id="copy")
            
        yield Footer()

    @on(Button.Pressed, "#send_button")
    def send_request(self, event) -> None:
        select_obj = self.query_one("#http_verb_select", Select)
        verb = select_obj.value

        input_obj = self.query_one("#url_bar", Input)
        url = input_obj.value
        print(verb, url)

        match verb:
            case "GET":
                try:
                    resp = requests.get(url=url)
                    resp.raise_for_status()
                    json_data = json.dumps(resp.json(), indent=2, default=str)
                    self.update_text(json_data)
                except requests.exceptions.MissingSchema as e:
                    message = f"Missing URL. {e}"
                    self.update_text(message)

    @on(Button.Pressed, "#copy")
    def copy_button_press(self, event) -> None:
        self.copy_text()


    def update_text(self, text) -> None: 
        response_text_obj = self.query_one("#response_text", TextArea)
        response_text_obj.text = text   


    def copy_text(self):
        text_obj = self.query_one("#response_text")
        text = text_obj.text 

        try:
            pyperclip.copy(text=text)
            self.notify("Copied to clipboard.")
        except pyperclip.PyperclipException as e:
            self.notify(f"Could not copy to clipboard. {e}")


if __name__ == "__main__":
    Toastman().run()
