"""CSC111 Winter 2025 Project: Spotify Song Recommendation System

This Python module contains the classes used to represent our domain and
functions for the computation of our data.

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
import math
from typing import Any, Dict, List, Optional, Tuple


class _WeightedVertex:
    """A vertex in a weighted song similarity graph, used to represent a song.

    Each vertex item is a song name, represented as a string.

    Instance Attributes:
        - item: The data stored in this vertex, representing a song.
        - neighbours: The vertices that are adjacent to this vertex.
        - feature_configuration: A tuple that defines the audio features that are considered
                                 for every song and their respectives weights. It uses the format:
                                 (feature_name, weight, min_value. max_value)

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    item: str
    neighbours: dict[_WeightedVertex, float]
    feature_configuration = [
        # (field_name, weight, min_value, max_value)
        ('danceability', 0.25, 0.0, 1.0),
        ('energy', 0.25, 0.0, 1.0),
        ('valence', 0.15, 0.0, 1.0),
        ('tempo', 0.1, 50, 200),
        ('loudness', 0.1, -30, 0),
        ('acousticness', 0.1, 0.0, 1.0),
        ('instrumentalness', 0.05, 0.0, 1.0)
    ]

    def __init__(self, item: Any, metadata: Optional[dict] = None) -> None:
        """Initialize a new vertex with the given.

        This vertex is initialized with no neighbours.
        """
        self.item = item
        self.metadata = metadata if metadata is not None else {}
        self.neighbours = {}

    def similarity_score(self, other: '_WeightedVertex') -> float:
        """Calculate weighted similarity between this vertex and other."""
        dot_product = 0.0
        mag1 = 0.0
        mag2 = 0.0

        for feature, weight, min_val, max_val in self.feature_configuration:
            # Clip values to expected ranges
            val1 = max(min(self.metadata[feature], max_val), min_val)
            val2 = max(min(other.metadata[feature], max_val), min_val)

            # Min-max normalization with weighting
            norm1 = ((val1 - min_val) / (max_val - min_val)) * weight
            norm2 = ((val2 - min_val) / (max_val - min_val)) * weight

            dot_product += norm1 * norm2
            mag1 += norm1 ** 2
            mag2 += norm2 ** 2

        if mag1 == 0 or mag2 == 0:
            return 0.0

        raw_score = dot_product / (math.sqrt(mag1) * math.sqrt(mag2))

        # Apply non-linear scaling to better distribute scores
        return raw_score ** 2


class WeightedGraph:
    """A weighted graph used to represent songs and their similarities."""
    # Private Instance Attributes:
    #     -_vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _WeightedVertex]

    def __init__(self):
        self._vertices = {}
        self._song_lookup = {}

    def add_vertex(self, item: Any, metadata: Optional[dict] = None) -> None:
        """Add a song vertex to the graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _WeightedVertex(item, metadata)

    def add_edge(self, item1: Any, item2: Any, weight: Optional[float] = None) -> None:
        """Add a weighted edge between two songs, item1 and item2, and the given weight.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            weight = weight if weight is not None else v1.similarity_score(v2)
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight
        else:
            raise ValueError

    def get_all_vertices(self) -> set:
        """Return a set of all vertex items in this weighted graph."""
        return set(self._vertices.keys())

    def get_similarity_score(self, item1, item2):
        """Return the similarity score between two vertices."""
        v1 = self._vertices.get(item1)
        v2 = self._vertices.get(item2)
        if v1 is None or v2 is None:
            raise ValueError()
        return v1.similarity_score(v2)

    def find_song_id(self, song_name: str) -> Optional[str]:
        """Find a song's vertex key (track name) by its name (case-insensitive)."""
        target_name = song_name.lower().strip()
        for vertex_key, vertex in self._vertices.items():
            if vertex.metadata.get('track_name', '').lower() == target_name:
                return vertex_key  # Return the vertex's key (track name)
        return None  # Song not found

    def recommend_songs(self, song_names: List[str], limit: int = 5) -> List[Dict]:
        """Generate recommendations based on multiple seed songs."""
        if not song_names:
            return []

        # Initialize recommendation scores
        recommendations = {}

        for name in song_names:
            song_id = self.find_song_id(name)
            if not song_id:
                continue

            vertex = self._vertices[song_id]

            for neighbor, weight in vertex.neighbours.items():
                if neighbor.item in song_names:  # Skip seed songs
                    continue

                if neighbor.item in recommendations:
                    # If we've seen this recommendation before, add to its score
                    recommendations[neighbor.item]['total_score'] += weight
                    recommendations[neighbor.item]['count'] += 1
                else:
                    # New recommendation
                    recommendations[neighbor.item] = {
                        'total_score': weight,
                        'count': 1,
                        'metadata': neighbor.metadata
                    }

        # Calculate average scores and prepare results
        results = []
        for song_id, data in recommendations.items():
            avg_score = data['total_score'] / data['count']
            results.append({
                'track': data['metadata']['track_name'],
                'artist': data['metadata']['artists'],
                'album': data['metadata']['album_name'],
                'score': avg_score,
                'popularity': data['metadata'].get('popularity', 0)
            })

        # Sort by average score (descending) then popularity (descending)
        results.sort(key=lambda x: (-x['score'], -x['popularity']))

        return results[:limit]


def load_graph(songs_file: str) -> WeightedGraph:
    """Load song data and build similarity graph.

    Preconditions:
        - songs_file is the path to a CSV file corresponding to the song data format described
          in the written report
    """
    graph = WeightedGraph()
    songs = []

    with open(songs_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            try:
                metadata = {
                    'track_name': row[3],
                    'artists': row[1],
                    'album_name': row[2],
                    'popularity': float(row[4]),
                    'danceability': float(row[7]),
                    'energy': float(row[8]),
                    'valence': float(row[16]),
                    'tempo': float(row[17]),
                    'loudness': float(row[9]),
                    'acousticness': float(row[11]),
                    'instrumentalness': float(row[12])
                }
                track_name = metadata['track_name']
                graph.add_vertex(track_name, metadata)
                songs.append(track_name)
            except (IndexError, ValueError):
                continue

    for i in range(len(songs)):
        song1 = songs[i]
        if song1 not in graph.get_all_vertices():
            continue

        similarities = []
        for j in range(i + 1, len(songs)):
            song2 = songs[j]
            if song2 not in graph.get_all_vertices():
                continue

            similarity = graph.get_similarity_score(song1, song2)
            if similarity > 0.3:  # Threshold
                similarities.append((song2, similarity))

        # Keep top 20 most similar songs
        similarities.sort(key=lambda x: -x[1])
        for song2, similarity in similarities[:20]:
            graph.add_edge(song1, song2, similarity)

    return graph


def get_recommendation_count() -> int:
    """Get validated number of recommendations."""
    while True:
        try:
            count = int(input("How many recommendations? (1-10)\n> ").strip())
            if 1 <= count <= 10:
                return count
            print("Please enter a number between 1-10.")
        except ValueError:
            print("Please enter a valid number.")


def get_song_input() -> list[str]:
    """Get song names. Assume all song names are in dataset."""
    print("\nEnter song names (comma separated), or 'q' to quit:")
    user_input = input("> ").strip()
    return [] if user_input.lower() == 'q' else [name.strip() for name in user_input.split(',')]


def main():
    print("Spotify Song Recommender")
    print("Loading song data...")
    graph = load_graph('data/spotify_songs_smaller.csv')

    while True:
        song_ids = get_song_input()
        if not song_ids:
            break

        limit = get_recommendation_count()
        recommendations = graph.recommend_songs(song_ids, limit)

        print("\nRecommended Songs:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['track']} by {rec['artist']} (score: {rec['score']:.3f})")

        print("\nTry another search? (y/n)")
        if input("> ").lower() != 'y':
            break


if __name__ == '__main__':
    main()

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['pygame', 'csv', 'recommender'],
        'allowed-io': [],
        'max-line-length': 120
    })
