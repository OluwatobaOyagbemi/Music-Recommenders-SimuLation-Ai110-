"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Taste profile: a late-night study listener who wants calm, acoustic-leaning lofi
    user_prefs = {
        "genre": "lofi",          # favorite_genre
        "mood": "chill",          # favorite_mood
        "energy": 0.40,           # target_energy (0.0 = very calm, 1.0 = very intense)
        "likes_acoustic": True,   # prefers organic / acoustic sound over electronic
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
