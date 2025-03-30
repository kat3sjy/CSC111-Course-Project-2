import csv
import math
from typing import Any, Dict, List, Optional, Tuple


class _WeightedVertex:
    """A vertex in a weighted song similarity graph."""

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
        self.item = item
        self.metadata = metadata if metadata is not None else {}
        self.neighbours = {}

    def similarity_score(self, other: '_WeightedVertex') -> float:
        """Calculate weighted similarity between songs."""
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
    """A graph representing songs and their similarities."""

    def __init__(self):
        self._vertices = {}
        self._song_lookup = {}

    def add_vertex(self, item: Any, metadata: Optional[dict] = None) -> None:
        """Add a song vertex to the graph."""
        if item not in self._vertices:
            self._vertices[item] = _WeightedVertex(item, metadata)
            if metadata:
                song_key = metadata['track_name'].lower()
                self._song_lookup[song_key] = item

    def add_edge(self, item1: Any, item2: Any, weight: Optional[float] = None) -> None:
        """Add a weighted edge between two songs."""
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            weight = weight if weight is not None else v1.similarity_score(v2)
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight

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
        """Find a song ID by name (case-insensitive)."""
        return self._song_lookup.get(song_name.lower().strip())

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
    """Load song data and build similarity graph."""
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

    # Build similarity edges more efficiently
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
            print("Please enter between 1-10")
        except ValueError:
            print("Please enter a valid number")


def get_song_input() -> list[str]:
    """Get song names. Assume all song names are in dataset."""
    print("\nEnter song names (comma separated), or 'q' to quit:")
    user_input = input("> ").strip()
    return [] if user_input.lower() == 'q' else [name.strip() for name in user_input.split(',')]


def main():
    print("Spotify Song Recommender")
    print("Loading song data...")
    graph = load_graph('spotify_songs_smaller.csv')

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
        'extra-imports': ['csv', 'math'],  # external modules used
        'allowed-io': ['main', 'load_graph', 'get_song_input', 'get_recommendation_count'],
        # functions using print/input
        'max-line-length': 120
    })
