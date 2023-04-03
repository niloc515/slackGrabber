import requests
from datetime import datetime
import os
import time
from dateutil.relativedelta import relativedelta


def make_directory(dir_name: str):
    """
    For creating directories. See https://stackoverflow.com/questions/1274405/how-to-create-new-folder
    """
    try:
        os.makedirs(dir_name)
    except OSError:
        pass
    # let exception propagate if we just can't
    # cd into the specified directory
    os.chdir(dir_name)
    return os.getcwd()


def oath_exists(token: str) -> (str, bool):
    """
    Tests to ensure the OAuth token exists and begins with the string 'xoxb'.
    All Slack tokens begin with 'xoxb'
    """
    error_text = 'Invalid OAuth token. Please check your input'
    token_components = token.split('-')
    if not (token_components[0] == 'xoxb'):
        return error_text, False
    else:
        for token in token_components[1:]:
            if not token.isalnum():
                return error_text, False
        return 'Valid token', True


class SlackWorker:
    BASE_URL = 'https://slack.com/api/'
    CONVERSATIONS_LIST_URL = BASE_URL + 'conversations.list'
    CONVERSATIONS_JOIN_URL = BASE_URL + 'conversations.join?channel='
    FILES_LIST_URL = BASE_URL + 'files.list'

    def __init__(self, token: str):
        self.oauth_token = token

    def get_conversation_id(self, channels):
        """
        Gets the list of slack channels, returns the lis of channel objects for the relevant channels
        """
        res = self.slack_request(self.CONVERSATIONS_LIST_URL)

        if res['ok']:
            relevant_channels = list(filter(lambda channel: (channel['name'] in channels), res['channels']))
            if relevant_channels:
                return relevant_channels
            else:
                raise Exception('There are no channels found under the names: ' + channels)
        else:
            raise Exception('Error occured: \n' + res['error'])

    def join_channels(self, channels: list) -> (list, list, str):
        """
        Joins the channels given to the method
        This is necessary in order to see the information about all the files in a given channel.
        """
        joined_channels = []
        unjoined_channels = []
        message = ''

        channels_info = self.get_conversation_id(channels)

        for channel in channels_info:
            res = self.slack_request(self.CONVERSATIONS_JOIN_URL + channel['id'])
            if res['ok']:
                joined_channels.append(channel)
            else:
                unjoined_channels.append(channel)
                message += 'unable to join channel with name: ' + channel['name'] + ' for reason ' + res['error'] + '\n'

        return joined_channels, unjoined_channels, message

    def slack_request(self, url: str):
        """
        Simple function that makes a slack request and returns a json object
        """
        api_call_headers = {'Authorization': 'Bearer ' + self.oauth_token}
        return requests.get(url, headers=api_call_headers).json()

    def download_file(self, file, current_folder):
        """
        Takes a single file object (as returned by the slack files.list api)
        and downloads that file and places it in the appropriate directory
        """
        time_file_created = datetime.fromtimestamp(file['timestamp'])
        api_call_headers = {'Authorization': 'Bearer ' + self.oauth_token}
        r = requests.get(file['url_private'], headers=api_call_headers)

        open(file['title'], 'wb').write(r.content)
        mod_time = time.mktime(time_file_created.timetuple())
        os.utime(current_folder + '/' + file['title'], (mod_time, mod_time))

    def download_files_from_channels(self, joined_channels: list, start_folder, months=1, messanger=None):
        """
        Downloads all the files from a given list of channels in the past number of months
        TODO: start grabbing files from the time of the most recently downloaded file
        """
        current_time = datetime.now().strftime('%Y-%m-%d')
        download_from_ts = (datetime.now() - relativedelta(months=months)).timestamp()
        root_folder = make_directory(start_folder + 'Slack_' + current_time)

        for channel in joined_channels:
            make_directory(channel['name'] + '_' + current_time)
            current_folder = os.getcwd()
            next_page = 1
            while True:
                res = self.slack_request(
                    f'{self.FILES_LIST_URL}?page={next_page}&channel={channel["id"]}&ts_from={str(download_from_ts)}')
                for file in res['files']:
                    if messanger:
                        messanger(f'Downloading file "{file["title"]}"')
                    self.download_file(file, current_folder)
                if next_page <= res['paging']['pages']:
                    if messanger:
                        messanger('Files finished downloading')
                    break
                else:
                    next_page += 1
            os.chdir(root_folder)
