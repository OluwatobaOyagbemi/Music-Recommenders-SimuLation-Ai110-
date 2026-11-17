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

Output of `python -m src.main` for the first two profiles (all seven are in [model_card.md](model_card.md#7-evaluation)):

```
Loaded songs: 20

================================================================
Profile: High-Energy Pop
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
Profile: Chill Lofi
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

The High-Energy Pop results match what you'd expect. *Sunrise City* is the only song that matches both genre and mood, so it wins clearly. *Gym Hero* (pop, but intense) and *Rooftop Lights* (happy, but indie pop) each match one of the two. After that, songs score only on energy closeness and non-acoustic sound.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Experiment 1: Weight shift (genre halved, energy doubled)

**Change:** in `src/recommender.py`, `GENRE_WEIGHT` went from 2.0 to 1.0 and `ENERGY_WEIGHT` from 1.0 to 2.0. Mood (1.5) and acoustic (0.5) stayed the same. **Is the math still valid?** Yes. The maximum score is still 1.0 + 1.5 + 2.0 + 0.5 = **5.0**, every component is still between 0 and its weight, and energy closeness is still `1 − |gap|`, so no score can go negative or above 5. The weights were set back to normal after the run.

**Top 5, baseline vs. experiment:**

| Profile | Baseline top 3 | Experiment top 3 |
|---|---|---|
| High-Energy Pop | Sunrise City, **Gym Hero**, Rooftop Lights | Sunrise City, **Rooftop Lights**, Gym Hero |
| Chill Lofi | Library Rain, Midnight Coding, **Focus Flow** | Library Rain, Midnight Coding, **Spacewalk Thoughts** |
| Deep Intense Rock | Storm Runner, Gym Hero, Strobe Heart | *(same)* |
| Sad but Hyped | **Paper Boats**, Campfire Anthem, Storm Runner | **Paper Boats**, Campfire Anthem, Storm Runner |
| Acoustic Metalhead | Iron Tempest, Campfire Anthem, Storm Runner | Iron Tempest, Strobe Heart, Gym Hero |

**More accurate or just different?** A bit of both:
- **More accurate for High-Energy Pop.** *Rooftop Lights* (happy indie pop) moved above *Gym Hero* (intense workout pop). For someone who asked for *happy* pop, that feels right.
- **Different but not clearly better for Chill Lofi.** *Spacewalk Thoughts* (chill ambient) passed *Focus Flow* (focused lofi). Both are reasonable study music.
- **Didn't fix the main problem.** For "Sad but Hyped" (wants energy 0.9), *Paper Boats* (energy 0.30) still ranks #1. Genre + mood (2.5 points) still beats the energy penalty (0.6 gap × 2 = 1.2 points).
- **Made one thing worse.** The Acoustic Metalhead's only acoustic-leaning pick (*Campfire Anthem*) dropped out of the top 3, replaced by electronic EDM and pop.

**Conclusion:** I kept the original weights. The shift helped one profile, hurt another, and didn't fix the biggest weakness, which is that matching labels can override a big energy mismatch.

### Experiment 2: Adversarial profiles

I ran four edge-case profiles alongside three normal ones. Full output and analysis are in [model_card.md](model_card.md#7-evaluation). Main findings:
- Conflicting preferences are settled by the labels, not the numbers.
- An unknown genre fails silently.
- *Gym Hero* shows up for 4 of the 7 profiles.

---

## Stretch Features

All four stretch challenges are implemented. The default `python -m src.main` output is unchanged; new behavior is turned on with flags:

```bash
python -m src.main --table                      # summary table with reasons
python -m src.main --mode mood-first            # genre-first | mood-first | energy-focused
python -m src.main --diverse                    # diversity penalty for repeated artists/genres
python -m src.main --profile "night owl" --table
```

### 1. Advanced song features

Five new columns in `data/songs.csv`. Each one is scored **only if a profile asks for it**, so older profiles behave exactly as before.

| Column | Type | Profile key | Scoring |
|---|---|---|---|
| `popularity` | 0–100 | `popularity` (target) | up to +0.5, closer is better |
| `release_decade` | 1960–2020 | `decade` | up to +0.5, 0 points if 50+ years apart |
| `mood_tags` | e.g. `nostalgic\|warm\|summer` | `tags` (list) | +0.5 per matching tag, max +1.0 |
| `instrumentalness` | 0–1 | `wants_instrumental` (bool) | up to +0.5 |
| `explicit` | 0/1 | `avoid_explicit` (bool) | −1.0 if explicit and avoided |

**Finding:** the explicit penalty is a *soft* penalty. In "Clean Party Mix" (pop, intense, avoids explicit), *Gym Hero* is explicit but still ranks #1 (4.93 vs. 4.32), because it matches everything else. A parent using "avoid explicit" would expect it to be removed entirely, so this should probably become a hard filter.

### 2. Scoring modes (Strategy pattern)

| Mode | genre | mood | energy | tags | Idea |
|---|---|---|---|---|---|
| `genre-first` (default) | 2.0 | 1.5 | 1.0 | 1.0 | the original recipe |
| `mood-first` | 1.0 | 2.5 | 1.0 | 1.5 | the vibe matters more than the label |
| `energy-focused` | 0.75 | 0.75 | 3.0 | 1.0 | how intense it feels matters most |

**What changed between modes:**
- **High-Energy Pop:** in `mood-first`, *Rooftop Lights* (happy indie pop) moves above *Gym Hero* (intense pop) to #2. That fits a "happy" request better.
- **Sad but Hyped:** `energy-focused` is the only mode that fixes this profile. *Campfire Anthem* (energy 0.72) moves above *Paper Boats* (0.30) to #1, and the rest of the list fills with high-energy songs. This was the main weakness found in the evaluation.
- **Chill Lofi:** the same songs appear in every mode, just in a slightly different order. A clear, consistent taste holds up regardless of the weights.

See [ai_interactions.md](ai_interactions.md) for why each mode is a weights object instead of a separate class.

### 3. Diversity penalty

With `--diverse`, the top k are picked one at a time. Each candidate loses **1.0 for every earlier pick by the same artist** and **0.5 for every earlier pick in the same genre**. For Chill Lofi, *Focus Flow* (lofi, by LoRoom, the same artist as *Midnight Coding*) drops from #3 to #5, and two other genres move up:

```
Profile: Chill Lofi
+----+--------------------------+----------------------+---------------+------------------------------------------------+
| #  | Song                     | Genre / Mood         | Score         | Reasons                                        |
+====+==========================+======================+===============+================================================+
| 1  | Library Rain             | lofi / chill         | 4.88 / 5.00   | - genre match: lofi (+2.0)                     |
|    | by Paper Lanterns        |                      |               | - mood match: chill (+1.5)                     |
|    |                          |                      |               | - energy 0.35 vs target 0.40 (+0.95)           |
|    |                          |                      |               | - acoustic fit (+0.43)                         |
+----+--------------------------+----------------------+---------------+------------------------------------------------+
| 2  | Midnight Coding          | lofi / chill         | 4.34 / 5.00   | - genre match: lofi (+2.0)                     |
|    | by LoRoom                |                      |               | - mood match: chill (+1.5)                     |
|    |                          |                      |               | - energy 0.42 vs target 0.40 (+0.98)           |
|    |                          |                      |               | - acoustic fit (+0.35)                         |
|    |                          |                      |               | - diversity: genre already listed (-0.50)      |
+----+--------------------------+----------------------+---------------+------------------------------------------------+
| 3  | Spacewalk Thoughts       | ambient / chill      | 2.84 / 5.00   | - mood match: chill (+1.5)                     |
|    | by Orbit Bloom           |                      |               | - energy 0.28 vs target 0.40 (+0.88)           |
|    |                          |                      |               | - acoustic fit (+0.46)                         |
+----+--------------------------+----------------------+---------------+------------------------------------------------+
| 4  | Coffee Shop Stories      | jazz / relaxed       | 1.42 / 5.00   | - energy 0.37 vs target 0.40 (+0.97)           |
|    | by Slow Stereo           |                      |               | - acoustic fit (+0.45)                         |
+----+--------------------------+----------------------+---------------+------------------------------------------------+
| 5  | Focus Flow               | lofi / focused       | 1.39 / 5.00   | - genre match: lofi (+2.0)                     |
|    | by LoRoom                |                      |               | - energy 0.40 vs target 0.40 (+1.00)           |
|    |                          |                      |               | - acoustic fit (+0.39)                         |
|    |                          |                      |               | - diversity: artist already listed (-1.00)     |
|    |                          |                      |               | - diversity: genre already listed (-1.00)      |
+----+--------------------------+----------------------+---------------+------------------------------------------------+
```

### 4. Summary table

`--table` prints an ASCII table with every reason behind each score. It uses no extra library. This example uses the advanced features:

```
Profile: Nostalgic Night Owl (tags, decade, instrumental)
+----+--------------------------+----------------------+---------------+------------------------------------------------+
| #  | Song                     | Genre / Mood         | Score         | Reasons                                        |
+====+==========================+======================+===============+================================================+
| 1  | Blue Hour Ballad         | jazz / melancholic   | 6.81 / 7.50   | - genre match: jazz (+2.0)                     |
|    | by Nina Ross             |                      |               | - mood match: melancholic (+1.5)               |
|    |                          |                      |               | - energy 0.33 vs target 0.35 (+0.98)           |
|    |                          |                      |               | - acoustic fit (+0.40)                         |
|    |                          |                      |               | - mood tags: nocturnal, nostalgic (+1.00)      |
|    |                          |                      |               | - 1960s vs 1980s (+0.30)                       |
|    |                          |                      |               | - popularity 31 vs target 35 (+0.48)           |
|    |                          |                      |               | - instrumental fit (+0.15)                     |
+----+--------------------------+----------------------+---------------+------------------------------------------------+
| 2  | Coffee Shop Stories      | jazz / relaxed       | 5.64 / 7.50   | - genre match: jazz (+2.0)                     |
|    | by Slow Stereo           |                      |               | - energy 0.37 vs target 0.35 (+0.98)           |
|    |                          |                      |               | - acoustic fit (+0.45)                         |
|    |                          |                      |               | - mood tags: warm, nostalgic (+1.00)           |
|    |                          |                      |               | - 1990s vs 1980s (+0.40)                       |
|    |                          |                      |               | - popularity 41 vs target 35 (+0.47)           |
|    |                          |                      |               | - instrumental fit (+0.35)                     |
+----+--------------------------+----------------------+---------------+------------------------------------------------+
| 3  | Moonlit Sonata Redux     | classical /          | 4.24 / 7.50   | - mood match: melancholic (+1.5)               |
|    | by Clara Vey             | melancholic          |               | - energy 0.22 vs target 0.35 (+0.87)           |
|    |                          |                      |               | - acoustic fit (+0.48)                         |
|    |                          |                      |               | - 1970s vs 1980s (+0.40)                       |
|    |                          |                      |               | - popularity 33 vs target 35 (+0.49)           |
|    |                          |                      |               | - instrumental fit (+0.49)                     |
+----+--------------------------+----------------------+---------------+------------------------------------------------+
| 4  | Dusty Backroads          | country / nostalgic  | 2.96 / 7.50   | - energy 0.55 vs target 0.35 (+0.80)           |
|    | by Wade Hollis           |                      |               | - acoustic fit (+0.34)                         |
|    |                          |                      |               | - mood tags: nostalgic, warm (+1.00)           |
|    |                          |                      |               | - 1990s vs 1980s (+0.40)                       |
|    |                          |                      |               | - popularity 54 vs target 35 (+0.41)           |
|    |                          |                      |               | - instrumental fit (+0.01)                     |
+----+--------------------------+----------------------+---------------+------------------------------------------------+
| 5  | Night Drive Loop         | synthwave / moody    | 2.90 / 7.50   | - energy 0.75 vs target 0.35 (+0.60)           |
|    | by Neon Echo             |                      |               | - acoustic fit (+0.11)                         |
|    |                          |                      |               | - mood tags: nocturnal, nostalgic (+1.00)      |
|    |                          |                      |               | - 1980s vs 1980s (+0.50)                       |
|    |                          |                      |               | - popularity 57 vs target 35 (+0.39)           |
|    |                          |                      |               | - instrumental fit (+0.30)                     |
+----+--------------------------+----------------------+---------------+------------------------------------------------+
```

---

## Limitations and Risks

- **Tiny, uneven catalog:** 20 made-up songs, and most genres have only one.
- **Labels beat numbers:** a genre + mood match (3.5 points) outweighs even a huge energy mismatch (at most −1 point), so users with conflicting tastes get results that ignore part of what they asked for.
- **Exact matching only:** "indie pop" gets no credit for a "pop" fan, and "relaxed" gets none for "chill".
- **No warning on bad matches:** an unknown genre still produces a confident-looking top 5.
- **It doesn't understand** lyrics, language, or how happy vs. sad a song sounds (valence isn't scored).

See [model_card.md](model_card.md) sections 6–7 for the full analysis.

---

## Reflection

Full model card: [**model_card.md**](model_card.md)

> **Draft. Rewrite in your own words.**

Building this showed me that a recommender is really just a way of turning preferences into numbers and sorting. Each song gets points for matching the user's genre, mood, energy and acoustic taste, and the "recommendation" is simply the top of the sorted list. What makes it feel smart is the data and the weights, not complicated code. Even this tiny version produced lists that felt right for clear tastes like "chill lofi."

Bias came from places I didn't expect. The weights are opinions: making genre worth twice as much as energy meant a quiet song beat what a "high-energy" user asked for. The uneven catalog meant lofi fans got great lists while metal fans got one real match and four fillers. Exact label matching treated "indie pop" as unrelated to "pop." None of that was intentional, which is the point: in a real app with millions of users, these small design choices decide which artists get heard and which users get served well.



