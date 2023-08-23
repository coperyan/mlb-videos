import os


from filmroom import Video
from statcast import Statcast
from statsapi import Game, Player


statcast_data = Statcast(
    start_date="2023-07-21",
    end_date="2023-07-28",
    transform=["umpire_calls"],
)
statcast_df = statcast_data.df
players = Player(
    list(
        set(
            statcast_df["batter"].values.tolist()
            + statcast_df["pitcher"].values.tolist()
        )
    )
)
players_df = players.df
games = Game(list(set(statcast_df["game_pk"].values.tolist())))
games_df = games.df

master_df = statcast_df.copy()
master_df = master_df.merge(
    players_df.rename(
        columns={
            c: "batter" if c == "id" else f"batter_{c}"
            for c in players_df.columns.values
        }
    ),
    how="left",
    on="batter",
)
master_df = master_df.merge(
    players_df.rename(
        columns={
            c: "pitcher" if c == "id" else f"pitcher_{c}"
            for c in players_df.columns.values
        }
    ),
    how="left",
    on="pitcher",
)
master_df = master_df.merge(
    games_df.rename(
        columns={c: f"game_{c}" for c in games_df.columns.values if c != "game_pk"}
    ),
    how="left",
    on="game_pk",
)
