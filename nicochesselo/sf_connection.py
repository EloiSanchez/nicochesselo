import snowflake.connector
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


def add_players(players):
    players = [players] if type(players) == str else players

    statement = f"INSERT INTO players(player_id) VALUES "
    statement += ','.join(f"('{player}')" for player in players) + ';'

    con.execute_string(statement)


def _get_games_info(game_list):
    players, games, moves, openings = set(), set(), set(), set()
    for game in game_list:
        players = players.union((game.headers['White'], game.headers['Black']))
        # games = games.union({})

    return players, games, moves, openings

# TODO: Probably not used
def get_players(game):
    return {'white': game.headers['White'],
            'black': game.headers['Black']}