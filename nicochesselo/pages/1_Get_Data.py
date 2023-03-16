import streamlit as st
import sf_connection
import lichess_api
import datetime

"""
# Get Data from Lichess

Here you will be able to look for specific games, whether by ID or by user.

What should it do:
- Get a game and add it to the database
- Get all or some games of a specific user
- Introduce a game by hand introducing the game information and the list of moves
"""
#st.button('Restart Database', on_click=sf_connection.restart_database)
#st.button('Populate Databse', on_click=sf_connection.populate_database)


def opening_func():
    eco,name = lichess_api.get_opening_by_moves(Moves) 
    st.session_state.op_name = name; 
    st.session_state.op_eco = eco; 

def test_func(name, eco):

    # if White_ID == Black_ID:
    #     print ("Players ID must be different") #Do in streamlit 
    # else:    
        game_param = {'GAME_ID' : Game_Id, 'EVENT': Event,'WHITE_PLAYER_ID': White_ID, 'BLACK_PLAYER_ID':Black_ID,'OPENING_ID':Opening,
                    'RESULT':Result, 'WHITE_ELO' :WhiteElo,'BLACK_ELO': BlackElo,'GAME_DATE': Date}
        sf_connection.add_games_by_hand(game_param)

        opening_param = {'OPENING_ID' : name, 'ECO' : eco}
        sf_connection.add_openings_hand(opening_param)


# --- WITH SUMBIT BUTTON
col1, col2 = st.columns(2)

with col1:
    st.header("Search by UserId")
    with st.form('Form1'):
        name =  st.text_input('Insert UserID',key ="input_text_user_sub")
        num_games = st.slider(f'How many games by the user?', 1, 130, 10)
        submit_user = st.form_submit_button('Submit 1')

if submit_user:
    get_game_ = lichess_api.get_games(name ,num_games)
    if get_game_ == 0:
         st.error("THIS USER DOESN'T EXISTS")
    else:
        sf_connection.add_games(get_game_)
        #sf_connection.add_games(lichess_api.get_games(name ,num_games))

with col2:
    st.header("Search by GameID")
    with st.form('Form2'):
        game = st.text_input('Insert GameID',key ="input_game" )
        submit_game = st.form_submit_button('Submit 1')

if submit_game:
    get_game_ = lichess_api.get_games_ID(st.session_state.input_game)

    if get_game_ == 0:
         st.error("THIS GAME DOESN'T EXISTS")
    else:
     sf_connection.add_games(get_game_)

st.header("Insert a game by Hand")
    
Game_Id = st.text_input('Insert GameID',key ="input_gid" ,max_chars =8)
Event = st.selectbox('Type of game', ['rapid', 'bullet', 'blitz', 'classical'], key=1)
White_ID = st.text_input('Insert White player ID',key ="input_wid" ,max_chars=10 )
Black_ID = st.text_input('Insert Black  player ID',key ="input_bid", max_chars=10 )
Result = st.selectbox( '',['1-0', '0-1','1/2-1/2'], key=2)
WhiteElo = st.slider('White ELO', 1500, 2000, 1666)
BlackElo = st.slider('Black ELO', 1500, 2000, 1666)
Date = st.date_input( "Date of the game", datetime.date(2023, 1, 1))

st.header("Insert Moves and Discover the opening")

if "op_name" not in st.session_state:
    Opening = st.session_state.op_name = 'Wait for moves'
        
if "op_eco" not in st.session_state:
    ECO =st.session_state.op_eco = '...'

Moves = st.text_input('Insert Moves',key ="input_mvs" )
Opening = st.write("Opening name:", st.session_state.op_name)
ECO  = st.write("Opening ECO: ", st.session_state.op_eco)

opg_button = st.button("Find Opening", on_click=opening_func)

submit_hand  = st.button("INSERT GAME", on_click= test_func)
