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
- `tempo_bpm`, `valence`, `danceability`: loaded but not scored in v1. Across the 20-song catalog, tempo and acousticness closely track energy (correlation 0.89 and −0.92), so scoring them as well would mostly double-count energy. Valence (0.22–0.88) is the strongest candidate to add next (see Expected Biases).

**`UserProfile`**
- `favorite_genre`
- `favorite_mood`
- `target_energy` (0–1)
- `likes_acoustic` (True/False)

### Catalog

`data/songs.csv` has 20 songs. The original 10 were expanded with 10 more to cover genres the starter file lacked (hip-hop, classical, country, metal, r&b, reggae, edm, folk) and moods it lacked (confident, melancholic, nostalgic, angry, romantic, uplifting, energetic, sad). A few songs deliberately break the usual "high energy = low acousticness" pattern. For example, *Campfire Anthem* is an upbeat folk song (energy 0.72) that is still very acoustic (0.85).

### Example taste profile

`src/main.py` uses this profile, a late-night study listener:

```python
user_prefs = {
    "genre": "lofi",
    "mood": "chill",
    "energy": 0.40,
    "likes_acoustic": True,
}
```

**Can it tell "intense rock" from "chill lofi"?** Yes, clearly. *Library Rain* (chill lofi) scores 4.88 out of 5, while *Storm Runner* (intense rock) scores 0.54 and *Iron Tempest* (angry metal) scores 0.45. **Is it too narrow?** Somewhat. Only 3 songs are lofi and 3 are chill, so after the top 4 results every song earns points from energy and acoustic fit alone. In that range, *Paper Boats* (a sad folk song) scores 1.37, almost the same as *Coffee Shop Stories* (relaxed jazz, 1.42), because the profile has no way to say "calm but not sad."

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

### Data flow

```
INPUT                      PROCESS (the loop)                         OUTPUT (the ranking)
─────                      ──────────────────                         ────────────────────
user_prefs (dict) ─┐       for each song in songs.csv:
                   ├────►    genre match?      +2.0                   sort all 20 by score
songs.csv          │         mood match?       +1.5         ────►     (ties → title A–Z)
 └► load_songs() ──┘         energy closeness  0–1.0                  return top k
    (20 dicts)               acoustic fit      0–0.5                  (song, score, "because…")
                             → (score, reasons)
```

### Expected biases and limitations

- **Genre dominates.** A genre match (+2.0) is the single biggest component, worth more than a mood match (+1.5). A wrong-genre song can only win by matching both mood and energy well, so a great song in a neighboring genre ("indie pop" for a "pop" fan) usually ranks below a so-so song in the exact genre.
- **Exact string matching.** "relaxed", "focused" and "chill" are treated as completely different moods, and so are "pop" and "indie pop". Close matches earn zero points.
- **Uneven catalog.** Lofi has 3 songs while most genres have 1, so lofi fans get a full top 3 of genre matches and metal fans get one match followed by filler.
- **No sense of sad vs. happy.** Valence isn't scored, so for a calm listener a sad ballad and a peaceful one look nearly the same.
- **Filter bubble.** Like any content-based system, it only recommends more of what the user already said they like. It never surprises them the way collaborative filtering can.

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

Output of `python -m src.main` for the default pop/happy profile and the late-night study profile:

```
Loaded songs: 20

================================================================
Profile: Default pop/happy
  genre=pop, mood=happy, energy=0.8, likes_acoustic=False
================================================================
1. Sunrise City by Neon Echo  [pop/happy]
   Score: 4.89 / 5.00
     - genre match: pop (+2.0)
     - mood match: happy (+1.5)
     - energy 0.82 vs target 0.80 (+0.98)
     - non-acoustic fit (+0.41)
2. Gym Hero by Max Pulse  [pop/intense]
   Score: 3.35 / 5.00
     - genre match: pop (+2.0)
     - energy 0.93 vs target 0.80 (+0.87)
     - non-acoustic fit (+0.47)
3. Rooftop Lights by Indigo Parade  [indie pop/happy]
   Score: 2.79 / 5.00
     - mood match: happy (+1.5)
     - energy 0.76 vs target 0.80 (+0.96)
     - non-acoustic fit (+0.33)
4. Concrete Crown by Block Theory  [hip-hop/confident]
   Score: 1.42 / 5.00
     - energy 0.78 vs target 0.80 (+0.98)
     - non-acoustic fit (+0.44)
5. Storm Runner by Voltline  [rock/intense]
   Score: 1.34 / 5.00
     - energy 0.91 vs target 0.80 (+0.89)
     - non-acoustic fit (+0.45)

================================================================
Profile: Late-night study listener
  genre=lofi, mood=chill, energy=0.4, likes_acoustic=True
================================================================
1. Library Rain by Paper Lanterns  [lofi/chill]
   Score: 4.88 / 5.00
     - genre match: lofi (+2.0)
     - mood match: chill (+1.5)
     - energy 0.35 vs target 0.40 (+0.95)
     - acoustic fit (+0.43)
2. Midnight Coding by LoRoom  [lofi/chill]
   Score: 4.84 / 5.00
     - genre match: lofi (+2.0)
     - mood match: chill (+1.5)
     - energy 0.42 vs target 0.40 (+0.98)
     - acoustic fit (+0.35)
3. Focus Flow by LoRoom  [lofi/focused]
   Score: 3.39 / 5.00
     - genre match: lofi (+2.0)
     - energy 0.40 vs target 0.40 (+1.00)
     - acoustic fit (+0.39)
4. Spacewalk Thoughts by Orbit Bloom  [ambient/chill]
   Score: 2.84 / 5.00
     - mood match: chill (+1.5)
     - energy 0.28 vs target 0.40 (+0.88)
     - acoustic fit (+0.46)
5. Coffee Shop Stories by Slow Stereo  [jazz/relaxed]
   Score: 1.42 / 5.00
     - energy 0.37 vs target 0.40 (+0.97)
     - acoustic fit (+0.45)
```

The pop/happy results match what you'd expect. *Sunrise City* is the only song that matches both genre and mood, so it wins clearly. *Gym Hero* (pop, but intense) and *Rooftop Lights* (happy, but indie pop) each match one of the two. After that, songs score only on energy closeness and non-acoustic sound.

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



