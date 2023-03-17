import streamlit as st
import sf_connection
import lichess_api
import datetime
import chess.pgn
import chess
import pandas as pd
"""
# Get Data from Lichess or Upload a Game

Here you will be able to look for specific games, whether by ID or by user and load them into the database.

"""
if 'input_mvs' not in st.session_state:
    st.session_state.disabled = True

if 'input_gid' not in st.session_state:
    st.session_state.disabled_add_game = True

def test_func():

        board = chess.Board()
        txt = Moves
        x = txt.split(",")
        x = board.variation_san([chess.Move.from_uci(m) for m in x]) 
        x = str(x).split()
        moves = []
        move_id = []
        for a in range(len(x)):
            if a%3 != 0:
                moves.append(x[a])
                if a%3 ==1:
                    move_id.append(x[a-1]+'w')
                else:
                    move_id.append(x[a-2]+'b')

        list_x =[]
        list_x.append(moves)
        list_x.append(move_id)
            
           
        game_param = {'GAME_ID' : Game_Id, 'EVENT': Event,'WHITE_PLAYER_ID': White_ID, 'BLACK_PLAYER_ID':Black_ID,'OPENING_ID':st.session_state.op_name,
        'RESULT':Result, 'WHITE_ELO' :WhiteElo,'BLACK_ELO': BlackElo,'GAME_DATE': Date}
        sf_connection.add_games_by_hand(game_param)        # opening_param = {'OPENING_ID' : name, 'ECO' : eco}
        sf_connection.add_openings_hand(st.session_state.op_name, st.session_state.op_eco)
       

        for n in range(len(move_id)):
            add_moves={'GAME_ID': Game_Id , 'MOVE_ID': list_x[1][n], 'MOVE':list_x[0][n]}
            sf_connection.add_moves_hand(add_moves)

def opening_func():
    ECO,Opening  = lichess_api.get_opening_by_moves(Moves) 
    print (f"OPENING {ECO},{Opening}")
    st.session_state.op_name = Opening; 
    st.session_state.op_eco = ECO;


st.button('Populate Databse', on_click=sf_connection.populate_database)

if "op_name" not in st.session_state:
    Opening = st.session_state.op_name = 'Wait for moves'
if "op_eco" not in st.session_state:
    ECO = st.session_state.op_eco = '...'


col1, col2 = st.columns(2)

with col1:
    st.header("Search by UserId")
    with st.form('Form1'):
        name =  st.text_input('Insert UserID',key ="input_text_user_sub")
        num_games = st.slider(f'How many games by the user?', 1, 130, 10)
        submit_user = st.form_submit_button('Upload')

if submit_user:
    get_game_ = lichess_api.get_games(name ,num_games)
    if get_game_ == 0:
         st.error("THIS USER DOESN'T EXISTS")
    else:
        sf_connection.add_games(get_game_)

with col2:
    st.header("Search by GameID")
    with st.form('Form2'):
        game = st.text_input('Insert GameID',key ="input_game" )
        submit_game = st.form_submit_button('Upload')

if submit_game:
    get_game_ = lichess_api.get_games_ID(st.session_state.input_game)
    if get_game_ == 0:
         st.error("THIS GAME DOESN'T EXISTS")
    else:
     sf_connection.add_games(get_game_)




st.header("Insert a game by Hand - All fields are mandatory")
col4, col3 = st.columns(2)

with st.form('Form3'):

    with col4:

        st.header("Search Opening")

        Moves = st.text_input('Insert Moves in UCI format (ex-d2d4,d7d5,c2c4,c7c6,c4d5)',key ="input_mvs" )
        st.write("Opening name:", st.session_state.op_name)
        st.write("Opening ECO: ", st.session_state.op_eco)
        

        opg_button = st.button("Find Opening", on_click=opening_func, disabled=st.session_state.disabled)
        
        if len("input_mvs") > 0:
            st.session_state.disabled = False
        else:
            st.session_state.disabled = True


    with col3:
       
        st.header("Insert Game params ")

        Game_Id = st.text_input('Insert GameID',key ="input_gid" ,max_chars =8)
        Event = st.selectbox('Type of game', ['rapid', 'bullet', 'blitz', 'classical'], key=1)
        White_ID = st.text_input('Insert White player ID',key ="input_wid" ,max_chars=10 )
        Black_ID = st.text_input('Insert Black  player ID',key ="input_bid", max_chars=10 )
        Result = st.selectbox( '',['1-0', '0-1','1/2-1/2'], key=2)
        WhiteElo = st.slider('White ELO', 1500, 3000, 1678)
        BlackElo = st.slider('Black ELO', 1500, 3000, 1678)
        Date = st.date_input( "Date of the game", datetime.date(2023, 1, 1))

    submit_game_h = st.form_submit_button('Submit Game',disabled= st.session_state.disabled_add_game)

    if len('input_gid')>0 and len('input_wid') :
        st.session_state.disabled_add_game = False
    else:
        st.session_state.disabled_add_game = True

    if submit_game_h:
        test_func()            

st.button('Restart Database', on_click=sf_connection.restart_database)



