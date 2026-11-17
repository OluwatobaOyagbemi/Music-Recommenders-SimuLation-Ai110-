# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**: a tiny music recommender that matches songs to your vibe.

---

## 2. Goal and Intended Use  

**Goal:** VibeMatch suggests the top 5 songs a person is most likely to enjoy right now. It doesn't predict ratings or plays. It just ranks songs by how well they fit what the user says they want.

**What it assumes about the user:** that they can describe their taste with four things: a favorite genre, a mood, an energy level from 0 to 1, and whether they like acoustic sound. It assumes those four things stay fixed for the session.

**Intended use:**
- Classroom exploration of how recommenders turn data into rankings.
- Experimenting with weights and seeing how results change.
- Showing why each song was picked, using the "reasons" it prints.

**Not intended for:**
- Real users or a real music app. The catalog is only 20 made-up songs.
- Judging what music is "good". A low score only means "doesn't match these four settings."
- Learning anyone's taste over time. It has no memory, no history, and no feedback loop.
- Any decision that matters to a person, like ranking artists for pay or promotion.

---

## 3. How the Model Works  

**How it works, in plain language**

Imagine a friend picking songs for you from a stack of 20 records. Before they start, you tell them four things: your favorite genre, the mood you're in, how energetic you want the music to be (from very calm to very intense), and whether you like acoustic, "unplugged" sound.

Your friend then goes through every record one at a time and gives it points:

- **Right genre:** 2 points. This counts most, because genre is usually the most stable part of someone's taste.
- **Right mood:** 1.5 points.
- **Right energy level:** up to 1 point. A song gets the full point if its energy is exactly what you asked for and fewer points the further away it is, whether it's too calm or too intense. This means asking for "medium energy" gets you medium-energy songs, not the loudest songs in the stack.
- **Acoustic fit:** up to half a point. If you like acoustic sound, more acoustic songs earn more; if you don't, more electronic songs earn more.

The best possible score is 5. Once every record has a score, your friend sorts the stack from highest to lowest and hands you the top five. Each one comes with a note listing the points it earned, like "genre match: pop (+2.0)", so you can see exactly why it was picked.

The system doesn't look at what other people listen to, only at the songs' own descriptions. That means it can recommend a brand-new song right away, but it will mostly give you more of what you already said you like.

**Changes from the starter logic:** The starter code returned the first few songs in the file no matter who was asking. This version scores every song against the user's taste, rewards being *close* to the target energy instead of simply higher or lower, adds an acoustic preference, and explains every recommendation.

---

## 4. Data  

- **Size:** 20 songs in `data/songs.csv`. The starter file had 10, and I added 10 more.
- **Features per song:** title, artist, genre, mood, energy, tempo (BPM), valence (how happy it sounds), danceability, and acousticness. The numeric ones are on a 0–1 scale except tempo.
- **Features actually scored:** genre, mood, energy and acousticness. Tempo, valence and danceability are loaded but not used yet.
- **Genres (15):** lofi, pop, indie pop, rock, metal, edm, synthwave, hip-hop, r&b, reggae, country, folk, jazz, ambient, classical.
- **Moods (14):** chill, happy, intense, relaxed, moody, focused, confident, melancholic, nostalgic, angry, romantic, uplifting, energetic, sad.
- **What I added:** 10 songs to cover genres and moods the starter file didn't have. A few were chosen on purpose to break patterns, like *Campfire Anthem*, an upbeat song that is still very acoustic.

**Limits:**
- It's tiny. Most genres have only 1 song, so many users run out of real matches after #1.
- It's uneven. Lofi has 3 songs, while metal, classical, country and others have 1.
- The songs and numbers are made up, not measured from real audio.
- Each song gets exactly one genre and one mood. Real songs often fit several.
- Lyrics, language, artist popularity, release year and culture aren't included at all.

---

## 5. Strengths  

- **Clear, single-genre tastes work well.** Chill Lofi, High-Energy Pop and Deep Intense Rock all got a #1 that felt exactly right, scoring 4.88–4.94 out of 5.
- **It clearly separates opposite vibes.** The Chill Lofi and Deep Intense Rock lists share zero songs.
- **"Closer is better" for energy works.** Asking for medium energy gets medium-energy songs, not just the loudest ones.
- **Every pick is explained.** Each song lists the points it earned, so you can always see *why* it ranked where it did. That made bugs and biases easy to spot.
- **New songs work on day one.** It doesn't need anyone else's listening history.

---

## 6. Observed Behavior and Biases 

**Main weakness found: matching labels overpower the energy preference.** A genre match plus a mood match is worth 3.5 points, while being completely wrong on energy costs at most 1 point. So when a user's preferences conflict, the labels always win. In the "Sad but Hyped" test (folk, sad, energy 0.9), the top pick was *Paper Boats*, a quiet song with energy 0.30, which is the opposite of the 0.9 the user asked for. The same thing happens with acoustic taste: the "Acoustic Metalhead" got *Iron Tempest* (acousticness 0.03) as #1, because the acoustic preference is worth only half a point. In practice this means users whose tastes don't fit neatly into one genre-and-mood label get recommendations that ignore part of what they asked for.

**Other limitations:**
- **Uneven catalog.** Lofi has 3 songs and folk, jazz and pop have 2 each, but most genres have only 1. A metal or classical fan gets one real match and then four unrelated songs.
- **Exact label matching.** "pop" and "indie pop", or "chill" and "relaxed", are treated as completely unrelated. A user can be underserved just because of how a song happens to be labeled.
- **Silent failure.** If the user's genre or mood isn't in the catalog (the "Ghost Genre" test, k-pop / euphoric), every song scores between about 1.2 and 1.4, and the system shows its top 5 anyway with no warning that nothing actually matched.
- **Filter bubble.** The system only recommends what matches stated preferences. It never suggests something new, and it ignores valence (happy vs. sad sound), tempo and lyrics.

---

## 7. Evaluation Process  

**In short:** I tested 7 profiles (3 normal and 4 designed to trick the system), compared their top 5 lists in pairs, and ran one weight experiment (genre halved, energy doubled). I checked whether the #1 song made sense, whether the list felt right, and which score component decided the order. Details are below.

**Profiles tested** (all defined in `src/main.py`):

| Profile | genre | mood | energy | likes_acoustic | Purpose |
|---|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.80 | no | normal user |
| Chill Lofi | lofi | chill | 0.40 | yes | normal user |
| Deep Intense Rock | rock | intense | 0.90 | no | normal user |
| Sad but Hyped | folk | sad | 0.90 | yes | conflict: sad mood but high energy |
| Acoustic Metalhead | metal | angry | 0.95 | yes | conflict: metal but loves acoustic |
| Ghost Genre | k-pop | euphoric | 0.70 | no | genre and mood not in the catalog |
| Dead Center | — | — | 0.50 | — | only one preference given |

For each profile I checked whether the #1 song made sense, whether the top 5 "felt" like that listener, and which part of the score decided the order. The two existing unit tests also pass (`pytest`).

**Does it feel right?** For the three normal profiles, yes. Chill Lofi returns two chill lofi tracks, then focused lofi, then chill ambient, which is exactly what I'd put on to study. Deep Intense Rock gives *Storm Runner* first (4.94 of 5), followed by other loud, intense songs.

**Why did *Sunrise City* rank first for High-Energy Pop?** It's the only song that matches **both** pop and happy (2.0 + 1.5). Its energy, 0.82, is almost exactly the 0.80 target (+0.98), and it's mostly electronic, which suits a non-acoustic listener (+0.41). Total: 4.89 out of 5. No other song matches both labels, so nothing else gets close.

**What surprised me:**
1. **Conflicts are always settled by the labels.** "Sad but Hyped" got a quiet sad song (energy 0.30) as #1 even though they asked for 0.9 energy.
2. ***Gym Hero* keeps showing up.** It's in the top 5 for 4 of the 7 profiles: High-Energy Pop (#2), Deep Intense Rock (#2), the Acoustic Metalhead (#5) and Ghost Genre (#5).
3. **The unknown genre fails quietly.** Ghost Genre still got a confident-looking top 5, all scoring about 1.3, essentially ranked by energy alone.
4. **The Dead Center profile is ranked by energy only.** That's correct behavior, but it shows how little the system can do with one preference: a romantic R&B song and a lofi study track sit side by side.

**Why does *Gym Hero* keep showing up for people who just want "Happy Pop"?** The system doesn't understand "happy pop" as one idea. It checks separately: is it pop? Is it happy? Is the energy close? *Gym Hero* is labeled pop (+2 points), has high energy close to 0.8 (+0.87), and is electronic (+0.47). That earns 3.35 points without being happy at all. *Rooftop Lights* is genuinely happy, but it's labeled "indie pop", which the system treats as a completely different genre, so it misses the 2 genre points and lands just behind. To the recommender, "pop and pumped up" looks more like "happy pop" than "happy and indie" does.

**Comparing profiles in pairs:**
- **High-Energy Pop vs. Chill Lofi:** These share no songs at all. Pop leans toward bright, loud, electronic tracks (energy 0.76–0.93), while lofi shifts to soft, acoustic, low-energy tracks (0.28–0.42). This makes sense because the two profiles disagree on every input: genre, mood, energy and acoustic.
- **High-Energy Pop vs. Deep Intense Rock:** These overlap a lot (*Gym Hero*, *Sunrise City*, *Storm Runner* appear in both) because both want high energy and non-acoustic sound. The genre and mood decide who wins: pop puts *Sunrise City* first and rock puts *Storm Runner* first. *Gym Hero* is #2 in both, but for different reasons: for pop it matches the genre, and for rock it matches the "intense" mood.
- **Chill Lofi vs. Deep Intense Rock:** These are complete opposites, with no songs in common. Lofi's list stays under energy 0.45 and rock's stays above 0.75. This confirms the system clearly separates "intense rock" from "chill lofi".
- **Deep Intense Rock vs. Acoustic Metalhead:** Both want very high energy, but the metalhead's #1 is *Iron Tempest* (the only metal song) instead of *Storm Runner*. Their "likes acoustic" setting pulled upbeat folk (*Campfire Anthem*) into 2nd place. That makes sense: it's the only high-energy song that's also acoustic.
- **Chill Lofi vs. Sad but Hyped:** Both like acoustic music, but Sad but Hyped's list starts with the two folk songs and then switches to loud rock and pop (picked for energy 0.9), while lofi stays quiet throughout. The first two picks follow the labels; spots 3–5 follow the energy number.
- **Ghost Genre vs. Dead Center:** Both effectively have no labels that match, so both lists are ranked mostly by energy. Ghost Genre (energy 0.70, non-acoustic) gets upbeat electronic songs, and Dead Center (0.50) gets mid-tempo R&B, country and lofi. The scores are low and bunched together (all under 1.5), which shows the system has no strong opinion. It should probably say so.

**Weight experiment:** see "Experiments You Tried" in the README. Halving genre and doubling energy moved *Rooftop Lights* above *Gym Hero* for High-Energy Pop, but it did not fix the "Sad but Hyped" result.

**Full terminal output** (`python -m src.main`, original weights):

<details>
<summary>High-Energy Pop</summary>

```
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
```

</details>

<details>
<summary>Chill Lofi</summary>

```
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

</details>

<details>
<summary>Deep Intense Rock</summary>

```
================================================================
Profile: Deep Intense Rock
  genre=rock, mood=intense, energy=0.9, likes_acoustic=False
================================================================
1. Storm Runner by Voltline  [rock/intense]
   Score: 4.94 / 5.00
     - genre match: rock (+2.0)
     - mood match: intense (+1.5)
     - energy 0.91 vs target 0.90 (+0.99)
     - non-acoustic fit (+0.45)
2. Gym Hero by Max Pulse  [pop/intense]
   Score: 2.94 / 5.00
     - mood match: intense (+1.5)
     - energy 0.93 vs target 0.90 (+0.97)
     - non-acoustic fit (+0.47)
3. Strobe Heart by Pulsewave  [edm/energetic]
   Score: 1.44 / 5.00
     - energy 0.95 vs target 0.90 (+0.95)
     - non-acoustic fit (+0.49)
4. Iron Tempest by Grave Signal  [metal/angry]
   Score: 1.42 / 5.00
     - energy 0.97 vs target 0.90 (+0.93)
     - non-acoustic fit (+0.48)
5. Sunrise City by Neon Echo  [pop/happy]
   Score: 1.33 / 5.00
     - energy 0.82 vs target 0.90 (+0.92)
     - non-acoustic fit (+0.41)
```

</details>

<details>
<summary>Sad but Hyped (conflict: sad mood, 0.9 energy)</summary>

```
================================================================
Profile: Sad but Hyped (conflict: sad mood, 0.9 energy)
  genre=folk, mood=sad, energy=0.9, likes_acoustic=True
================================================================
1. Paper Boats by Willow & Finch  [folk/sad]
   Score: 4.37 / 5.00
     - genre match: folk (+2.0)
     - mood match: sad (+1.5)
     - energy 0.30 vs target 0.90 (+0.40)
     - acoustic fit (+0.47)
2. Campfire Anthem by The Hollow Pines  [folk/uplifting]
   Score: 3.24 / 5.00
     - genre match: folk (+2.0)
     - energy 0.72 vs target 0.90 (+0.82)
     - acoustic fit (+0.42)
3. Storm Runner by Voltline  [rock/intense]
   Score: 1.04 / 5.00
     - energy 0.91 vs target 0.90 (+0.99)
     - acoustic fit (+0.05)
4. Rooftop Lights by Indigo Parade  [indie pop/happy]
   Score: 1.03 / 5.00
     - energy 0.76 vs target 0.90 (+0.86)
     - acoustic fit (+0.17)
5. Sunrise City by Neon Echo  [pop/happy]
   Score: 1.01 / 5.00
     - energy 0.82 vs target 0.90 (+0.92)
     - acoustic fit (+0.09)
```

</details>

<details>
<summary>Acoustic Metalhead (conflict: metal + loves acoustic)</summary>

```
================================================================
Profile: Acoustic Metalhead (conflict: metal + loves acoustic)
  genre=metal, mood=angry, energy=0.95, likes_acoustic=True
================================================================
1. Iron Tempest by Grave Signal  [metal/angry]
   Score: 4.50 / 5.00
     - genre match: metal (+2.0)
     - mood match: angry (+1.5)
     - energy 0.97 vs target 0.95 (+0.98)
     - acoustic fit (+0.01)
2. Campfire Anthem by The Hollow Pines  [folk/uplifting]
   Score: 1.20 / 5.00
     - energy 0.72 vs target 0.95 (+0.77)
     - acoustic fit (+0.42)
3. Storm Runner by Voltline  [rock/intense]
   Score: 1.01 / 5.00
     - energy 0.91 vs target 0.95 (+0.96)
     - acoustic fit (+0.05)
4. Strobe Heart by Pulsewave  [edm/energetic]
   Score: 1.01 / 5.00
     - energy 0.95 vs target 0.95 (+1.00)
     - acoustic fit (+0.01)
5. Gym Hero by Max Pulse  [pop/intense]
   Score: 1.01 / 5.00
     - energy 0.93 vs target 0.95 (+0.98)
     - acoustic fit (+0.03)
```

</details>

<details>
<summary>Ghost Genre (genre/mood not in catalog)</summary>

```
================================================================
Profile: Ghost Genre (genre/mood not in catalog)
  genre=k-pop, mood=euphoric, energy=0.7, likes_acoustic=False
================================================================
1. Concrete Crown by Block Theory  [hip-hop/confident]
   Score: 1.36 / 5.00
     - energy 0.78 vs target 0.70 (+0.92)
     - non-acoustic fit (+0.44)
2. Night Drive Loop by Neon Echo  [synthwave/moody]
   Score: 1.34 / 5.00
     - energy 0.75 vs target 0.70 (+0.95)
     - non-acoustic fit (+0.39)
3. Sunrise City by Neon Echo  [pop/happy]
   Score: 1.29 / 5.00
     - energy 0.82 vs target 0.70 (+0.88)
     - non-acoustic fit (+0.41)
4. Rooftop Lights by Indigo Parade  [indie pop/happy]
   Score: 1.26 / 5.00
     - energy 0.76 vs target 0.70 (+0.94)
     - non-acoustic fit (+0.33)
5. Gym Hero by Max Pulse  [pop/intense]
   Score: 1.24 / 5.00
     - energy 0.93 vs target 0.70 (+0.77)
     - non-acoustic fit (+0.47)
```

</details>

<details>
<summary>Dead Center (energy 0.5, no genre or mood)</summary>

```
================================================================
Profile: Dead Center (energy 0.5, no genre or mood)
  energy=0.5
================================================================
1. Velvet Hours by Amara Lane  [r&b/romantic]
   Score: 1.00 / 1.00
     - energy 0.50 vs target 0.50 (+1.00)
2. Dusty Backroads by Wade Hollis  [country/nostalgic]
   Score: 0.95 / 1.00
     - energy 0.55 vs target 0.50 (+0.95)
3. Midnight Coding by LoRoom  [lofi/chill]
   Score: 0.92 / 1.00
     - energy 0.42 vs target 0.50 (+0.92)
4. Focus Flow by LoRoom  [lofi/focused]
   Score: 0.90 / 1.00
     - energy 0.40 vs target 0.50 (+0.90)
5. Island Time by Sol Collective  [reggae/uplifting]
   Score: 0.90 / 1.00
     - energy 0.60 vs target 0.50 (+0.90)
```

</details>

---

## 8. Ideas for Improvement  

1. **Let energy push back against the labels.** Right now a perfect genre and mood match wins even if the energy is way off. I'd make the energy penalty grow faster for big gaps, or cap how much the labels can add when energy is far from the target. That would fix the "Sad but Hyped" result.
2. **Partial credit for similar labels.** "indie pop" should get some points for a "pop" fan, and "relaxed" should get some for "chill". A small table of related genres and moods would do it. That would also stop *Gym Hero* from beating *Rooftop Lights* for happy-pop fans.
3. **Add valence and a variety rule.** Scoring valence would let the system tell "calm" from "sad". A rule like "no more than 2 songs from the same artist or genre in the top 5" would make lists less repetitive. It should also warn the user when nothing actually matched, like in the Ghost Genre test.

---

## 9. Personal Reflection  

**Biggest learning moment.** The "Sad but Hyped" test. I made a profile that wanted sad songs at 0.9 energy, and it gave me *Paper Boats*, the quietest folk song in the list (energy 0.30). That's when it clicked that the weights I picked are basically the system's opinions. Later I tried the energy-focused mode and it moved a high-energy song to #1, but then it mostly ignored "sad." That taught me the real problem was the data: there's no sad, high-energy song in my catalog, so no weight setting could find one.

**How AI helped, and when I had to double-check.** I used an AI coding assistant (Claude Code) as a helper throughout the project. I used it to analyze my CSV, brainstorm scoring rules and weights, help write and debug code, and draft documentation. It also pointed out something I wouldn't have noticed: energy, tempo and acousticness were almost the same signal in my data. But it wasn't always right, so I treated its answers as suggestions to check. One early note said genre was worth more than mood and energy combined, and that's just wrong (1.5 + 1.0 = 2.5, which is more than 2.0). A draft also miscounted how many lists *Gym Hero* showed up in. I only caught those by running the code and checking the real numbers myself.

**What surprised me.** How real a little bit of math feels. Adding up four numbers and sorting gave me lists that honestly looked like something Spotify would show me. Printing the reasons made it feel even smarter. But it can also look confident when it has no idea. In the Ghost Genre test (k-pop, which isn't in the catalog), it still gave me a top 5 like everything was fine.

**What I'd try next.** I'd make up listening history for a few fake users and try collaborative filtering ("people like you also liked..."), then mix it with my content-based scores like real apps do. I'd also give partial credit for close labels, so "indie pop" counts a little for a pop fan, and see if that finally stops *Gym Hero* from beating *Rooftop Lights* for happy pop.
