import pandas as pd
import math


class SpotifyRecommender:
    """
    Recommends a list of similar songs based on user input.
    """
    def __init__(self, csv_file='spotify_songs.csv'):
        """Initialize with CSV file path"""
        try:
            self.songs = pd.read_csv(csv_file).to_dict('records')
            print(f"loaded {len(self.songs)} songs")
        except FileNotFoundError:
            self.songs = []

        self.graph = {}

        if self.songs:
            self._build_graph()

    def _calculate_similarity(self, song1, song2):
        """Calculate similarity between two songs (0-1 scale)"""
        features = ['danceability', 'energy', 'valence', 'acousticness']
        total_diff = sum((song1[f] - song2[f]) ** 2 for f in features)
        return 1 / (1 + math.sqrt(total_diff))

    def _build_graph(self, threshold=0.7):
        """Build connections between similar songs"""
        for i, song1 in enumerate(self.songs):
            for j in range(i + 1, len(self.songs)):
                song2 = self.songs[j]
                sim = self._calculate_similarity(song1, song2)
                if sim > threshold:
                    self.graph.setdefault(song1['track_id'], {})[song2['track_id']] = sim
                    self.graph.setdefault(song2['track_id'], {})[song1['track_id']] = sim
        print(f"{len(self.graph)} songs.")

    def recommend(self, input_songs, num_recs=5):
        """Get recommendations based on input songs"""
        if not self.songs:
            print("\nNo song data available. Cannot make recommendations.")
            return []

        seed_ids = []
        for name in input_songs:
            found = False
            for song in self.songs:
                if name.lower() in song['track_name'].lower():
                    print(f" ✓ Found: {song['track_name']} by {song['artists']}")
                    seed_ids.append(song['track_id'])
                    found = True
                    break
            if not found:
                print(f" ✗ Not found: {name}")

        if not seed_ids:
            print("\nNo matching songs found. Try different names.")
            return []

        recommendations = {}
        for song_id in seed_ids:
            for neighbor_id, sim in self.graph.get(song_id, {}).items():
                if neighbor_id not in seed_ids:
                    recommendations[neighbor_id] = recommendations.get(neighbor_id, 0) + sim

        if not recommendations:
            print("No recommendations found.")
            return []

        # Get top recommendations
        top_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:num_recs]

        results = []
        for song_id, score in top_recs:
            song = next(s for s in self.songs if s['track_id'] == song_id)
            results.append({
                'Track': song['track_name'],
                'Artist': song['artists'],
                'Similarity': f"{score:.2f}",
                'Popularity': song['popularity'],
                'Danceability': song['danceability']
            })

        return pd.DataFrame(results)


if __name__ == "__main__":
    recommender = SpotifyRecommender()

    # Example songs if user doesn't provide input
    example_songs = ["Blinding Lights", "Dance Monkey", "Shape of You"]

    while True:
        print("\nEnter song names (comma separated) or 'quit' to exit:")
        user_input = input("> ").strip()

        if user_input.lower() == 'quit':
            break

        if not user_input:
            input_songs = example_songs
        else:
            input_songs = [name.strip() for name in user_input.split(",")]

        # Get number of recommendations
        while True:
            try:
                num_recs = int(input("\nHow many recommendations would you like? (1-20): ").strip())
                if 1 <= num_recs <= 20:
                    break
                print("Please enter a number between 1 and 20.")
            except ValueError:
                print("Please enter a valid number.")

        # Get and display recommendations
        recs = recommender.recommend(input_songs, num_recs)
        if not recs.empty:
            print("\nHere are your recommendations:")
            print(recs.to_string(index=False))
        else:
            print("\nNo recommendations could be generated.")
