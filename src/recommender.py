import csv
from typing import Any, List, Dict, Tuple
from dataclasses import dataclass, asdict

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

# Algorithm Recipe weights (see README "How The System Works")
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.5
ENERGY_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 0.5

NUMERIC_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")


def _profile_to_prefs(user: "UserProfile") -> Dict[str, Any]:
    """Converts a UserProfile into the dict format used by score_song()."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Stores the catalog of Song objects to recommend from."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k Song objects for this user, highest score first."""
        prefs = _profile_to_prefs(user)
        scored = [(song, score_song(prefs, asdict(song))[0]) for song in self.songs]
        ranked = sorted(scored, key=lambda pair: (-pair[1], pair[0].title))
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a one-line explanation of why a song scored the way it did."""
        score, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict[str, Any]]:
    """Reads songs.csv into a list of dicts, converting numeric columns to int/float."""
    songs: List[Dict[str, Any]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row: Dict[str, Any] = dict(raw)
            row["id"] = int(row["id"])
            for field in NUMERIC_FIELDS:
                row[field] = float(row[field])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict[str, Any], song: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Scores one song against user_prefs and returns (score out of 5.0, list of reasons)."""
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {song['genre']} (+{GENRE_WEIGHT:.1f})")

    if song["mood"] == user_prefs.get("mood"):
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {song['mood']} (+{MOOD_WEIGHT:.1f})")

    if "energy" in user_prefs:
        # Reward closeness to the target, not higher or lower energy.
        closeness = 1.0 - abs(song["energy"] - user_prefs["energy"])
        points = ENERGY_WEIGHT * closeness
        score += points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} (+{points:.2f})"
        )

    if "likes_acoustic" in user_prefs:
        acoustic = song["acousticness"]
        fit = acoustic if user_prefs["likes_acoustic"] else 1.0 - acoustic
        points = ACOUSTIC_WEIGHT * fit
        score += points
        label = "acoustic" if user_prefs["likes_acoustic"] else "non-acoustic"
        reasons.append(f"{label} fit (+{points:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict[str, Any], songs: List[Dict[str, Any]], k: int = 5) -> List[Tuple[Dict[str, Any], float, str]]:
    """Scores every song, sorts highest first (ties by title), and returns the top k as (song, score, explanation)."""
    scored: List[Tuple[Dict[str, Any], float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)  # score_song is the "judge"
        scored.append((song, score, "; ".join(reasons)))
    return sorted(scored, key=lambda item: (-item[1], str(item[0]["title"])))[:k]
