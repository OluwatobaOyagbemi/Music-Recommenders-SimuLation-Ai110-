from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Stretch features ---------------------------------------------------------

from src.recommender import (
    ENERGY_FOCUSED,
    GENRE_FIRST,
    MOOD_FIRST,
    load_songs,
    max_score,
    recommend_songs,
    score_song,
)


def _song(**overrides):
    base = {
        "id": 1, "title": "T", "artist": "A", "genre": "pop", "mood": "happy",
        "energy": 0.5, "tempo_bpm": 100.0, "valence": 0.5, "danceability": 0.5,
        "acousticness": 0.5, "popularity": 50, "release_decade": 2010,
        "mood_tags": [], "instrumentalness": 0.0, "explicit": False,
    }
    base.update(overrides)
    return base


def test_load_songs_parses_advanced_features():
    songs = load_songs("data/songs.csv")
    first = songs[0]
    assert isinstance(first["popularity"], int)
    assert isinstance(first["release_decade"], int)
    assert isinstance(first["mood_tags"], list) and first["mood_tags"]
    assert isinstance(first["instrumentalness"], float)
    assert isinstance(first["explicit"], bool)


def test_mood_tags_give_half_weight_per_match_capped():
    prefs = {"tags": ["warm", "nostalgic", "cozy"]}
    one, _ = score_song(prefs, _song(mood_tags=["warm"]))
    three, _ = score_song(prefs, _song(mood_tags=["warm", "nostalgic", "cozy"]))
    assert one == 0.5
    assert three == 1.0  # capped at TAGS_WEIGHT


def test_explicit_penalty_only_when_user_avoids_it():
    clean, _ = score_song({"avoid_explicit": True}, _song(explicit=False))
    dirty, reasons = score_song({"avoid_explicit": True}, _song(explicit=True))
    assert clean - dirty == 1.0
    assert any("explicit" in r for r in reasons)


def test_strategies_change_the_ranking():
    # Song "G" matches genre only; song "M" matches mood only.
    songs = [
        _song(title="G", genre="rock", mood="sad"),
        _song(title="M", genre="pop", mood="angry"),
    ]
    prefs = {"genre": "rock", "mood": "angry"}
    assert recommend_songs(prefs, songs, k=1, strategy=GENRE_FIRST)[0][0]["title"] == "G"
    assert recommend_songs(prefs, songs, k=1, strategy=MOOD_FIRST)[0][0]["title"] == "M"


def test_max_score_matches_strategy_weights():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.5, "likes_acoustic": True}
    assert max_score(prefs, GENRE_FIRST) == 5.0
    assert max_score(prefs, ENERGY_FOCUSED) == 0.75 + 0.75 + 3.0 + 0.5


def test_diversity_penalty_pushes_down_repeated_artist():
    songs = [
        _song(title="A1", artist="Same", genre="pop", energy=0.50),
        _song(title="A2", artist="Same", genre="rock", energy=0.50),
        _song(title="B1", artist="Other", genre="jazz", energy=0.30),
    ]
    prefs = {"energy": 0.5}
    plain = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=3)]
    diverse = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=3, diversity=True)]
    assert plain == ["A1", "A2", "B1"]
    assert diverse == ["A1", "B1", "A2"]  # A2 drops: same artist already listed
