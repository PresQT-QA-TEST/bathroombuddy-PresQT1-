from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
from flask import Flask, jsonify
import re

from configs import config_loader
from secrets import secret_loader

from utterances import hidden_gems
from utterances import known_utterances
from utterances import utterance_handler


app = Flask(__name__)

bathroom_buddy_slack_secrets = secret_loader.load_secrets().get("slack")
bathroom_buddy_configs = config_loader.load_configs()

slack_events_adapter = SlackEventAdapter(
    bathroom_buddy_slack_secrets.get(
        "slack_signing_secret"), "/slack/events", app)
slack_client = SlackClient(bathroom_buddy_slack_secrets.get("slack_bot_token"))


@app.route("/alive")
def alive():
    return jsonify({"health": "Bathroom Buddy is ALIIIIIIVE."})


@app.route("/configs")
def configs():
    return jsonify(bathroom_buddy_configs)


@slack_events_adapter.on("app_mention")  # Subscribe to app mentions
@slack_events_adapter.on("message")  # Subscribe to direct messages
def handle_message(event_data):
    message = event_data["event"]
    channel = message["channel"]

    # Strip off the bot id from the message
    message_from_event = message.get('text')
    clean_message = re.sub(r'<@.........> ', '', message_from_event)

    # Check to see if this is a direct match to an utterance we know how to handle.
    if message.get("subtype") is None and clean_message in \
       known_utterances.known_utterances:
        utterance_handler.known_utterance_handler(
            slack_client, clean_message, channel)

    # Check to see if this is a direct match to a hidden gem...
    elif message.get("subtype") is None and clean_message in \
            hidden_gems.hidden_gems and bathroom_buddy_configs.get(
            "hidden_gems").get("enable"):
        utterance_handler.hidden_gem_handler(
            slack_client, clean_message, channel)

    # Return an 'I Don't Know' response
    elif message.get("subtype") is None and bathroom_buddy_configs.get(
            "cached_response").get("enable"):
        utterance_handler.cached_response_handler(slack_client, channel)


@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: {}".format(err))
