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
st.button('Restart Database', on_click=sf_connection.restart_database)
st.button('Populate Databse', on_click=sf_connection.populate_database)

# --- WITH SUMBIT BUTTON

col1, col2 = st.columns(2)

with col1:
    st.header("Search by UserId")

    with st.form('Form1'):
        name =  st.text_input('Insert UserID',key ="input_text_user_sub")
        num_games = st.slider(f'How many games by the user?', 1, 130, 10)
        submit_user = st.form_submit_button('Submit 1')

if submit_user:
    sf_connection.add_games(lichess_api.get_games(name ,num_games))

with col2:
    st.header("Search by GameID")
    with st.form('Form2'):
        Game = st.text_input('Insert GameID',key ="input_text" )
        submit_game = st.form_submit_button('Submit 1')

if submit_game:
     sf_connection.add_games(lichess_api.get_games_ID(st.session_state.input_text))


st.header("Insert a game by Hand")
    
with st.form('Form3'):
    Game_Id = st.text_input('Insert GameID',key ="input_gid" )
    Event = st.selectbox('Type of game', ['rapid', 'bullet', 'blitz', 'classical'], key=1)
    White_ID = st.text_input('Insert White player ID',key ="input_wid" )
    Black_ID = st.text_input('Insert Black  player ID',key ="input_bid" )
    Result = st.selectbox( '',['1-0', '0-1','1/2-1/2'], key=2)
    WhiteElo = st.slider('White ELO', 1500, 2000, 1666)
    BlackElo = st.slider('Black ELO', 1500, 2000, 1666)
    Date = st.date_input( "Date of the game", datetime.date(2023, 1, 1))
    Opening = st.selectbox('Opening', ['rapid', 'bullet', 'blitz', 'classical'], key=3);
    Moves = st.text_input('Insert Moves',key ="input_mvs" )
    submit_hand =  st.form_submit_button('Submit')

if submit_hand:
 pass   


       



# --- WITH CALLBACKS
# def proc():
#     sf_connection.add_games(lichess_api.get_games_ID(st.session_state.input_text))


# def proc2():
#     sf_connection.add_games(lichess_api.get_games(st.session_state.input_text_user ,10))

# Game = st.text_input('Insert GameID',key ="input_text", on_change = proc )
# User = st.text_input('Insert UserID',key ="input_text_user", on_change = proc2 )

# num_games = st.slider(f'How many games by the user{st.session_state.input_text_user}?', 0, 130, 10)
# #st.write("I'm ", age, 'years old')

# # st.write('The current game  is', Game)
# # User = st.text_input('Insert UserID')
# # def proc():
# # st.write(st.session_state.text_key)
# # st.text_area('enter text', on_change=proc, key='text_key')
# # st.text_input(label, value="Insert GameID", label_visibility="visible")