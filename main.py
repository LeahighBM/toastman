import json
import pyperclip
import requests
from textual import on
from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical
from textual.containers import Container
from textual.widgets import (
    Static, 
    Footer, 
    Input, 
    Select, 
    Button, 
    Header, 
    TextArea,
    TabbedContent,
    TabPane,
    Label
)

class Toastman(App):
    CSS_PATH = "css/toastman.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("b", "toggle_sidebar", "Toggle Sidebar"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        yield Container(
            Static("https://pokeapi.co/api/v2/pokemon", id="sidebar_content"),
            id="sidebar"
        )

        with HorizontalScroll():
            yield Select(
                options = [
                    ("GET", "GET"),
                    ("POST", "POST"),
                    ("PUT", "PUT"),
                    ("DELETE", "DELETE"),
                    ("OPTIONS", "OPTIONS")
                ],
                value="GET",
                id="http_verb_select"
                
            )
            yield Input(
                placeholder="https://example.com/items",
                id="url_bar",)
            
            yield Button("SEND", variant="primary", id="send_button")

        with TabbedContent():
            yield TabPane("Tab 1", Label("Tab 1"))
            yield TabPane("POST Body", TextArea(id="post_body",language="json",))
            yield TabPane("Tab 3", Label("content"))
    
        with Container():
            yield TextArea(
                read_only=True,
                id="response_text"
                )
            yield Button("Copy to clipboard", variant="warning", id="copy")
            
        yield Footer()

    @on(Button.Pressed, "#send_button")
    @on(Input.Submitted, "#url_bar")
    def send_request(self, event) -> None:
        select_obj = self.query_one("#http_verb_select", Select)
        verb = select_obj.value

        input_obj = self.query_one("#url_bar", Input)
        url = input_obj.value
        print(verb, url)

        # the smart thing to do would be to check that the URL is not None or "" before we get here
        # but I tried that and it broke everything... so we are stuck with checking for the 
        # MissingSchema for every verb  
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
                except requests.HTTPError as he:
                    self.update_text(f"An error occurred during or as a result of the last request: {he}")
            case "POST":
                try:
                    post_body_obj = self.query_one("#post_body")
                    body = post_body_obj.text
                    body = json.dumps(body)
                    resp = requests.post(url=url, data=body)
                except requests.exceptions.MissingSchema as e:
                    message = f"Missing URL. {e}"
                    self.update_text(message)
            case "OPTIONS":
                try:
                    resp = requests.options(url=url)
                    resp.raise_for_status()
                    if resp.headers.get( 'Access-Control-Allow-Methods') is not None:
                        self.update_text(resp.headers.get( 'Access-Control-Allow-Methods'))
                    else:
                        self.update_text(resp.headers)
                except requests.exceptions.MissingSchema as e:
                    message = f"Missing URL. {e}"
                    self.update_text(message)

    def on_mount(self) -> None:  
        self.theme = "dracula"

    @on(Button.Pressed, "#copy")
    def copy_button_press(self, event) -> None:
        self.copy_text()

    def update_text(self, text) -> None: 
        response_text_obj = self.query_one("#response_text", TextArea)
        response_text_obj.text = text   

    def copy_text(self) -> None:
        text_obj = self.query_one("#response_text")
        text = text_obj.text 

        try:
            pyperclip.copy(text=text)
            self.notify("Copied to clipboard.")
        except pyperclip.PyperclipException as e:
            self.notify(f"Could not copy to clipboard. {e}")

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar")
        sidebar.toggle_class("visible")

if __name__ == "__main__":
    Toastman().run()
