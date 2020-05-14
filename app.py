from slacker import Slacker
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import os
import json


token = os.environ['SLACK_TOKEN']
slack = Slacker(token)

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from marchine import lotto
from models import Wcode

@app.route("/")
def lotto_default_route():
    return "This is lotto_default_route"


def get_base_blocks(text):
    """
    convert text to slack section blocks format
    :param text: string
    :return list: slack blocks contained text
    """
    base_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    ]
    return base_blocks


def get_base_context_blocks(text):
    """
    convert text to slack context blocks format
    :param text: string
    :return list: slack blocks contained text
    """
    blocks = [
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": text}
            ]
        }
    ]
    return blocks


def get_lotto_blocks(tickets):
    """
    make match blocks with matched users' name and activity
    :param match: Match
    :return list: slack blocks that contains match guide message
    """
    last_code = Wcode.query.order_by(desc("no")).first()
    text = str(last_code.no + 1)
    text += "회차 예상 5장의 로또 티켓입니다. 대박 나세요:moneybag:!"
    blocks = get_base_blocks(text)
    ticket_blocks = {
        'type': "section",
        'fields': [
        {
            "type": "plain_text",
            "text": ":one: ",
            "emoji": True
        },
        {
            "type": "plain_text",
            "text": ":two: ",
            "emoji": True
        },
        {
            "type": "plain_text",
            "text": ":three: ",
            "emoji": True
        },
        {
            "type": "plain_text",
            "text": ":four: ",
            "emoji": True
        }]
    }
    for idx, ticket in enumerate(tickets):
        ticket_blocks['fields'][idx]['text'] += " ".join(list(map(lambda x: str(x), ticket)))
    blocks.append(ticket_blocks)
    return blocks


def send_guide_message(form):
    """
    send message that guide where to check direct message
    :param form: payload from slack slash command
    """
    slack_id = form.getlist('user_id')[0]
    call_channel = form.getlist('channel_id')
    eph_blocks = get_base_context_blocks("메시지가 전송되었습니다. Apps에서 'glotto'를 확인해주세요!")
    slack.chat.post_ephemeral(channel=call_channel, text="", user=[slack_id], blocks=json.dumps(eph_blocks))


@app.route("/slack/command", methods=['POST'])
def command_main():
    """
    Send 5 Lotto tickets
    first, second ticket = pattern algorithm
    third ticket = exclude often recent numbers
    fourth ticket = include often recent numbers
    fifth ticket = exclude most recent numbers
    :return: http 200 status code
    """
    form = request.form
    channel_name = form.getlist('channel_name')[0]
    if channel_name != "directmessage" and channel_name != "privategroup":
        send_guide_message(form)
    slack_id = form.getlist('user_id')[0]
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    tickets = lotto()
    blocks = get_lotto_blocks(tickets)
    slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))
    return ("", 200)


if __name__ == "__main__":
    app.run()
