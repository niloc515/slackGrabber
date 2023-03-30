from SlackWorker import SlackWorker, oath_exists

import datetime

from kivy.app import App
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.settings import SettingsWithSidebar
from kivy.config import Config
from kivy.storage.jsonstore import JsonStore
from kivy.logger import Logger


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SlackGrabber(GridLayout):
    info_text = StringProperty('Program Started')
    api_key = StringProperty('')
    file_path = StringProperty('')
    channels = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore(App.get_running_app().user_data_dir + '/app_data.json')
        if 'app_info' in self.store:
            self.api_key = self.store['app_info']['api_key']
            self.channels = self.store['app_info']['channels']
        else:
            # set some default values for the app on first run
            self.store['app_info'] = {
                'api_key': 'xoxb-...-...-...',
                'channels': 'general',
                'last_fetch': 1375336800.0
            }
        self._popup = None
        self.worker = None

    def dismiss_popup(self):
        self._popup.dismiss()

    def save(self, path, filename):
        self.file_path = path + '/' + filename
        channels_str = self.ids.channels_input_text.text
        info_temp = self.store['app_info']
        info_temp['channels'] = channels_str
        self.store['app_info'] = info_temp
        joined_channels, unjoined_channels, message = self.worker.join_channels(channels_str.split(', '))
        if len(unjoined_channels) > 0:
            self.new_message(message)
        else:
            channel_names = ', '.join([joined_channel['name'] for joined_channel in joined_channels])
            self.new_message(f'Channels {channel_names} joined')

        self.worker.download_files_from_channels(joined_channels, self.file_path, messanger=self.new_message)
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
            info_temp = self.store['app_info']
            info_temp['api_key'] = input_text
            self.store['app_info'] = info_temp
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
        Formats and adds a message to the messages scroll field.
        Message is also added to the Kivy logs as well.
        TODO: prepend the message with the time the message was added
        """
        now = datetime.datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        message = f"{formatted_date}: {text}"
        Logger.info(message)
        self.info_text += '\n' + message


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
        with open('settings.json', 'r') as file:
            json_settings = file.read()
        settings.add_json_panel('Settings', Config, data=json_settings)

    def on_stop(self):
        Config.write()


if __name__ == '__main__':
    SlackGrabberApp().run()
