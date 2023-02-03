from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
import requests
import os
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def oath_exists(token: str) -> (str, bool):
    """
    Tests to ensure the OAuth token exists and begins with the string 'xoxb'.
    All Slack tokens begin with 'xoxb'
    TODO: add further validation on inside text segments to check for alpha numerics
    """
    if not (token and token.split('-')[0] == 'xoxb'):
        return 'Invalid OAuth token. Please check value of SLACK_OAUTH', False
    else:
        return 'Valid token', True


class SlackGrabber(GridLayout):
    info_text = StringProperty('Program Started')
    api_key = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_validate_input(self, widget):
        """
        Handles the enter key press after entering the api key
        """
        self.on_key_add_click()

    def on_key_add_click(self):
        """
        Handles key press, validates the key is valid, if valid, unlocks
        the get files button
        """
        input_text = self.ids.key_input_text.text
        message, status = oath_exists(input_text)
        self.new_message('Button Clicked')
        self.new_message(message)
        self.ids.get_files_button.disabled = not status

    def on_get_files_click(self):
        """
        Initiates the fetching of all the files.
        - function must get the ids for the conversations using chanel names
        - Join the chanels
            - note that the bot may already have joined channels in the past, revist this later
        - Download the files from each channel and place it in an appropriate file
        """
        self.new_message('Get Files Pressed')

    def new_message(self, text):
        """
        Formats and adds a message to the messages scroll field
        TODO: prepend the message with the time the message was added
        """
        self.info_text += '\n' + text

class SlackGrabberApp(App):
    pass


if __name__ == "__main__":
    SlackGrabberApp().run()
