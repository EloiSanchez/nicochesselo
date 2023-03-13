import json
import requests
import chess.pgn as pgn
import io


DEFAULT_GAME_TYPES = ('classical', 'rapid', 'blitz', 'bullet')


def _resp_to_json(response):
    return json.loads(response.text)


def _get_usernames(json_list, field = 'username'):
    return set(x[field] for x in json_list)


def get_leaderboard(
    game_types = ('classical', 'rapid', 'blitz', 'bullet'), n=200
    ):
    users = set()
    for game_type in game_types:
        users = users.union(_get_usernames(_resp_to_json(
            requests.get(f'https://lichess.org/api/player/top/{n}/{game_type}')
            )['users']))
    return users


def get_streamers():
    return set(_get_usernames(_resp_to_json(
        requests.get(f'https://lichess.org/api/streamer/live')
        ), 'name'))


def get_games(usernames, n = 100):
    usernames = [usernames] if type(usernames) == str else usernames

    game_info_params = {
        'max' : f'{n}',
        'perfType' : ','.join(DEFAULT_GAME_TYPES),
        'evals' : 'false'
    }

    games = []
    for user in usernames:
        print(f'getting {user}')
        games.append(_parse_games(
            requests.get(f'https://lichess.org/api/games/user/{user}',
                         params = game_info_params)
        ))
    return games


def _parse_games(response):
    games = []
    with io.StringIO(response.text) as games_text:
        while True:
            game = pgn.read_game(games_text)

            if game is None:
                break

            games.append(game)
    return games


def get_default_games(n_users=200, n_games=100):
    return get_games(
        get_leaderboard(n=n_users).union(get_streamers()),
        n=n_games
        )