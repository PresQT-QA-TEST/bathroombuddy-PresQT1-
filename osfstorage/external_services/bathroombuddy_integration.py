import requests
import datetime
import os

import paho.mqtt.subscribe as subscribe
import certifi
import mlbgame
import lxml.etree as etree


def get_nhl_scores(message):
    """
    Get yesterdays NHL scores :).
    """
    statsapi = "https://statsapi.web.nhl.com/api/v1/"
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    result = requests.get(
        "{}schedule?date={}".format(statsapi, yesterday)).json()
    try:
        games = result['dates'][0]['games']
    except IndexError:
        return("There were no NHL games yesterday :connolly:")
    scores = []
    for game in games:
        away = "{} {}\n".format(
            game['teams']['away']['team']['name'],
            game['teams']['away']['score'])
        home = "{} {}\n".format(
            game['teams']['home']['team']['name'],
            game['teams']['home']['score'])
        scores.append(away+home)

    return('\n'.join(str(score) for score in scores))


def get_bathroom_buddy_mens_status(message):
    """
    Get the Men's Bathroom status.
    """
    status = subscribe.simple(
        "Home/mens/state", hostname="m16.cloudmqtt.com",
        auth={'username': os.environ['USERNAME'],
              'password': os.environ['SLACK_PASS']},
        port=21775, tls={'ca_certs': certifi.where()})

    return(status.payload)


def get_bathroom_buddy_womens_status(message):
    """
    Get the Women's Bathroom status.
    """
    status = subscribe.simple(
        "Home/womens/state", hostname="m16.cloudmqtt.com",
        auth={'username': os.environ['USERNAME'],
              'password': os.environ['SLACK_PASS']},
        port=21775, tls={'ca_certs': certifi.where()})

    return(status.payload)


def get_weather_south_bend(message):
    """
    The following function returns the current weather for
    South Bend, IN....
    """
    weather_api = 'http://api.openweathermap.org/data/2.5/weather?id=4926563&&units=imperial&appid={}'.format(
        os.environ['WEATHER_KEY'])
    weather = requests.get(weather_api).json()

    return("The current weather at Notre Dame is {} with a temperature of {}.".format(
        weather['weather'][0]['main'], str(weather['main']['temp'])))


def get_uk_time(message):
    """
    Prometheus helper to quickly see the time in London.
    """
    time_api = 'http://worldtimeapi.org/api/timezone/Europe/London.json'
    london_time = requests.get(time_api).json()

    return("The current time in London, England is {}".format(
        london_time['datetime'][11:16]))


def scoreboard(year, month, day):
    """
    Return the scoreboard information for games matching the parameters
    as a dictionary.
    """
    # Get data from mlbgame library
    data = mlbgame.data.get_scoreboard(year, month, day)
    # Parse through returned data
    parsed = etree.parse(data)
    root = parsed.getroot()
    output = []
    # Loop through the list of games that are returned
    for game in root:
        if game.tag == 'data':
            return []
        # Get the Team Names
        teams = game.findall('team')
        home_name = teams[0].attrib['name']
        away_name = teams[1].attrib['name']
        # Building a dictionary
        # I am really only interested in the scores.... not sure if
        # game_id is actually necessary....but here it stays
        game_data = game.find('game')
        game_id = game_data.attrib['id']
        home_team_data = teams[0].find('gameteam')
        home_team = home_name
        home_team_runs = int(home_team_data.attrib['R'])
        away_team_data = teams[1].find('gameteam')
        away_team = away_name
        away_team_runs = int(away_team_data.attrib['R'])
        score = {
            'home_team': home_team,
            'home_team_runs': home_team_runs,
            'away_team': away_team,
            'away_team_runs': away_team_runs
        }
        output.append(score)
    return output


def get_mlb_scores(message):
    """
    This function will fetch yesterday's mlb scores and return them in a
    similar fashion to how nhl scores are being returned.
    """
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    games = scoreboard(yesterday.year,
                       yesterday.month,
                       yesterday.day)
    scores = []

    for game in games:
        home = "{} {}\n".format(
            game['home_team'],
            str(game['home_team_runs']))
        away = "{} {}\n".format(
            game['away_team'],
            str(game['away_team_runs']))

        scores.append(away+home)

    if len(scores) > 0:
        return('\n'.join(str(score) for score in scores))
    else:
        return ("There were no MLB games yesterday :mattstairs:")


def get_indiana_covid_stats(message):
    """
    This function gets updated Covid stats for the state of Indiana.
    """
    api_link = "https://corona.lmao.ninja/v2/states"
    get_stats = requests.get(api_link)

    for state in get_stats.json():
        if state['state'] == "Indiana":
            cases = state['cases']
            deaths = state['deaths']

    covid_message = ":coronavirus: In Indiana, there are currently {} confirmed cases of COVID-19, resulting in {} deaths. :coronavirus:".format(
        cases, deaths)

    return covid_message


def chuck_norris_jokes(message):
    """
    Returns a random Chuck Norris joke.
    """

    joke = requests.get("https://api.chucknorris.io/jokes/random").json()

    return joke['value']


def random_advice(message):
    """
    Returns a random bit of advice.
    """
    advice = requests.get("https://api.adviceslip.com/advice").json()['slip']['advice']

    return advice


def song_lyrics(message):
    """
    Return the lyrics of the song submitted.
    """
    spaceless_message = message.partition(' ')[2]
    if ":" in spaceless_message:
        # Try and find the lyrics.
        band_name = spaceless_message[0]
        song_title = spaceless_message[2]

        response = requests.get("https://api.lyrics.ovh/v1/{}/{}".format(band_name, song_title))

        if response.status_code == 404:
            return response.json()['error']
        return response.json()['lyrics']
    else:
        return ("Message not formatted correctly. Please try again using this format:\nlyrics band name:song title")
