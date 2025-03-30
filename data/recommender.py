import csv
from typing import Any, Union, Optional, Dict, List

class _WeightedVertex:
    """A vertex in a weighted song similarity graph."""

    def __init__(self, item: Any, metadata: Optional[dict] = None) -> None:
        self.item = item
        self.metadata = metadata if metadata is not None else {}
        self.neighbours = {}

    def similarity_score(self, other: '_WeightedVertex') -> float:
        """Calculate similarity using only key audio features."""
        # Normalize tempo (0-250 → 0-1)
        self_tempo = self.metadata['tempo'] / 250
        other_tempo = other.metadata['tempo'] / 250

        # Calculate differences
        dance_diff = abs(self.metadata['danceability'] - other.metadata['danceability'])
        energy_diff = abs(self.metadata['energy'] - other.metadata['energy'])
        valence_diff = abs(self.metadata['valence'] - other.metadata['valence'])
        tempo_diff = abs(self_tempo - other_tempo)

        # Weighted similarity (1 - average difference)
        avg_diff = (dance_diff * 0.4 + energy_diff * 0.3 +
                    valence_diff * 0.2 + tempo_diff * 0.1)
        return 1 - avg_diff  # Convert to similarity (1 = identical)


class SongGraph:
    """A graph representing songs and their similarities."""

    def __init__(self):
        self._vertices = {}
        self._song_lookup = {}  # For case-insensitive song name lookup

    def add_vertex(self, item: Any, metadata: Optional[dict] = None) -> None:
        if item not in self._vertices:
            self._vertices[item] = _WeightedVertex(item, metadata)
            # Create lookup by name
            if metadata:
                song_key = metadata['track_name'].lower()
                self._song_lookup[song_key] = item

    def add_edge(self, item1: Any, item2: Any, weight: Optional[float] = None) -> None:
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            weight = weight if weight is not None else v1.similarity_score(v2)
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight

    def find_song_id(self, song_name: str) -> Optional[str]:
        """Find a song ID by name."""
        song_name = song_name.lower().strip()

        if song_name in self._song_lookup:
            return self._song_lookup[song_name]

        return None

    def recommend_songs(self, song_names: List[str], limit: int = 5) -> List[Dict]:
        # Convert song names to IDs
        song_ids = []
        for name in song_names:
            song_id = self.find_song_id(name)
            if song_id:
                song_ids.append(song_id)
            # Assume all songs are found in dataset
            # else:
            #     print(f"Song '{name}' not found in dataset")

        if not song_ids:
            return []

        # Calculate recommendations
        scores = {}
        for song_id in song_ids:
            seed_vertex = self._vertices[song_id]
            for neighbor, weight in seed_vertex.neighbours.items():
                if neighbor.item in song_ids:
                    continue
                if neighbor.item in scores:
                    scores[neighbor.item]['score'] += weight
                else:
                    scores[neighbor.item] = {'score': weight, 'metadata': neighbor.metadata}

        # Sort by score and popularity
        sorted_scores = sorted(
            scores.items(),
            key=lambda x: (-x[1]['score'], -x[1]['metadata'].get('popularity', 0))
        )

        # Prepare clean recommendations
        recommendations = []
        for track_id, data in sorted_scores[:limit]:
            rec = {
                'track': data['metadata']['track_name'],
                'artist': data['metadata']['artists'],
                'album': data['metadata']['album_name'],
                'score': data['score'] / len(song_ids)
            }
            recommendations.append(rec)

        return recommendations


def load_graph(songs_file: str) -> SongGraph:
    """Load song data using only essential features for similarity."""
    graph = SongGraph()

    with open(songs_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip header row

        for row in reader:
            # Only store features we'll use for similarity
            metadata = {
                'track_name': row[3],  # track_name
                'artists': row[1],  # artists
                'album_name': row[2],  # album name
                'danceability': float(row[7]),  # danceability
                'energy': float(row[8]),  # energy
                'valence': float(row[16]),  # valence
                'tempo': float(row[17])  # tempo
            }

            graph.add_vertex(metadata['track_name'], metadata)

    # Create similarity edges
    songs = list(graph._vertices.values())
    for i, song1 in enumerate(songs):
        similarities = []
        for j, song2 in enumerate(songs):
            if i == j:
                continue
            similarity = song1.similarity_score(song2)
            similarities.append((song2, similarity))

        # Sort by similarity and keep top 20
        similarities.sort(key=lambda x: -x[1])
        for song2, similarity in similarities[:20]:
            if similarity > 0.3:  # Minimum similarity threshold
                graph.add_edge(song1.item, song2.item, similarity)

    return graph

def get_recommendation_count() -> int:
    """Get number of recommendations with proper validation."""
    while True:
        try:
            print("How many recommendations would you like? (1-10)")
            limit = int(input("> ").strip())
            if 1 <= limit <= 10:
                return limit
            print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid number.")


def get_song_input() -> list[str]:
    """Get song names. Assume all song names are in dataset."""
    print("\nEnter song names (comma separated), or 'q' to quit:")
    user_input = input("> ").strip()
    return [] if user_input.lower() == 'q' else [name.strip() for name in user_input.split(',')]


def main():
    print("Spotify Song Recommender")
    graph = load_graph('spotify_songs_smaller.csv')

    while True:
        # Get song names (no validation)
        song_names = get_song_input()
        if not song_names:
            break

        # Get recommendation count
        limit = get_recommendation_count()

        # Get recommendations
        recommendations = graph.recommend_songs(
            [graph.find_song_id(name) for name in song_names],
            limit
        )

        # Display results
        print("\nRecommended Songs:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['track']} by {rec['artist']} ({rec['score']:.2f})")

        print("\nTry another search? (y/n)")
        if input("> ").lower() != 'y':
            break

if __name__ == "__main__":
    main()
