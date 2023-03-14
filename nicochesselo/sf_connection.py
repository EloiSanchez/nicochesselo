import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import lichess_api
import os


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

    games = [games] if type(games) == tuple else games
 
    df = pd.DataFrame(games, columns=('GAME_ID','EVENT', 'WHITE_PLAYER_ID','BLACK_PLAYER_ID','OPENING_ID','RESULT','WHITE_ELO','BLACK_ELO','DATE'))
    print(df.to_string())
    write_pandas(con, df, 'GAMES')

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

        try:
            games = games.union(
                ((game.headers['Site'].split(".org/")[1][0:8],
                game.headers['Event'],
                game.headers['White'],
                game.headers['Black'],
                game.headers['Opening'],
                game.headers['Result'],
                None if game.headers['WhiteElo'] =='?' else game.headers['WhiteElo'],
                None if game.headers['BlackElo'] =='?' else game.headers['BlackElo'],
                game.headers['Date']),)
            ) 
        except Exception:
            game.headers['Site'] = "NULL"
        
        
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


# TODO: Probably not used
def get_players(game):
    return {'white': game.headers['White'],
            'black': game.headers['Black']}