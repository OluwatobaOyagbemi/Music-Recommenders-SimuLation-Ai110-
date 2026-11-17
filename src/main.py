"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs

# Taste profiles to try. Each is a dict of target values for the scored features.
PROFILES = {
    # --- Core profiles ---
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.80,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre": "lofi",          # favorite_genre
        "mood": "chill",          # favorite_mood
        "energy": 0.40,           # target_energy (0.0 = very calm, 1.0 = very intense)
        "likes_acoustic": True,   # prefers organic / acoustic sound over electronic
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.90,
        "likes_acoustic": False,
    },
    # --- Adversarial / edge-case profiles ---
    "Sad but Hyped (conflict: sad mood, 0.9 energy)": {
        "genre": "folk",
        "mood": "sad",
        "energy": 0.90,
        "likes_acoustic": True,
    },
    "Acoustic Metalhead (conflict: metal + loves acoustic)": {
        "genre": "metal",
        "mood": "angry",
        "energy": 0.95,
        "likes_acoustic": True,
    },
    "Ghost Genre (genre/mood not in catalog)": {
        "genre": "k-pop",
        "mood": "euphoric",
        "energy": 0.70,
        "likes_acoustic": False,
    },
    "Dead Center (energy 0.5, no genre or mood)": {
        "energy": 0.50,
    },
}

WIDTH = 64


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Prints one profile's top-k results as a readable block with per-song reasons."""
    print("=" * WIDTH)
    print(f"Profile: {name}")
    print("  " + ", ".join(f"{key}={value}" for key, value in user_prefs.items()))
    print("=" * WIDTH)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']}/{song['mood']}]")
        print(f"   Score: {score:.2f} / 5.00")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    """Loads the catalog and prints the top 5 recommendations for each profile."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)


if __name__ == "__main__":
    main()
