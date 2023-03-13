import json
import requests


def _resp_to_json(response):
    return json.loads(response.text)


def _get_usernames(json_list, field = 'username'):
    return set(x[field] for x in json_list)


def get_leaderboard(n, game_types = ('classical', 'rapid', 'blitz', 'bullet')):
    for game_type in game_types:
        yield _get_usernames(_resp_to_json(
            requests.get(f'https://lichess.org/api/player/top/{n}/{game_type}')
            )['users'])


def get_streamers():
    return _get_usernames(_resp_to_json(
        requests.get(f'https://lichess.org/api/streamer/live')
        ), 'name')


