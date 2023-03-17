import streamlit as st

if 'but_a' not in st.session_state:
    st.session_state.disabled = True

Game_Id = st.text_input('Insert GameID',key ="input_gid" ,max_chars =8)

button_a = st.button('a', key='but_a')

button_b = st.button('b', key='but_b')

button_c = st.button('c', key='but_c', disabled=st.session_state.disabled)

st.write(button_a, button_b, button_c)


if len('input_gid')>0:
    st.write("clicked A")
    st.session_state.disabled = False
else:
    st.session_state.disabled = True

# if button_b:
#     st.write('clicked B')
