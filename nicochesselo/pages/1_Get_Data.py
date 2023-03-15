import streamlit as st
import sf_connection

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