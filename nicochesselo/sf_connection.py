import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import lichess_api


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
    for game in game_list:
        # Get players information
        players = players.union((game.headers['White'], game.headers['Black']))
        # games = games.union({})

        try:
            game_id = game.headers['Site'].split(".org/")[1][0:8]
            games = games.union(
                ((game_id,
                game.headers['Event'],
                game.headers['White'],
                game.headers['Black'],
                game.headers['Opening'],
                game.headers['Result'],
                None if game.headers['WhiteElo'] =='?' else game.headers['WhiteElo'],
                None if game.headers['BlackElo'] =='?' else game.headers['BlackElo'],
                game.headers['Date']),)
            )

            # Get move information
            info_moves = str(game.mainline()).split()

            for i in range(0, len(info_moves), 3):
                next_move = info_moves[i:i+3]
                if next_move[0][0] in '123456789' and len(next_move) == 3:
                    move_num, white, black = info_moves[i:i+3]
                    moves_to_add = (
                        (game_id, f'{move_num[:-1]}w', white),
                        (game_id, f'{move_num[:-1]}b', black),
                    )
                # When the last move is made by white
                elif next_move[0][0] in '123456789' and len(next_move) == 2:
                    move_num, white = info_moves[i:i+2]
                    moves_to_add = ((game_id, f'{move_num[:-1]}w', white), )
                else:
                    break

                moves = moves.union(moves_to_add)
        except Exception:
            pass

        # Get opening information
        try:
            openings = openings.union(((game.headers['Opening'], game.headers['ECO']), ))
        except Exception:
            pass

    return players, games, moves, openings


def restart_database():
    valid_answer = False
    print('WARNING: This will delete all records from the database')
    while not valid_answer:
        answer = input('Are you sure? [Y/N] >> ').strip().lower()
        if answer.startswith('n'):
            valid_answer = True
            print('Cancelled')
            return

        elif answer.startswith('y'):
            valid_answer = True
            try:
                con.execute_string('TRUNCATE moves;')
                con.execute_string('TRUNCATE players;')
                con.execute_string('TRUNCATE games;')
                con.execute_string('TRUNCATE openings;')
                print('Database cleaned succesfully.')
            except Exception:
                print('There was an error cleaning up the database.')
        else:
            print('Provide a valid answer.')


def populate_database(n_users = 200, n_games = 100):
    add_games(lichess_api.get_default_games(n_users, n_games))