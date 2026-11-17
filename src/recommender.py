import csv
from typing import Any, List, Dict, Tuple
from dataclasses import dataclass, asdict, field

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
    # Advanced features (defaults keep older code and tests working)
    popularity: int = 50                # 0-100, how mainstream the song is
    release_decade: int = 2010          # e.g. 1980, 2020
    mood_tags: List[str] = field(default_factory=lambda: [])  # e.g. ["nostalgic", "warm"]
    instrumentalness: float = 0.0       # 0-1, 1 = no vocals
    explicit: bool = False              # explicit lyrics

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


# ---------------------------------------------------------------------------
# Scoring strategies (Strategy pattern)
#
# A ScoringStrategy is a named set of weights. score_song() runs the same
# scoring steps for every strategy; only the weights change. Adding a new mode
# means adding one ScoringStrategy, not editing the scoring function.
# ---------------------------------------------------------------------------

# Original Algorithm Recipe weights (see README "How The System Works")
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.5
ENERGY_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 0.5

# Weights for the advanced features. They only apply if the profile asks for them.
TAGS_WEIGHT = 1.0           # max points for detailed mood tags (half per matching tag)
DECADE_WEIGHT = 0.5         # closeness to preferred release decade
POPULARITY_WEIGHT = 0.5     # closeness to target popularity (mainstream vs. niche)
INSTRUMENTAL_WEIGHT = 0.5   # fit with wanting / not wanting vocals
EXPLICIT_PENALTY = 1.0      # subtracted for explicit songs if the user avoids them

DECADE_RANGE = 50           # songs this many years away or more get 0 decade points

# Diversity penalties used when re-ranking (see diversify())
ARTIST_REPEAT_PENALTY = 1.0  # per song by the same artist already in the list
GENRE_REPEAT_PENALTY = 0.5   # per song of the same genre already in the list


@dataclass(frozen=True)
class ScoringStrategy:
    """A named ranking mode: the weight given to each scoring component."""
    name: str
    description: str
    genre: float
    mood: float
    energy: float
    acoustic: float = ACOUSTIC_WEIGHT
    tags: float = TAGS_WEIGHT
    decade: float = DECADE_WEIGHT
    popularity: float = POPULARITY_WEIGHT
    instrumental: float = INSTRUMENTAL_WEIGHT
    explicit_penalty: float = EXPLICIT_PENALTY


GENRE_FIRST = ScoringStrategy(
    name="genre-first",
    description="Genre matters most, then mood, then energy (the original recipe).",
    genre=GENRE_WEIGHT, mood=MOOD_WEIGHT, energy=ENERGY_WEIGHT,
)
MOOD_FIRST = ScoringStrategy(
    name="mood-first",
    description="Mood and mood tags matter most; genre is a tiebreaker.",
    genre=1.0, mood=2.5, energy=1.0, tags=1.5,
)
ENERGY_FOCUSED = ScoringStrategy(
    name="energy-focused",
    description="How close the energy is matters most; labels count less.",
    genre=0.75, mood=0.75, energy=3.0,
)

STRATEGIES: Dict[str, ScoringStrategy] = {
    s.name: s for s in (GENRE_FIRST, MOOD_FIRST, ENERGY_FOCUSED)
}

NUMERIC_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")

Scored = Tuple[Dict[str, Any], float, List[str]]


def _pts(x: float) -> str:
    """Formats a weight as 2.0 or 0.75 (one decimal unless more are needed)."""
    return f"{x:.1f}" if round(x, 1) == x else f"{x:.2f}"


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
    def __init__(self, songs: List[Song], strategy: ScoringStrategy = GENRE_FIRST):
        """Stores the catalog of Song objects and the scoring strategy to use."""
        self.songs = songs
        self.strategy = strategy

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k Song objects for this user, highest score first."""
        prefs = _profile_to_prefs(user)
        scored = [(song, score_song(prefs, asdict(song), self.strategy)[0]) for song in self.songs]
        ranked = sorted(scored, key=lambda pair: (-pair[1], pair[0].title))
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a one-line explanation of why a song scored the way it did."""
        score, reasons = score_song(_profile_to_prefs(user), asdict(song), self.strategy)
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict[str, Any]]:
    """Reads songs.csv into a list of dicts, converting numeric columns to int/float."""
    songs: List[Dict[str, Any]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row: Dict[str, Any] = dict(raw)
            row["id"] = int(row["id"])
            for name in NUMERIC_FIELDS:
                row[name] = float(row[name])
            # Advanced features: optional so older CSVs still load.
            row["popularity"] = int(row.get("popularity") or 50)
            row["release_decade"] = int(row.get("release_decade") or 2010)
            row["instrumentalness"] = float(row.get("instrumentalness") or 0.0)
            row["explicit"] = str(row.get("explicit") or "0").strip().lower() in ("1", "true")
            tags = str(row.get("mood_tags") or "")
            row["mood_tags"] = [t.strip() for t in tags.split("|") if t.strip()]
            songs.append(row)
    return songs


def score_song(
    user_prefs: Dict[str, Any],
    song: Dict[str, Any],
    strategy: ScoringStrategy = GENRE_FIRST,
) -> Tuple[float, List[str]]:
    """Scores one song against user_prefs using the strategy's weights; returns (score, reasons)."""
    w = strategy
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += w.genre
        reasons.append(f"genre match: {song['genre']} (+{_pts(w.genre)})")

    if song["mood"] == user_prefs.get("mood"):
        score += w.mood
        reasons.append(f"mood match: {song['mood']} (+{_pts(w.mood)})")

    if "energy" in user_prefs:
        # Reward closeness to the target, not higher or lower energy.
        closeness = 1.0 - abs(song["energy"] - user_prefs["energy"])
        points = w.energy * closeness
        score += points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} (+{points:.2f})"
        )

    if "likes_acoustic" in user_prefs:
        acoustic = song["acousticness"]
        fit = acoustic if user_prefs["likes_acoustic"] else 1.0 - acoustic
        points = w.acoustic * fit
        score += points
        label = "acoustic" if user_prefs["likes_acoustic"] else "non-acoustic"
        reasons.append(f"{label} fit (+{points:.2f})")

    # --- Advanced features (only scored if the profile sets them) ---

    wanted_tags = user_prefs.get("tags")
    if wanted_tags:
        matched = [t for t in song.get("mood_tags", []) if t in wanted_tags]
        if matched:
            points = min(w.tags, (w.tags / 2) * len(matched))
            score += points
            reasons.append(f"mood tags: {', '.join(matched)} (+{points:.2f})")

    if "decade" in user_prefs:
        decade = song.get("release_decade", 2010)
        gap = abs(decade - user_prefs["decade"])
        points = w.decade * max(0.0, 1.0 - gap / DECADE_RANGE)
        score += points
        reasons.append(f"{decade}s vs {user_prefs['decade']}s (+{points:.2f})")

    if "popularity" in user_prefs:
        popularity = song.get("popularity", 50)
        gap = abs(popularity - user_prefs["popularity"])
        points = w.popularity * (1.0 - gap / 100)
        score += points
        reasons.append(f"popularity {popularity} vs target {user_prefs['popularity']} (+{points:.2f})")

    if "wants_instrumental" in user_prefs:
        inst = song.get("instrumentalness", 0.0)
        fit = inst if user_prefs["wants_instrumental"] else 1.0 - inst
        points = w.instrumental * fit
        score += points
        label = "instrumental" if user_prefs["wants_instrumental"] else "vocal"
        reasons.append(f"{label} fit (+{points:.2f})")

    if user_prefs.get("avoid_explicit") and song.get("explicit"):
        score -= w.explicit_penalty
        reasons.append(f"explicit lyrics (-{_pts(w.explicit_penalty)})")

    return score, reasons


def max_score(user_prefs: Dict[str, Any], strategy: ScoringStrategy = GENRE_FIRST) -> float:
    """Returns the highest score possible for this profile under this strategy."""
    w = strategy
    parts = [
        ("genre" in user_prefs, w.genre),
        ("mood" in user_prefs, w.mood),
        ("energy" in user_prefs, w.energy),
        ("likes_acoustic" in user_prefs, w.acoustic),
        (bool(user_prefs.get("tags")), w.tags),
        ("decade" in user_prefs, w.decade),
        ("popularity" in user_prefs, w.popularity),
        ("wants_instrumental" in user_prefs, w.instrumental),
    ]
    return sum(weight for used, weight in parts if used)


def diversify(scored: List[Scored], k: int) -> List[Scored]:
    """Greedily picks k songs, penalizing each repeat of an artist or genre already picked."""
    remaining = list(scored)
    picked: List[Scored] = []
    while remaining and len(picked) < k:
        candidates: List[Tuple[Scored, int]] = []
        for index, (song, base, reasons) in enumerate(remaining):
            same_artist = sum(1 for s, _, _ in picked if s["artist"] == song["artist"])
            same_genre = sum(1 for s, _, _ in picked if s["genre"] == song["genre"])
            artist_pen = same_artist * ARTIST_REPEAT_PENALTY
            genre_pen = same_genre * GENRE_REPEAT_PENALTY
            extra: List[str] = []
            if artist_pen:
                extra.append(f"diversity: artist already listed (-{artist_pen:.2f})")
            if genre_pen:
                extra.append(f"diversity: genre already listed (-{genre_pen:.2f})")
            candidates.append(((song, base - artist_pen - genre_pen, reasons + extra), index))
        # Highest adjusted score wins; ties go to the title earlier in A-Z.
        best, best_index = min(candidates, key=lambda c: (-c[0][1], str(c[0][0]["title"])))
        picked.append(best)
        remaining.pop(best_index)
    return picked


def recommend_songs(
    user_prefs: Dict[str, Any],
    songs: List[Dict[str, Any]],
    k: int = 5,
    strategy: ScoringStrategy = GENRE_FIRST,
    diversity: bool = False,
) -> List[Tuple[Dict[str, Any], float, str]]:
    """Scores every song, ranks highest first (ties by title), and returns the top k as (song, score, explanation)."""
    scored: List[Scored] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, strategy)  # score_song is the "judge"
        scored.append((song, score, reasons))
    scored.sort(key=lambda item: (-item[1], str(item[0]["title"])))
    top = diversify(scored, k) if diversity else scored[:k]
    return [(song, score, "; ".join(reasons)) for song, score, reasons in top]
