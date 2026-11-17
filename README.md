# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

My version is a small content-based music recommender. It loads a 10-song catalog from `data/songs.csv`, compares each song to a user's taste profile (favorite genre, favorite mood, target energy level, and whether they like acoustic music), and gives each song a score out of 5. Genre matches count most, then mood, then how close the song's energy is to what the user wants. The system ranks the songs by score and returns the top picks, each with a plain-language explanation of why it was chosen. Because it uses song attributes rather than other listeners' behavior, it can recommend any song in the catalog right away, but it tends to keep users inside the genres and moods they already chose.



## How The System Works

Real-world platforms like Spotify and YouTube use hybrid recommenders. **Collaborative filtering** learns from millions of users' behavior (likes, skips, saves, playlist co-occurrence, listen time) to find "people like you also loved…" patterns. **Content-based filtering** describes each song by its attributes (genre, mood, tempo, energy) and recommends songs similar to what a user already likes. At scale, these signals feed machine-learning models that first narrow millions of tracks to a few hundred candidates and then rank them. My simulation has no listening history, so it is a purely **content-based** recommender. It prioritizes **genre first, then mood, then how close a song's energy is to the user's target**, with a small bonus for acoustic sound. It favors songs that *match* the user's vibe over songs that are simply "more" of something.

### Features used

**`Song`**
- `genre`: categorical; exact match with the user's favorite
- `mood`: categorical; exact match with the user's favorite
- `energy` (0–1): numeric; scored by closeness to the user's target
- `acousticness` (0–1): numeric; rewarded if the user likes acoustic music
- `title`, `artist`, `id`: used for display only, not for scoring
- `tempo_bpm`, `valence`, `danceability`: loaded but not scored in v1. In this dataset, tempo and acousticness track energy almost perfectly (correlation 0.96 and −0.99), so scoring them as well would mostly double-count energy.

**`UserProfile`**
- `favorite_genre`
- `favorite_mood`
- `target_energy` (0–1)
- `likes_acoustic` (True/False)

### Algorithm Recipe

**Scoring Rule (one song → one number):**

| Component | Points |
|---|---|
| Genre matches `favorite_genre` | +2.0 |
| Mood matches `favorite_mood` | +1.5 |
| Energy closeness: `1.0 × (1 − |song.energy − target_energy|)` | 0 to +1.0 |
| Acoustic fit: if `likes_acoustic`, `0.5 × acousticness`; otherwise `0.5 × (1 − acousticness)` | 0 to +0.5 |

Maximum score = 5.0. Each component that adds points also adds a human-readable reason (for example, "genre match: lofi"), which becomes the explanation.

The energy term uses **distance, not raw value**. A user who wants energy 0.4 gets the most points from a song at 0.4, while songs at 0.1 or 0.9 earn less. Rewarding high energy directly would push every user toward gym music.

**Ranking Rule (many scores → a top-k list):** Score every song in the catalog, sort by score from highest to lowest (ties broken by title), and return the top `k`. The scoring rule decides how good one song is for this user. The ranking rule decides which songs to show and in what order. Keeping them separate means either one can change, such as new weights or a diversity rule like "max 2 songs per artist", without rewriting the other.

```
UserProfile ──┐
              ├─► score_song() for each Song ─► sort by score ─► top k + reasons
songs.csv ────┘
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



