import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import lichess_api
from datetime import datetime

con = snowflake.connector.connect(
    user='chess_user',
    password='ChessAPI_Elo',
    account='NE01301.switzerland-north.azure',
    warehouse='CHESS_WH',
    database='CHESS_DB',
    schema='CHESS_SCH'
)

cur = con.cursor()

def add_games(game_list):

    print(f'Preparing {len(game_list)} games to add to database')

    players, games, moves, openings = _get_games_info(game_list)

    df = pd.DataFrame(games, columns=('GAME_ID','EVENT', 'WHITE_PLAYER_ID','BLACK_PLAYER_ID','OPENING_ID','RESULT','WHITE_ELO','BLACK_ELO','GAME_DATE'))

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


def _get_event(event_name):
    event_name = event_name.lower()
    if 'classical' in event_name:
        return 'classical'
    elif 'rapid' in event_name:
        return 'rapid'
    elif 'blitz' in event_name:
        return 'blitz'
    elif 'bullet' in event_name:
        return 'bullet'
    else:
        event_name

def _get_games_info(game_list):
    players, games, moves, openings = [], [], [], []
    total_games = len(game_list)
    print_values = [i for i in range(0, total_games, total_games // 5)]
    for game_num, game in enumerate(game_list):
        # Get players information
        players.append(game.headers['White'])
        players.append(game.headers['Black'])

        try:
            game_id = game.headers['Site'].split(".org/")[1][0:8]
            game_date = game.headers['Date'] if not game.headers['Date'].startswith('?') else game.headers['UTCDate']

            games.append(
                (game_id,
                _get_event(game.headers['Event']),
                game.headers['White'],
                game.headers['Black'],
                game.headers['Opening'],
                game.headers['Result'],
                None if game.headers['WhiteElo'] =='?' else game.headers['WhiteElo'],
                None if game.headers['BlackElo'] =='?' else game.headers['BlackElo'],
                game_date.replace('.', '-'))
            )

            # Get move information
            info_moves = str(game.mainline()).split()

            for i in range(0, len(info_moves), 3):
                next_move = info_moves[i:i+3]
                if next_move[0][0] in '123456789' and len(next_move) == 3:
                    move_num, white, black = info_moves[i:i+3]
                    moves_to_add = [
                        (game_id, f'{move_num[:-1]}w', white),
                        (game_id, f'{move_num[:-1]}b', black),
                    ]
                # When the last move is made by white
                elif next_move[0][0] in '123456789' and len(next_move) == 2:
                    move_num, white = info_moves[i:i+2]
                    moves_to_add = [(game_id, f'{move_num[:-1]}w', white), ]
                else:
                    break

                [moves.append(move) for move in moves_to_add]

            if game_num in print_values:
                print(f'Prepared {game_num} games out of {total_games}')
        except Exception:
            pass

        # Get opening information
        try:
            openings.append((game.headers['Opening'], game.headers['ECO']))
        except Exception:
            pass

    return set(players), set(games), set(moves), set(openings)


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


def populate_database(limit=-1):
    add_games(lichess_api.get_games_from_file(r'C:\Users\elois\Documents\nicochesselo\data\lichess_db_standard_rated_2013-06.pgn', limit))


def find_games(username, color, results, gamemodes, dates, elos):
    statement = "SELECT * FROM games WHERE 1=1\n"

    if username != '':
        if color == 'Any':
            statement += f"AND (white_player_id ILIKE '{username}%' "
            statement += f"OR black_player_id ILIKE '{username}%')\n"
        elif color == 'Black':
            statement += f"AND black_player_id ILIKE '{username}%'\n"
        else:
            statement += f"AND white_player_id ILIKE '{username}%'\n"

    if results != []:
        statement += f"AND result IN ({','.join(results)})\n"

    if gamemodes != []:
        statement += f"AND event IN ({','.join(gamemodes)})\n"

    statement += f"AND game_date BETWEEN '{datetime.strftime(dates[0], '%Y-%m-%d')}' AND '{datetime.strftime(dates[1], '%Y-%m-%d')}'\n"
    statement += f"AND (white_elo+black_elo)/2 BETWEEN {elos[0]} AND {elos[1]}"

    try:
        cur.execute(statement + ';')
        df = cur.fetch_pandas_all()
    except:
        df = 'ERROR in query.'

    return statement, df

def get_game_ranges():
    try:
        cur.execute("""SELECT
                           MIN(white_elo) as min_welo,
                           MAX(white_elo) as max_welo,
                           MIN(black_elo) as min_belo,
                           MAX(black_elo) as max_belo,
                           MIN(game_date) as min_date,
                           MAX(game_date) as max_date
                       FROM GAMES;""")
        df = cur.fetch_pandas_all()
    except:
        df = 'ERROR in query.'
    return {
        'min_elo': min(int(df['MIN_WELO']), int(df['MIN_BELO'])),
        'max_elo': max(int(df['MAX_WELO']), int(df['MAX_BELO'])),
        'min_date': df['MIN_DATE'].iloc[0],
        'max_date': df['MAX_DATE'].iloc[0]
    }