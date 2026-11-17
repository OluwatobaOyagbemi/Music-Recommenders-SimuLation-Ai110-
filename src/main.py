"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main                         # all profiles, genre-first, list view
    python -m src.main --table                 # summary table view
    python -m src.main --mode mood-first       # switch scoring strategy
    python -m src.main --diverse               # apply artist/genre diversity penalty
    python -m src.main --profile lofi --table  # only profiles whose name contains "lofi"
"""

import argparse
import textwrap
from typing import Any, Dict, List, Tuple

from src.recommender import STRATEGIES, ScoringStrategy, load_songs, max_score, recommend_songs

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
    # --- Profiles that use the advanced features ---
    "Nostalgic Night Owl (tags, decade, instrumental)": {
        "genre": "jazz",
        "mood": "melancholic",
        "energy": 0.35,
        "likes_acoustic": True,
        "tags": ["nostalgic", "nocturnal", "warm"],  # detailed mood tags
        "decade": 1980,                              # preferred release decade
        "popularity": 35,                            # prefers lesser-known songs
        "wants_instrumental": True,
    },
    "Clean Party Mix (avoids explicit, wants hits)": {
        "genre": "pop",
        "mood": "intense",
        "energy": 0.90,
        "likes_acoustic": False,
        "tags": ["euphoric", "party"],
        "popularity": 85,
        "avoid_explicit": True,
    },
}

WIDTH = 64
Rec = Tuple[Dict[str, Any], float, str]


def print_recommendations(name: str, user_prefs: Dict[str, Any], recommendations: List[Rec], best: float) -> None:
    """Prints one profile's top-k results as a readable block with per-song reasons."""
    print("=" * WIDTH)
    print(f"Profile: {name}")
    print("  " + ", ".join(f"{key}={value}" for key, value in user_prefs.items()))
    print("=" * WIDTH)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']}/{song['mood']}]")
        print(f"   Score: {score:.2f} / {best:.2f}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def print_table(name: str, recommendations: List[Rec], best: float) -> None:
    """Prints one profile's top-k results as an ASCII table, including every reason."""
    headers = ["#", "Song", "Genre / Mood", "Score", "Reasons"]
    widths = [2, 24, 20, 13, 46]

    def cell_lines(text: str, width: int) -> List[str]:
        lines: List[str] = []
        for part in text.split("\n"):
            lines.extend(textwrap.wrap(part, width) or [""])
        return lines

    def row(cells: List[str]) -> str:
        wrapped = [cell_lines(c, w) for c, w in zip(cells, widths)]
        height = max(len(lines) for lines in wrapped)
        out: List[str] = []
        for i in range(height):
            parts = [(lines[i] if i < len(lines) else "").ljust(w) for lines, w in zip(wrapped, widths)]
            out.append("| " + " | ".join(parts) + " |")
        return "\n".join(out)

    rule = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(f"Profile: {name}")
    print(rule)
    print(row(headers))
    print(rule.replace("-", "="))
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = "\n".join("- " + r for r in explanation.split("; ") if r)
        print(row([
            str(rank),
            f"{song['title']}\nby {song['artist']}",
            f"{song['genre']} / {song['mood']}",
            f"{score:.2f} / {best:.2f}",
            reasons,
        ]))
        print(rule)
    print()


def parse_args() -> argparse.Namespace:
    """Reads command-line options for mode, diversity, view, and profile filter."""
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=sorted(STRATEGIES), default="genre-first",
                        help="scoring strategy to rank with (default: genre-first)")
    parser.add_argument("--diverse", action="store_true",
                        help="penalize repeated artists/genres in the top results")
    parser.add_argument("--table", action="store_true", help="show results as a summary table")
    parser.add_argument("--profile", default="", help="only run profiles whose name contains this text")
    parser.add_argument("-k", type=int, default=5, help="number of songs to recommend (default: 5)")
    return parser.parse_args()


def main() -> None:
    """Loads the catalog and prints the top k recommendations for each selected profile."""
    args = parse_args()
    strategy: ScoringStrategy = STRATEGIES[args.mode]
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")
    if args.mode != "genre-first" or args.diverse:
        print(f"Mode: {strategy.name} ({strategy.description})"
              + ("  |  diversity penalty ON" if args.diverse else "") + "\n")

    for name, user_prefs in PROFILES.items():
        if args.profile.lower() not in name.lower():
            continue
        recommendations = recommend_songs(user_prefs, songs, k=args.k,
                                          strategy=strategy, diversity=args.diverse)
        best = max_score(user_prefs, strategy)
        if args.table:
            print_table(name, recommendations, best)
        else:
            print_recommendations(name, user_prefs, recommendations, best)


if __name__ == "__main__":
    main()
