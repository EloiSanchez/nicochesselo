import json
import requests
import chess.pgn as pgn
from chess import IllegalMoveError
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


# TODO: Get game by ID
def get_games(usernames, n = 100):
    usernames = [usernames] if type(usernames) == str else usernames

    game_info_params = {
        'max' : f'{n}',
        'perfType' : ','.join(DEFAULT_GAME_TYPES),
        'evals' : 'false',
        'opening': 'true'
    }

    games = []
    for user in usernames:
        print(f'getting {user}')
        games += _parse_games(
            requests.get(f'https://lichess.org/api/games/user/{user}',
                         params = game_info_params)
        )
    return games


def _parse_games(response):
    games = []
    with io.StringIO(response.text) as games_text:
        while True:
            # TODO: Silence errors
            game = pgn.read_game(games_text)

            if game is None:
                break

            if len(game.errors) > 0:
                continue

            games.append(game)
    return games


def get_default_games(n_users=200, n_games=100):
    return get_games(
        # get_leaderboard(n=n_users).union(get_streamers()),
        get_leaderboard(n=n_users).union(),
        n=n_games
        )


def get_player_info(username):
    return _resp_to_json(requests.get(f'https://lichess.org/api/user/{username}'))