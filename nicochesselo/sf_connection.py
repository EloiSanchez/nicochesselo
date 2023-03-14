import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import lichess_api
import os

# os.environ["SNOWSQL_PWD"] = "ChessAPI_Elo"
# os.environ["SNOWSQL_USR"] = "chess_user"
# os.environ["SNOWSQL_ACC"] = "NE01301.switzerland-north.azure"
# os.environ["SNOWSQL_WH"] = "CHESS_WH"
# os.environ["SNOWSQL_DB"] = "CHESS_DB"
# os.environ["SNOWSQL_SCH"] = "CHESS_SCH"

con = snowflake.connector.connect(
    user='chess_user',
    password='ChessAPI_Elo',
    account='NE01301.switzerland-north.azure',
    warehouse='CHESS_WH',
    database='CHESS_DB',
    schema='CHESS_SCH'
)

def add_games(games):
    players, games, moves, openings = _get_games_info(games)
    add_players(players)
    add_openings(openings)
    add_moves(moves)


def add_players(players):
    players = [players] if type(players) == str else players

    df = pd.DataFrame(players, columns=('PLAYER_ID',))
    write_pandas(con, df, 'PLAYERS')


def add_openings(openings):
    openings = [openings] if type(openings) == tuple else openings

    df = pd.DataFrame(openings, columns=('OPENING_ID', 'ECO'))
    write_pandas(con, df, 'OPENINGS')


def add_moves(moves):
    df = pd.DataFrame(moves, columns=('GAME_ID','MOVE_ID', 'MOVE'))
    write_pandas(con, df, 'MOVES')


def _get_games_info(game_list):
    players, games, moves, openings = set(), set(), set(), set()
    for game_id, game in enumerate(game_list):
        # Get players information
        players = players.union((game.headers['White'], game.headers['Black']))
        # games = games.union({})

        # Get opening information
        try:
            openings = openings.union(((game.headers['Opening'], game.headers['ECO']), ))
        except Exception:
            opening_id = 'NULL'

        # Get move information
        info_moves = str(game.mainline()).split()

        for i in range(0, len(info_moves), 3):
            try:
                move_num, white, black = info_moves[i:i+3]
                moves_to_add = (
                    (game_id, f'{move_num[:-1]}w', white),
                    (game_id, f'{move_num[:-1]}b', black),
                )
            except ValueError:
                move_num, white = info_moves[i:i+2]
                moves_to_add = ((game_id, f'{move_num[:-1]}w', white), )

            moves = moves.union(moves_to_add)

    return players, games, moves, openings


def _parse_moves(game):
    info_moves = str(game.mainline()).split()
    moves = set()
    for i in range(0, len(info_moves), 3):
        move_num, white, black = info_moves[i:i+3]
        moves.union(
            (
                (move_num[:-1], )
            )
        )


# TODO: Probably not used
def get_players(game):
    return {'white': game.headers['White'],
            'black': game.headers['Black']}