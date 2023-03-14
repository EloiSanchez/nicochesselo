import streamlit as st

"""
# Here you can visualize data

Here you will be able to look at the data.

What should it do:
- General filter of the games that the user wants to use for the stats
- Improvise and see what happens
    - Predetermined set of charts that are always shown
    - some other plots with more thinguies and buttons that the user can touch
"""

variable = st.slider('This is a slider', 1500, 1700)

st.text(f'this is the slider value {variable}')