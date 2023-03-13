import lichess_api
import sf_connection

games = lichess_api.get_default_games(n_users = 2, n_games = 10)

sf_connection.add_games(games)