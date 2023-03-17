import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import lichess_api
from datetime import datetime
import os


file_dir =  os.path.dirname(os.path.realpath(__file__))

# Get SF connection and cursor
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
    """Addes a list of games to the SF database

    Args:
        game_list (list[chess.Game]): list of chess.Games to add to database
    """
    print(f'Preparing {len(game_list)} games to add to database')

    # Get the required information from the game list
    players, games, moves, openings = _get_games_info(game_list)

    # Add the data to the different tables

    df = pd.DataFrame(games, columns=('GAME_ID','EVENT', 'WHITE_PLAYER_ID','BLACK_PLAYER_ID','OPENING_ID','RESULT','WHITE_ELO','BLACK_ELO','GAME_DATE'))

    write_pandas(con, df, 'GAMES')
    add_players(players)
    add_openings(openings)
    add_moves(moves)
    


def add_players(players):
    """Adds player rows to players table

    Args:
        players (set[tuple]): set of tuples with the row information
    """
    players = [players] if type(players) == str else players

    df = pd.DataFrame(players, columns=('PLAYER_ID',))
    write_pandas(con, df, 'PLAYERS')



def add_openings(openings):
    """Adds opening rows to openings table

    Args:
        players (set[tuple]): set of tuples with the row information
    """
    openings = [openings] if type(openings) == tuple else openings

    df = pd.DataFrame(openings, columns=('OPENING_ID', 'ECO'))
    write_pandas(con, df, 'OPENINGS')


def add_moves(moves):
    """Adds move rows to moves table

    Args:
        players (set[tuple]): set of tuples with the row information
    """
    df = pd.DataFrame(moves, columns=('GAME_ID','MOVE_ID', 'MOVE'))
    write_pandas(con, df, 'MOVES')

def _get_event(event_name):
    """Parses the event information and returns the value to be stored in SF

    Args:
        event_name (str): Event name

    Returns:
        str: cleaned event name
    """
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
    """Parses list of games in chess.Game format and obtains the tuples to be
    added to the database

    Args:
        game_list (list[chess.Game]): list of games to be parsed

    Returns:
        tuple[set[tuple]]: parsed sets of tuples to be added to database
    """
    players, games, moves, openings = [], [], [], []

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

        except Exception:
            pass

        # Get opening information
        try:
            openings.append((game.headers['Opening'], game.headers['ECO']))
        except Exception:
            pass

    return set(players), set(games), set(moves), set(openings)


def restart_database():
    """Deletes all record from the database"""
    con.execute_string('TRUNCATE moves;')
    con.execute_string('TRUNCATE players;')
    con.execute_string('TRUNCATE games;')
    con.execute_string('TRUNCATE openings;')
    print('Database cleaned succesfully.')


def populate_database(limit=-1):
    """Populated the database with a set of games obtained from a file
    downloaded from the lichess database

    Args:
        limit (int, optional): Amount of games to get. If negative, gets
        all games from the file. Defaults to -1.
    """
    data_path = os.path.join(file_dir,
                             r"..\data\lichess_db_standard_rated_2013-06.pgn")
    add_games(lichess_api.get_games_from_file(data_path, limit))


def add_games_by_hand(game_hand):
    df = pd.DataFrame(game_hand, index=[0])
    write_pandas(con, df, 'GAMES')
    add_players_hand(game_hand['WHITE_PLAYER_ID'])    
    add_players_hand(game_hand['BLACK_PLAYER_ID'])


def add_players_hand(players):
    players = {'PLAYER_ID' : players}
    df = pd.DataFrame(players, index=[1])
    write_pandas(con, df, 'PLAYERS')


def add_openings_hand(opening_name, opening_eco):
    openings ={'OPENING_ID': opening_name , 'ECO' :opening_eco}
    df = pd.DataFrame(openings, index =[0])
    write_pandas(con, df, 'OPENINGS')


def add_moves_hand(moves):    
    df = pd.DataFrame(moves, index =[0])
    write_pandas(con, df, 'MOVES')



def find_games(username, color, results, gamemodes, dates, elos):
    """Queries the games databse to obtain a set of games that fulfil a set of
    conditions

    Args:
        username (str): database user_id
        color (str): color of the user_id player
        results (tuple): end game results
        gamemodes (tuple): different time modes
        dates (tuple): range of time
        elos (tuple): range of elos

    Returns:
        (str, pd.DataFrame): the statement used and the dataframe obtained
    """
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
    """
    Obtains the min and max values of the ranges input variables for the user

    Returns:
        dict: The min and max values to be used by streamlit
    """
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






