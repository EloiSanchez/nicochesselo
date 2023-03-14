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

    games = [games] if type(games) == tuple else games
    # add_players(players)
    # add_openings(openings)
    
    df = pd.DataFrame(games, columns=('GAME_ID','EVENT', 'WHITE_PLAYER_ID','BLACK_PLAYER_ID','OPENING_ID','RESULT','WHITE_ELO','BLACK_ELO','DATE'))
    print(df.to_string())
    write_pandas(con, df, 'GAMES')



def add_players(players):
    players = [players] if type(players) == str else players

    statement = f"INSERT INTO players(player_id) VALUES "
    statement += ','.join(f"('{player}')" for player in players) + ';'

    # print(statement)
    # con.execute_string(statement)


def add_openings(openings):
    statement = "INSERT INTO openings(opening_id, ECO) VALUES "
    statement += ','.join(
        [f"('{op['opening_id']}','{op['ECO']}')" for op in openings]
        )
    # print(statement)
    # con.execute_string(statement)



def _get_games_info(game_list):
    players, games, moves, openings = set(), set(), [], []
    for game in game_list:
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
            openings.append(
                {'opening_id': game.headers['Opening'], 
                 'ECO': game.headers['ECO']}
                )
        except Exception:
            opening_id = 'NULL'
            
        # Get move information
        # _parse_moves(game)

    return players, games, moves, openings 


def _parse_moves(game):
    info_moves = str(game.mainline()).split()
    for i in range():
        pass
    

# TODO: Probably not used
def get_players(game):
    return {'white': game.headers['White'],
            'black': game.headers['Black']}