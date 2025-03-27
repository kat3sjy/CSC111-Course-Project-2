
from __future__ import annotations
import csv
from typing import Any

columns_to_keep = [
    'track_id', 'artists', 'popularity', 'explicit', 'danceability', 'energy',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness',
    'valence', 'tempo', 'track_genre'
]

with open('spotify_songs.csv', 'r') as file:
    reader = csv.reader(file)
    filtered_rows = []
    for row in reader:
        filter_row = {song: row[song] for song in columns_to_keep}
        filtered_rows.append(filter_row)


