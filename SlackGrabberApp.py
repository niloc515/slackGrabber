from SlackWorker import SlackWorker

from kivy.app import App
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.settings import SettingsWithSidebar
from kivy.config import Config


def oath_exists(token: str) -> (str, bool):
    """
    Tests to ensure the OAuth token exists and begins with the string 'xoxb'.
    All Slack tokens begin with 'xoxb'
    TODO: Maybe move to SlackWorker
    TODO: add further validation on inside text segments to check for alpha numerics
    """
    if not (token and token.split('-')[0] == 'xoxb'):
        return 'Invalid OAuth token. Please check value of SLACK_OAUTH', False
    else:
        return 'Valid token', True


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SlackGrabber(GridLayout):
    info_text = StringProperty('Program Started')
    api_key = StringProperty('')
    file_path = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Config.read('slackgrabber.ini')
        self.api_key = Config.get('Slack Channel Info', 'api_key', fallback='xoxb-...-...-...')
        self._popup = None
        self.worker = None

    def dismiss_popup(self):
        self._popup.dismiss()

    def save(self, path, filename):
        self.file_path = path + '/' + filename
        channels_str = self.ids.channels_input_text.text
        joined_channels, unjoined_channels, message = self.worker.join_channels(channels_str.split(', '))
        if len(unjoined_channels) > 0:
            self.new_message(message)
        else:
            self.new_message('All channels joined')

        self.worker.download_files_from_channels(joined_channels, self.file_path)
        self.new_message('save button pushed')
        self.dismiss_popup()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title='Select folder to save files to', content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

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
        if status:
            self.api_key = input_text
            self.worker = SlackWorker(self.api_key)
            Config.set('Slack Channel Info', 'api_key', input_text)
        self.new_message('Button Clicked')
        self.new_message(message)
        self.ids.get_files_button.disabled = not status

    def on_get_files_click(self):
        """
        Launches the file selector popup, logs a message to the user that the button was pressed
        """
        self.new_message('Get Files Pressed')
        self.show_save()

    def new_message(self, text):
        """
        Formats and adds a message to the messages scroll field
        TODO: prepend the message with the time the message was added
        """
        self.info_text += '\n' + text


class SlackGrabberApp(App):

    def build(self):
        """
        Read in the settings a build the application.
        """
        self.settings_cis = SettingsWithSidebar
        return SlackGrabber()

    def build_settings(self, settings):
        """
        Construct the file
        """
        with open('./settings.json', 'r') as file:
            json_settings = file.read()
        settings.add_json_panel('Settings', Config, data=json_settings)

    def on_stop(self):
        Config.write()


if __name__ == '__main__':
    SlackGrabberApp().run()
