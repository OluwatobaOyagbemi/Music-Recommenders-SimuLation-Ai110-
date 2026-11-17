# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Implement all four stretch challenges in one agentic session, using Claude Code in VS Code:
1. Add 5+ advanced song features to `data/songs.csv` and score them in `src/recommender.py`.
2. Add multiple scoring modes (genre-first, mood-first, energy-focused) that can be switched in `main.py`.
3. Add a diversity penalty so the same artist or genre doesn't crowd the top results.
4. Show results as a readable summary table that includes the reasons for each score.

**Prompts used:**

Main prompt: I pasted the four challenge descriptions from the assignment directly into Claude Code. The agent then planned and carried out the steps itself. The key instructions in that text were:

> "Introduce 5 or more complex attributes to your dataset … such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags … Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes."

> "Build two or more different ranking strategies (e.g., "Genre-First," "Mood-First," or "Energy-Focused") so a user can switch between modes in main.py … brainstorm a design pattern (like a simple "Strategy" pattern) that keeps your code modular."

> "Implement a "Diversity Penalty" that prevents the recommender from suggesting too many songs from the same artist or genre in the top results … penalize a song's score if its artist is already present in the top recommendations list."

> "Use a library like tabulate or simple ASCII formatting to display your top recommendations … the table must include the "reasons" for each score."

Follow-up prompts:
- *"Try running something yourself, like `python -m src.main --mode energy-focused --profile sad`, and note what you saw."* I asked the agent to run a mode comparison on the hardest profile and record the results below.

**What did the agent generate or change?**

- **Branch:** the agent created `feature/stretch-challenges` so the working version on `main` stayed safe.
- **`data/songs.csv`:** added 5 columns to all 20 songs:
  - `popularity` (0–100)
  - `release_decade` (1960–2020)
  - `mood_tags` (detailed tags separated by `|`, e.g. `nostalgic|warm|summer`)
  - `instrumentalness` (0–1)
  - `explicit` (0/1)
- **`src/recommender.py`:**
  - `Song` got the 5 new fields, with defaults so old code and tests still work.
  - `load_songs` parses them (tags become a list, explicit becomes True/False).
  - `score_song` scores them, but **only if the profile asks**:
    - mood tags: +0.5 per matching tag, capped at +1.0
    - decade closeness: up to +0.5
    - popularity closeness: up to +0.5
    - instrumental fit: up to +0.5
    - explicit: −1.0 if the user avoids explicit songs
  - New `ScoringStrategy` class plus 3 modes (`GENRE_FIRST`, `MOOD_FIRST`, `ENERGY_FOCUSED`) and a `STRATEGIES` lookup.
  - New `max_score()` so the output shows the right "out of" number for each profile and mode.
  - New `diversify()`: greedy re-ranking that subtracts 1.0 for each earlier pick by the same artist and 0.5 for each earlier pick in the same genre.
  - `recommend_songs` takes `strategy=` and `diversity=` arguments.
- **`src/main.py`:**
  - Command-line flags `--mode`, `--diverse`, `--table`, `--profile` and `-k`.
  - An ASCII table view, which needs no new library because `tabulate` wasn't installed.
  - 2 new profiles that use the advanced features.
- **`tests/test_recommender.py`:** 6 new tests for parsing, tag capping, the explicit penalty, strategy switching, max score, and the diversity penalty.
- **Commands run:** `python -m src.main` with each mode and flag, `pytest`, and a `diff` of the default output before and after the change.

**What did you verify or fix manually?**

Checks the agent ran:
- **Default output unchanged.** The agent saved the output from before the change and diffed it against the output after. The only difference was the "Dead Center" profile now showing `/ 1.00` instead of `/ 5.00`, which is a fix: that profile only sets energy, so 1.00 really is its maximum score.
- **Tests:** all 8 pass, including the original 2.
- **Formatting fix during the session:** the first version printed `+2.00` instead of `+2.0`, which would have made the outputs already in the docs inaccurate. The agent added a small formatter so the output stays the same.
- **Behavior that needed human review:** the "Clean Party Mix" profile avoids explicit songs, but *Gym Hero* (explicit) still ranks #1. It matches everything else so well that the −1.0 penalty isn't enough. Whether "avoid explicit" should be a soft penalty or a hard filter is a design decision, so it was flagged instead of silently changed.

**Mode comparison on "Sad but Hyped"** (folk, sad, energy 0.9, likes acoustic):

| Rank | `genre-first` (default) | `energy-focused` |
|---|---|---|
| 1 | Paper Boats: folk/sad, energy 0.30 (4.37) | **Campfire Anthem**: folk/uplifting, energy 0.72 (3.63) |
| 2 | Campfire Anthem (3.24) | Paper Boats (3.17) |
| 3 | Storm Runner (1.04) | Storm Runner (3.02) |
| 4 | Rooftop Lights (1.03) | Gym Hero (2.94) |
| 5 | Sunrise City (1.01) | Strobe Heart (2.86) |

What I saw:
- **Energy-focused does fix the energy problem.** The quiet *Paper Boats* drops to #2, and spots 3–5 are now real high-energy songs (0.91–0.95). Before, they were happy pop songs that only scored about 1 point each.
- **But it "fixes" it by mostly ignoring the "sad" part.** None of the top 5 except *Paper Boats* is sad, and *Campfire Anthem* is the opposite mood (uplifting). The mood match is only worth 0.75 in this mode, so it barely counts.
- **The real issue is the data, not just the weights.** The catalog has no song that is both sad *and* high-energy. No weight setting can recommend a song that doesn't exist, so every mode has to give up either the mood or the energy.
- **The scores at the bottom are bunched up** (3.02, 2.94, 2.86) and are almost entirely energy points. Spots 3–5 could swap places with tiny changes, so their order shouldn't be read as meaningful.
- **Math check:** the maximum is 0.75 + 0.75 + 3.0 + 0.5 = 5.00, matching the "/ 5.00" printed. *Campfire Anthem*'s energy points are 3.0 × (1 − |0.72 − 0.90|) = 3.0 × 0.82 = 2.46, which matches the output.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

**Strategy pattern.** Each ranking mode is a `ScoringStrategy`: a small, frozen object that holds a name, a description, and one weight per scoring component. The scoring function doesn't know or care which mode it's running. It just reads the weights from whichever strategy it's given.

**How did AI help you brainstorm or implement it?**

The challenge suggested the Strategy pattern, and the AI compared two ways to build it:
1. **A separate class per mode**, each with its own `score()` method. This is the textbook version, but it would copy the same genre, mood, energy and tag logic three times. Any bug fix would need to be made in three places.
2. **One scoring function plus a weights object per mode.** Every mode in this project uses the *same* scoring steps with *different* weights, so only the weights need to vary.

We chose option 2 because it's less code, and adding a mode is a few lines (one new `ScoringStrategy(...)` plus an entry in `STRATEGIES`). The original weights stayed as the `GENRE_FIRST` strategy, so the default behavior didn't change. If a future mode needs genuinely different *logic*, not just different weights, option 1 would be the right upgrade.

**How does the pattern appear in your final code?**

- [`ScoringStrategy`](src/recommender.py): the strategy class (a frozen dataclass of weights).
- `GENRE_FIRST`, `MOOD_FIRST`, `ENERGY_FOCUSED` and the `STRATEGIES` dict in [src/recommender.py](src/recommender.py): the three concrete strategies.
- `score_song(user_prefs, song, strategy)` and `recommend_songs(..., strategy=...)`: these take a strategy and use its weights.
- `Recommender(songs, strategy=...)`: the class version also accepts a strategy.
- [src/main.py](src/main.py): `--mode` looks up `STRATEGIES[args.mode]` and passes it in, which is how a user switches modes.
