import streamlit as st
import numpy as np
import os
from PIL import Image

file_dir =  os.path.dirname(os.path.realpath(__file__))

"""
# Welcome to NicoChessElo

This application is a learning project created to unerstand the usage of APIs
and the Python-Snowflake connection.

## How does it work

The data is retreived either from a PGN file (obtained from the
[Lichess Database](https://database.lichess.org/)). It can also retrieve
specific games from a user in the Get Data page and visualize statistics of the
stored games in the Visualize Data page.

The data is stored in a [Snowflake](https://www.snowflake.com/en/) account
that can be accessed by the code. The
structre of the database is pretty simple and can be seen next.
"""

figs_dir = os.path.join(file_dir, r"..\figures")
erd_img = np.asarray(Image.open(os.path.join(figs_dir, 'Chess_ERD.png')))
st.image(erd_img, caption='Physical ERD of the database in Snowflake')

"""
## About us

We are [Eloi Sanchez](https://github.com/EloiSanchez) and
[Niccolò Racioppi](https://github.com/LoSputnik) and we are part of the
[Nimbus Intelligence Academy](https://nimbusintelligence.com/).
"""