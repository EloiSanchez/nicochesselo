# NicoChessElo

**Note:** This application cannot be run anymore. To have a feel of what it looked like initially, check the [screenshots page](https://github.com/EloiSanchez/nicochesselo/tree/main/screenshots) or see below.

This application is a 4-days learning project created to understand the usage of APIs and the Python-Snowflake connection.

## How does it work

The data is retreived either from a PGN file (obtained from the [Lichess Database](https://database.lichess.org/)). It can also retrieve specific games or a set of games from a user using the [Lichess API](https://lichess.org/api) in the Get Data page and visualize statistics of the stored games in the Visualize Data page.

The data is then stored in [Snowflake](https://www.snowflake.com/en/). The architecture (ERDs) of the database can be seen in the `figures` directory.

## Usage

Go to the directory of your preference and execute clone the repository.

```bash
git clone https://github.com/EloiSanchez/nicochesselo
```

Go into the recently cloned directory

```bash
cd nicochesselo
```

Create a new conda's environment with Python 3.11

```bash
conda create --name nicochesselo python=3.11
```

and activate it.

```bash
conda activate nicochesselo
```

Once the environment is active, execute the following commands

```bash
pip install "snowflake-connector-python[pandas]"
```

```bash
pip install -r requirements.txt
```

Launch with

```bash
streamlit run .\nicochesselo\NicoChessElo.py  # Windows
streamlit run nicochesselo/NicoChessElo.py    # Linux
```

### Optional

If the database is empty and must be populated, use [PeaZip](https://peazip.github.io/) (or something with similar functionalities) to extract the compressed PGN file stored in the `data` direcory. Do not change the name of the file.

## Screenshots

![Vizualization 1](https://github.com/EloiSanchez/nicochesselo/blob/main/screenshots/Visualize_data_page_1.png)

![Visualization 2](https://github.com/EloiSanchez/nicochesselo/blob/main/screenshots/Visualize_data_page_2.png)

![Vizualization 3](https://github.com/EloiSanchez/nicochesselo/blob/main/screenshots/Visualize_data_page_3.png)

![Vizualization 4](https://github.com/EloiSanchez/nicochesselo/blob/main/screenshots/Visualize_data_page_4png)

## About us

We are [Eloi Sanchez](https://github.com/EloiSanchez) and [Niccolò Racioppi](https://github.com/LoSputnik) and, at the time of making this project, we are part of the [Nimbus Intelligence Academy](https://nimbusintelligence.com/).
