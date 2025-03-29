from __future__ import annotations
from typing import Optional, Union, List, Dict
import pandas as pd  # Reads, processes CSV file
import numpy as np  # Efficient mathematical computations
from sklearn.neighbors import NearestNeighbors  # Efficient similarity search
from tqdm import tqdm  # Progress visualization (don't need in final version)


class _SongVertex:
    """A vertex in a song similarity graph."""
    item: str
    features: Dict[str, float]
    neighbours: Dict[_SongVertex, float]

    def __init__(self, item: str, features: Dict[str, float]) -> None:
        self.item = item
        self.features = features
        self.neighbours = {}


class SongGraph:
    """Optimized song similarity graph using ANN."""
    _vertices: Dict[str, _SongVertex]
    _metadata: Dict[str, Dict]

    def __init__(self):
        self._vertices = {}
        self._metadata = {}

    def add_song(self, track_id: str, features: Dict[str, float], metadata: Dict[str, Union[str, int]]) -> None:
        """
        Adds a song to the graph with its audio features and metadata. Creates a new vertex in the graph if the track_id doesn't already exist.
        """
        if track_id not in self._vertices:
            self._vertices[track_id] = _SongVertex(track_id, features)
            self._metadata[track_id] = metadata

    def build_similarity_edges(self, threshold: float = 0.7, n_neighbors: int = 100) -> None:
        """
        Constructs similarity edges between songs using approximate nearest neighbors.

        For each song in the graph, finds its most similar neighbors based on audio features and creates weighted edges between them. Uses cosine similarity over normalized audio features.
        """
        track_ids = list(self._vertices.keys())
        if not track_ids:
            return

        feature_names = [
            'danceability', 'energy', 'loudness',
            'speechiness', 'acousticness', 'instrumentalness',
            'liveness', 'valence', 'tempo'
        ]
        X = np.array([list(self._vertices[track_id].features.values()) for track_id in track_ids])

        # Add small noise to prevent exact duplicates
        X += np.random.normal(0, 0.0001, X.shape)

        nbrs = NearestNeighbors(
            n_neighbors=min(n_neighbors, len(track_ids) - 1),
            metric='cosine',
            algorithm='auto'
        ).fit(X)

        distances, indices = nbrs.kneighbors(X)
        similarities = 1 - distances

        for i in tqdm(range(len(track_ids)), desc="Building edges"):
            for j, sim in zip(indices[i], similarities[i]):
                if i != j and sim > threshold:
                    # if sim > 0.99:  # Cap near-perfect similarities
                    #     sim = 0.99
                    v1 = self._vertices[track_ids[i]]
                    v2 = self._vertices[track_ids[j]]
                    v1.neighbours[v2] = sim
                    v2.neighbours[v1] = sim

    def get_similar_songs(self, track_ids: List[str], limit: int = 10) -> List[Dict]:
        """
        Retrieves recommended songs based on similarity to input track(s).

        For each input track, aggregates similarities from its neighbors in the graph, then returns the top most similar songs not in the original input list. When multiple input tracks are provided, similarities are averaged across all tracks that reference a particular song.
        """
        if not track_ids:
            return []

        similarity_sums = {}
        for track_id in track_ids:
            if track_id in self._vertices:
                for neighbor, weight in self._vertices[track_id].neighbours.items():
                    similarity_sums[neighbor.item] = similarity_sums.get(neighbor.item, 0.0) + weight

        similar_songs = []
        for song_id, total_sim in similarity_sums.items():
            if song_id not in track_ids:
                avg_sim = total_sim / len(track_ids)
                similar_songs.append({
                    'track_id': song_id,
                    'track_name': self._metadata[song_id]['track_name'],
                    'artists': self._metadata[song_id]['artists'],
                    'album': self._metadata[song_id]['album_name'],
                    'similarity': min(0.99, avg_sim)  # Cap displayed similarity
                })

        similar_songs.sort(key=lambda x: (-x['similarity'], x['track_name']))
        return similar_songs[:limit]

    def find_song_by_name(self, track_name: str) -> Optional[str]:
        """
        Searches for a track by name and returns its track_id.
        """
        lower_name = track_name.lower()
        for track_id, meta in self._metadata.items():
            if meta['track_name'].lower() == lower_name:
                return track_id
        return None


class SpotifyGraphRecommender:
    """
    A song recommendation system using graph-based similarity.
    """
    def __init__(self, data_path: str):
        self.graph = SongGraph()
        self._load_data(data_path)
        self.graph.build_similarity_edges()

    def _load_data(self, filepath: str) -> None:
        df = pd.read_csv(filepath)

        features = [
            'danceability', 'energy', 'loudness',
            'speechiness', 'acousticness', 'instrumentalness',
            'liveness', 'valence', 'tempo'
        ]

        for feature in features:
            if feature != 'loudness':
                q1 = df[feature].quantile(0.25)
                q3 = df[feature].quantile(0.75)
                iqr = q3 - q1
                df[feature] = (df[feature] - q1) / iqr
            else:
                df['loudness'] = (df['loudness'] - (-60)) / 60

        for _, row in tqdm(df.iterrows(), total=len(df), desc="Loading songs"):
            features_dict = {f: row[f] for f in features}
            metadata = {
                'track_name': row['track_name'],
                'artists': row['artists'],
                'album_name': row['album_name'],
                'popularity': row['popularity']
            }
            self.graph.add_song(row['track_id'], features_dict, metadata)

    def recommend(self, track_names: List[str], limit: int = 10) -> List[Dict]:
        """
        Generates *limit* song recommendations based on input track names.
        """
        track_ids = []
        for name in track_names:
            track_id = self.graph.find_song_by_name(name)
            if track_id:
                track_ids.append(track_id)

        return self.graph.get_similar_songs(track_ids, limit)


def main():
    """
    Main loop.
    """
    print("Spotify Song Recommender")
    print("Loading data...")
    try:
        recommender = SpotifyGraphRecommender('spotify_songs_small.csv')
    except FileNotFoundError:
        print("Error: Could not find file.")
        return

    print("\nEnter song names separated by commas.")
    print("Type 'quit' to exit\n")

    while True:
        print("\nEnter song names:")
        user_input = input("> ").strip()

        if user_input.lower() == 'quit':
            break

        song_names = [name.strip() for name in user_input.split(",")]

        print("\nHow many recommendations? (1-20)")
        try:
            limit = min(max(int(input("> ")), 1), 20)
        except ValueError:
            limit = 10

        recs = recommender.recommend(song_names, limit)

        if not recs:
            print("No recommendations found. Check your song names.")
            continue

        print(f"\nTop {limit} recommendations:")
        for i, rec in enumerate(recs, 1):
            print(f"{i}. {rec['track_name']} by {rec['artists']} "
                  f"(Similarity: {rec['similarity']:.2f})")


if __name__ == "__main__":
    main()
