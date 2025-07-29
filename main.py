import json
import re
import pyperclip
import requests
from parse_config import parse_saved_requests
from extended_text_area import ExtendedTextArea
from http import HTTPStatus
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
    Label,
    Collapsible
)
color_dict = {
            "GET":    "[b][green]GET[/green][/b]",
            "POST":   "[b][blue]POST[/blue][/b]",
            "PUT":    "[b][orange]PUT[/orange][/b]",
            "DELETE": "[b][red]DELETE[/red][/b]"
        }
class Toastman(App):
    CSS_PATH = "css/toastman.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("b", "toggle_sidebar", "Toggle Sidebar"),
    ]

    def compose(self) -> ComposeResult:
        with open(".saved_requests", 'r') as f:
            lines = f.read()

        with Header(show_clock=True):
            yield Button("Toggle Side[underline]b[/underline]ar", compact=True, id="toggle_side_panel_button")

        parsed = parse_saved_requests(lines)
        
        with Container(id="sidebar"):
            for k,v in parsed.items():
                with Collapsible(title=k):
                    for x in v:
                        yield Button(f"{color_dict.get(x.get("method"))} {x.get("url")}", classes="saved_request_button")
            
        with HorizontalScroll():
            yield Select(
                options = [
                    ("[b][green]GET[/green][/b]", "GET"),
                    ("[b][blue]POST[/blue][/b]", "POST"),
                    ("[b][orange]PUT[/orange][/b]", "PUT"),
                    ("[b][red]DELETE[/red][/b]", "DELETE"),
                    ("OPTIONS", "OPTIONS")
                ],
                value="GET",
                id="http_verb_select")

            yield Input(
                placeholder="https://example.com/items",
                id="url_bar",)
            
            yield Button("SEND", variant="primary", id="send_button")
        
        with TabbedContent():
            yield TabPane("Hide", Label(""))
            yield TabPane("Body", ExtendedTextArea.code_editor(id="post_body",
                                           language="json", 
                                           text="{\n\n\n}",
                                           show_line_numbers=True,
                                           tab_behavior="indent"))
            yield TabPane("Headers", ExtendedTextArea.code_editor(id="header_data",
                                                                  highlight_cursor_line=False))
    
        with Container():
            with TabbedContent(id="response_tabs"):
                yield TabPane("Response", TextArea(
                    read_only=True,
                    id="response_text",))
                yield TabPane("Header Data", TextArea(
                    read_only=True,
                    id="resp_headers"
                ))
        yield Button("Copy", variant="warning", id="copy")
            
        yield Footer()

    @on(Button.Pressed, "#send_button")
    @on(Input.Submitted, "#url_bar")
    def send_request(self, event) -> None:
        select_obj = self.query_one("#http_verb_select", Select)
        verb = select_obj.value

        input_obj = self.query_one("#url_bar", Input)
        url = input_obj.value

        # the smart thing to do would be to check that the URL is not None or "" before we get here
        # but I tried that and it broke everything... so we are stuck with checking for the 
        # MissingSchema for every verb  
        # I also hate how I have to repeat everything for each request type... I need to fix that
        match verb:
            case "GET":
                try:
                    resp = requests.get(url=url)
                    resp.raise_for_status()
                    json_data = json.dumps(resp.json(), indent=2, default=str)
                    self.update_response_text(json_data)
                    self.update_response_headers(resp.headers)

                    if resp.status_code >= 200 and resp.status_code <= 299:
                        self.notify(f"Success!", 
                                    title=f"{resp.status_code} {HTTPStatus(resp.status_code).phrase}")

                except requests.exceptions.MissingSchema as e:
                    message = f"Missing URL. {e}"
                    self.update_response_text(message)
                except requests.exceptions.ConnectionError as e:
                    self.update_response_text(f"{e}")
                except requests.RequestException as e:
                    self.update_response_text(f"{e}")
                    self.update_response_headers(resp.headers)
                    self.notify(f"Request unsuccessful. Something went wrong", 
                                severity="error",
                                title=f"{resp.status_code} {HTTPStatus(resp.status_code).phrase}")
                
            case "POST": # this is a test because why does everything have merge conflicts
                try:
                    post_body_obj = self.query_one("#post_body")
                    body = post_body_obj.text
                    body = json.dumps(body)
                    resp = requests.post(url=url, data=body)
                    resp.raise_for_status()
                    self.update_response_text(json_data)
                    self.update_response_headers(resp.headers)

                    if resp.status_code >= 200 and resp.status_code <= 299:
                        self.notify(f"Success!", 
                                    title=f"{resp.status_code} {HTTPStatus(resp.status_code).phrase}")

                except requests.exceptions.MissingSchema as e:
                    message = f"Missing URL. {e}"
                    self.update_response_text(message)
                except requests.RequestException as e:
                    self.update_response_text(f"{e}")
                    self.update_response_headers(resp.headers) # this will cause the program to hard crash in the event of a connection error
                    self.notify(f"Request unsuccessful. Something went wrong.", 
                                severity="error",
                                title=f"{resp.status_code} {HTTPStatus(resp.status_code).phrase}")

            case "OPTIONS":
                try:
                    resp = requests.options(url=url)
                    resp.raise_for_status()

                    if resp.status_code >= 200 and resp.status_code <= 299:
                        self.notify(f"{resp.status_code} success!")

                    if resp.headers.get( 'Access-Control-Allow-Methods') is not None:
                        self.update_response_text(resp.headers.get( 'Access-Control-Allow-Methods'))

                    self.update_response_headers(resp.headers)
                except requests.exceptions.MissingSchema as e:
                    message = f"Missing URL. {e}"
                    self.update_response_text(message)
                except requests.RequestException as e:
                    self.update_response_text(f"{e}")
                    self.update_response_headers(resp.headers)
                    self.notify(f"Request unsuccessful. Something went wrong.", 
                                severity="error",
                                title=f"{resp.status_code} {HTTPStatus(resp.status_code).phrase}")

    def on_mount(self):  
        self.theme = "dracula"

    @on(Button.Pressed, "#copy")
    def copy_button_press(self, event) -> None:
        self.copy_text()  


    @on(Button.Pressed, ".saved_request_button")
    def populate_url_data(self, event) -> None:
        url_bar = self.query_one("#url_bar", Input)
        select_obj = self.query_one("#http_verb_select", Select)
        s = event.button.label.split(" ")
        select_obj.value = s[0]
        url_bar.value = str(s[1])


    @on(Button.Pressed, "#toggle_side_panel_button")
    def toggle_side_bar_from_header_bar(self, event) -> None:
        self.action_toggle_sidebar()

    def update_response_text(self, text) -> None: 
        response_text_obj = self.query_one("#response_text", TextArea)
        response_text_obj.text = text
        response_text_obj.highlight_cursor_line = False

    def update_response_headers(self, header_dict) -> None:
        response_head_obj = self.query_one("#resp_headers", TextArea)
        for k,v in header_dict.items():
            response_head_obj.insert(f"{k}: {v}\n")
        response_head_obj.cursor_location = (0,0)
        response_head_obj.highlight_cursor_line = False

    def copy_text(self) -> None:
        resp_tab      = self.query_one("#response_tabs")
        active_tab    = resp_tab.active 
        child_tab_obj = self.query_one("#response_text") if active_tab == "tab-1" else self.query_one("#resp_headers")
        active_text   = child_tab_obj.text 

        try:
            pyperclip.copy(text=active_text)
            self.notify("Copied to clipboard.")
        except pyperclip.PyperclipException as e:
            self.notify(f"Could not copy to clipboard. {e}")

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar")
        sidebar.toggle_class("visible")

if __name__ == "__main__":
    Toastman().run()
