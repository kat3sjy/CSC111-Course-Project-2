
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

#    def similarity_score(self, other: _Vertex) -> float:
#        """Return the similarity score between this song vertex and another, based on audio features."""
#        if not self.features or not other.features:
#            return 0.0

#        total = 0
#        for feature in self.features:
#            v1 = self.features[feature]
#            v2 = other.features[feature]
#            total += (v1 - v2) ** 2

#        euclidean_distance = (total) ** 0.5
#        return 1 / (1 + euclidean_distance)


if __name__ == '__main__':
    import doctest

    doctest.testmod()

    import python_ta

    python_ta.check_all(config={
        'extra-imports': [],  # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })
