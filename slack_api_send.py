import logging
import os
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
def get_config():
    try:
        with open('config.json') as json_file:
            json_data = json.load(json_file)
    except Exception as e:
        print('Error in reading config file, {}'.format(e))
        return None
    else:
        return json_data
# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
logger = logging.getLogger(__name__)
config = get_config()
client = WebClient(token=config['slackToken'])

def check_channel_id(channel_name):
    channel_name = channel_name
    conversation_id = None
    try:
        # Call the conversations.list method using the WebClient
        for result in client.conversations_list():
            if conversation_id is not None:
                break
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    conversation_id = channel["id"]
                    #Print result
                    print(f"Found conversation ID: {conversation_id}")
                    break

        return conversation_id

    except SlackApiError as e:
        print(f"Error: {e}")

def send_error_message(message):
    channel_id = check_channel_id('crawling-message')
    # ID of channel you want to post message to
    try:
        # Call the conversations.list method using the WebClient
        result = client.chat_postMessage(
            channel=channel_id,
            text=message
            # You could also use a blocks[] array to send richer content
        )
        # Print result, which includes information about the message (like TS)
        print(result[0])

    except SlackApiError as e:
        print(f"Error: {e}")

def upload_file():
    try:
        id = check_channel_id('dailygeneration_symphony')
        filepath_lists = [r'C:\symphony_api\original.mp4', r'C:\info\articles.txt', r'C:\info\prompt.txt']
        # filepath_lists = ['prompt.txt', 'articles.txt', 'original.mp4']
        # filepath_lists = ['original.mp4']

        for filepath in filepath_lists:
            result = client.files_upload_v2(
                channels=[id],
                file=filepath
                # You could also use a blocks[] array to send richer content
            )
            print(result)

    except SlackApiError as e:
        print(f"Error: {e}")



if __name__=='__main__':
    # id = check_channel_id('dailygeneration_symphony')
    # upload_file()
    send_error_message('testtest')
