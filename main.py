"""CSC111 Winter 2025 Project: Spotify Song Recommendation System

This Python module is the main module where the program is run.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 Cindy Yang, Kate Shen, Kristen Wong, Sara Kopilovic.
"""
from __future__ import annotations
import csv
from typing import Any

columns_to_keep = [
    'track_id', 'artists', 'popularity', 'explicit', 'danceability', 'energy',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness',
    'valence', 'tempo', 'track_genre'
]

with open('data/spotify_songs.csv', 'r') as file:
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
