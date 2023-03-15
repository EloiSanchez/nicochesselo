import streamlit as st
import sf_connection
from sf_connection import con

"""
# Here you can visualize data

Here you will be able to look at the data.

What should it do:
- General filter of the games that the user wants to use for the stats
- Improvise and see what happens
    - Predetermined set of charts that are always shown
    - some other plots with more thinguies and buttons that the user can touch
"""
range_values = sf_connection.get_game_ranges()

with st.form('Query form'):
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row2_col1, row2_col2, row2_col3 = st.columns(3)

    with row1_col1:
        username_value = st.text_input(label='Username',
                                       key='username_field')

    with row1_col2:
        color_value = st.selectbox(label='Playing as',
                                   options=['Any', 'White', 'Black'],
                                   key='color_field')

    with row1_col3:
        result_values = st.multiselect(label='Result',
                                       options=["'1-0'", "'1/2-1/2'", "'0-1'"],
                                       format_func=lambda x: x.strip("'"),
                                       key='result_field')

    with row2_col1:
        gamemode_values = st.multiselect(label='Game mode',
                                         options=["'classical'", "'rapid'", "'blitz'", "'bullet'"],
                                         format_func=lambda x: x.strip("'"),
                                         key='gamemode_field')

    with row2_col2:
        date_values = st.slider(label='Date Range',
                    min_value=range_values['min_date'],
                    max_value=range_values['max_date'],
                    value=(range_values['min_date'], range_values['max_date']))

    with row2_col3:
        elo_values = st.slider(label='Elo Range',
                    min_value=round(range_values['min_elo']-5, -1),
                    max_value=round(range_values['max_elo']+5, -1),
                    value=(range_values['min_elo'], range_values['max_elo']),
                    step=50)


    find_games = st.form_submit_button()


if find_games:
    statement, df = sf_connection.find_games(username_value, color_value,
                                             result_values, gamemode_values,
                                             date_values, elo_values)

    st.text(statement)

    df