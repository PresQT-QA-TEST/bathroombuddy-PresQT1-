import random

from utterances import cached_responses
from utterances import hidden_gems
from utterances import known_utterances

from external_services import bathroombuddy_integration
from configs import config_loader

configs = config_loader.load_configs()


def known_utterance_handler(slack_client, message, channel):
    if "lyrics" in message:
        message_string = bathroombuddy_integration.song_lyrics(message)
        slack_client.api_call("chat.postMessage",
                              channel=channel, text=message_string)
        return

    for entry in known_utterances.utterance_types:
        if entry.get("utterance") in message:
            message_string = get_utterance_response(message, entry.get("type"))
            slack_client.api_call("chat.postMessage",
                                  channel=channel, text=message_string)
            return


def get_utterance_response(message, utterance_type):
    if utterance_type == "help":
        return cached_responses.help_response
    elif utterance_type == "weather":
        return bathroombuddy_integration.get_weather_south_bend(message)

    elif utterance_type == "uk time":
        return bathroombuddy_integration.get_uk_time(message)

    elif utterance_type == "mlb scores":
        return bathroombuddy_integration.get_mlb_scores(message)

    elif utterance_type == "nhl scores":
        return bathroombuddy_integration.get_nhl_scores(message)

    elif utterance_type == (":coronavirus:"):
        return bathroombuddy_integration.get_indiana_covid_stats(message)

    elif utterance_type == ("m" or "M"):
        return bathroombuddy_integration.get_bathroom_buddy_mens_status(message)

    elif utterance_type == ("w" or "W"):
        return bathroombuddy_integration.get_bathroom_buddy_womens_status(message)
    elif utterance_type == "chuck norris":
        return bathroombuddy_integration.chuck_norris_jokes(message)
    elif utterance_type == 'advice':
        return bathroombuddy_integration.random_advice(message)

    return ""


def hidden_gem_handler(slack_client, message, channel):
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=hidden_gems.hidden_gems.get(message))


def cached_response_handler(slack_client, channel):
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=cached_responses.confused[random.randrange(
                              len(cached_responses.confused))])
