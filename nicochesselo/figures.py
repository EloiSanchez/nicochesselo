import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st

COLORS = {
    'w': 'rgb(255,255,255)',
    'b': 'rgb(64,71,73)',
    'd': 'rgb(179,179,179)',
}

RSLTS = {
    '1-0': 'White',
    '1/2-1/2': 'Draw',
    '0-1': 'Black'
}

OPACITY = 0.7

def frmt_label(label):
    return label.replace('_', ' ').lower().replace('elo', 'ELO').strip("'")


@st.cache_data
def _get_elo(df, round_to = None):
    elo_df = df.copy()
    elo_df['ELO'] = (df['WHITE_ELO'] + df['BLACK_ELO']) / 2

    if type(round_to) == int:
        elo_df['ELO'] = elo_df['ELO'].round(round_to)

    return elo_df

@st.cache_data
def _get_grouped_df(df, x_label, round_to=-2):
    group_df = df.copy()

    if x_label == 'ELO':
        group_df = _get_elo(df, round_to)

    return group_df[['GAME_ID', 'RESULT', x_label]]\
        .groupby(by=['RESULT', x_label]).count().reset_index()


@st.cache_data
def perc_results_by(df, x_label):
    result_count_df = _get_grouped_df(df, x_label, -2)

    if x_label == 'ELO':
        result_count_df = result_count_df[(1000 <= result_count_df['ELO']) & (result_count_df['ELO'] <= 2100)]

    fig = go.Figure()
    x = result_count_df[x_label]

    fig.add_trace(go.Scatter(
        x=x, y=result_count_df[result_count_df['RESULT'] == '1-0']['GAME_ID'],
        mode='lines',
        line=dict(width=0.5, color=COLORS['w']),
        name='White',
        stackgroup='one',
        groupnorm='percent' # sets the normalization for the sum of the stackgroup
    ))

    fig.add_trace(go.Scatter(
        x=x, y=result_count_df[result_count_df['RESULT'] == '1/2-1/2']['GAME_ID'],
        mode='lines',
        line=dict(width=0.5, color=COLORS['d']),
        name='Draw',
        stackgroup='one',
    ))

    fig.add_trace(go.Scatter(
        x=x, y=result_count_df[result_count_df['RESULT'] == '0-1']['GAME_ID'],
        mode='lines',
        line=dict(width=0.5, color=COLORS['b']),
        name='Black',
        stackgroup='one',
    ))

    fig.update_layout(
        title = f"End result by {frmt_label(x_label)}",
        yaxis=dict(ticksuffix='%')
            )

    return fig, result_count_df

@st.cache_data
def game_count(df, x_label):
    # Get right data
    game_count_df = _get_grouped_df(df, x_label)

    # Create figure and plot
    fig = go.Figure()
    x = game_count_df[x_label]

    fig.add_trace(go.Scatter(
        x=x, y=game_count_df[game_count_df['RESULT'] == '1-0']['GAME_ID'],
        mode='lines',
        line=dict(width=0.5, color=COLORS['w']),
        name='White',
        stackgroup='one',
        groupnorm='' # sets the normalization for the sum of the stackgroup

    ))

    fig.add_trace(go.Scatter(
        x=x, y=game_count_df[game_count_df['RESULT'] == '1/2-1/2']['GAME_ID'],
        mode='lines',
        line=dict(width=0.5, color=COLORS['d']),
        name='Draw',
        stackgroup='one',
    ))

    fig.add_trace(go.Scatter(
        x=x, y=game_count_df[game_count_df['RESULT'] == '0-1']['GAME_ID'],
        mode='lines',
        line=dict(width=0.5, color=COLORS['b']),
        name='Black',
        stackgroup='one',
    ))

    fig.update_layout(
        title = f"Game count by {frmt_label(x_label)}"
            )

    return fig, game_count_df


@st.cache_data
def _get_played_openings(df):
    return df[['OPENING_ID', 'GAME_ID']]\
        .groupby(by=['OPENING_ID']).count()\
            .reset_index().sort_values(by='GAME_ID', ascending=False)


@st.cache_data
def top_openings(df: pd.DataFrame, n=8, elos=None):
    op_df = _get_elo(df)
    op_df = op_df[(elos[0] <= op_df['ELO']) & (op_df['ELO'] <= elos[1])]

    # Get mainline
    op_df['OPENING_ID'] = op_df['OPENING_ID'].str.split(':').str[0]

    # Get
    top_op = _get_played_openings(op_df).head(n)['OPENING_ID'].to_list()

    top_op_df = op_df[['OPENING_ID', 'GAME_ID', 'RESULT']]
    top_op_df['is_top'] = top_op_df.apply(lambda x: x.iloc[0] in top_op,
                                                axis=1)
    top_op_df = top_op_df[top_op_df['is_top']]

    top_op_df = top_op_df.groupby(by=['OPENING_ID', 'RESULT']).count()\
        .reset_index()

    fig = px.histogram(
        top_op_df,
        x='OPENING_ID',
        y='GAME_ID',
        color='RESULT',
        color_discrete_sequence=(COLORS['b'], COLORS['w'], COLORS['d']),
        labels={'GAME_ID':'Games played', 'OPENING_ID': 'Opening'},
        barmode='stack',
        opacity=OPACITY
    ).update_xaxes(categoryorder='total descending',)

    # Change legend names
    fig.for_each_trace(lambda t: t.update(
        name = RSLTS[t.name],
        legendgroup = RSLTS[t.name],
        hovertemplate = t.hovertemplate.replace(t.name, RSLTS[t.name])
    )
                  )

    # Change title
    fig.update_layout(
        title=f'Top {n} most played openings'
    )

    return fig, top_op_df


@st.cache_data
def elo_dist(df):
    elo_dist_df = _get_elo(df)
    fig = px.histogram(elo_dist_df,
                       x='ELO',
                       color_discrete_sequence=(COLORS['w'],),
                       opacity=OPACITY)

    return fig, elo_dist_df