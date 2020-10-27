import os


def load_secrets():
    secrets = {
        "slack": {
            "slack_bot_token": os.environ['SLACK_BOT_TOKEN'],
            "slack_signing_secret": os.environ['SLACK_SIGNING_SECRET']
        }
    }

    return secrets
