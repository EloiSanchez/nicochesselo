import streamlit as st
import sf_connection
import figures as figs
from figures import frmt_label

"""
# Data Visualization
"""

# Get general data
range_values = sf_connection.get_game_ranges()
if 'df' not in st.session_state:
    df = None
else:
    df = st.session_state['df']

# Form in for getting games from SF
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
                                       format_func=frmt_label,
                                       key='result_field')

    with row2_col1:
        gamemode_values = st.multiselect(label='Game mode',
                                         options=["'classical'", "'rapid'", "'blitz'", "'bullet'"],
                                         format_func=frmt_label,
                                         key='gamemode_field')

    with row2_col2:
        date_values = st.slider(label='Date Range',
                    min_value=range_values['min_date'],
                    max_value=range_values['max_date'],
                    value=(range_values['min_date'], range_values['max_date']))

    with row2_col3:
        elo_values = st.slider(label='ELO Range',
                    min_value=round(range_values['min_elo']-5, -1),
                    max_value=round(range_values['max_elo']+5, -1),
                    value=(range_values['min_elo'], range_values['max_elo']),
                    step=50)


    find_games = st.form_submit_button('Look for games')

# When form is completed, execute query and get data from snowflake
if find_games:
    statement, df = sf_connection.find_games(username_value, color_value,
                                             result_values, gamemode_values,
                                             date_values, elo_values)
    st.session_state['df'] = df

# If data has been retrieved, make plots
if df is not None:

    # Aggregated plots selected by user
    agg_col1, agg_col2 = st.columns(2)

    with agg_col1:
        x_label1 = st.selectbox(label='x axis',
                                options=("GAME_DATE", "ELO", "EVENT"),
                                format_func=frmt_label,
                                key='x_label1')

        fig1, df1 = figs.perc_results_by(df, x_label1)
        st.plotly_chart(fig1, use_container_width=True)

    with agg_col2:
        x_label2 = st.selectbox(label='x axis',
                                options=("GAME_DATE", "ELO", "EVENT"),
                                format_func=frmt_label,
                                key='x_label2')
        fig2, df2 = figs.game_count(df, x_label2)
        st.plotly_chart(fig2, use_container_width=True)

    # Elo distribution plot
    fig3, df3 = figs.elo_dist(df)
    st.plotly_chart(fig3, use_container_width=True)

    # Top openings plot
    opening_col1, opening_col2 = st.columns(2)
    with opening_col1:
        elos = st.slider(label='ELO Range',
                        min_value=round(range_values['min_elo']-5, -1),
                        max_value=round(range_values['max_elo']+5, -1),
                        value=(range_values['min_elo'], range_values['max_elo']),
                        step=50)

    with opening_col2:
        n_openings = st.slider(label='Number of openings',
                            min_value=3,
                            max_value=10,
                            step=1,
                            value=8)

    fig4, df4 = figs.top_openings(df, n=n_openings, elos=elos)
    st.plotly_chart(fig4, use_container_width=True)
